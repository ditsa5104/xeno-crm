# Xeno — AI-Native Mini CRM

Two-service AI-native CRM for consumer brands. Marketers can segment customers, draft personalized campaigns with an AI copilot, dispatch messages over a simulated multi-channel gateway, and track delivery + revenue end-to-end in real time.

## Stack

- **CRM** — Django 4.2 + DRF + Channels 4 + Celery 5 + PostgreSQL 16 + Redis
- **Channel stub** — FastAPI async simulator with HMAC-signed callbacks
- **Frontend** — React 18 + Vite + TanStack Query + Recharts + Tailwind
- **AI** — OpenRouter via the `openai` SDK (model: `deepseek/deepseek-v3.2` by default)

## Product point of view

The brief is deliberately open. The bet this product makes: **a marketer should be able to run the entire reach-a-shopper loop — segment → draft → send → measure — from one place, with an AI copilot that can both *answer* (chat) and *act* (agent).** AI is woven into the three decisions the brief calls out — *who to talk to, what to say, which channel* — rather than bolted on as a sidebar gimmick:

- **Who** → natural-language segment builder turns "Mumbai high-spenders who lapsed 60 days" into a live filter tree; lookalike expansion grows a seed audience.
- **What** → the copilot drafts channel-appropriate message variants with merge tags.
- **Which channel / act** → the agent reuses or creates a segment, drafts copy, assembles a draft campaign, and (on explicit confirmation) launches it end-to-end.

**What I deliberately did NOT build** (scoping is part of the brief): no real provider integrations (the channel is stubbed by design), no auth beyond token auth, no multi-tenancy/org model, no visual drag-drop journey builder, no billing. These are the right cuts for a take-home: they add surface area without demonstrating anything the evaluation criteria reward.

## Architecture

```
                    ┌─────────────────────────────────────────────┐
   Browser  ◄─────► │  Frontend (React + Vite SPA)                 │
                    │  REST + WebSocket live feed                  │
                    └───────────────┬─────────────────────────────┘
                          REST/WS   │   Token auth
                    ┌───────────────▼─────────────────────────────┐
                    │  CRM (Django ASGI · daphne)                  │
                    │  DRF API · Channels WS · Copilot agent       │
                    │  ┌─────────┬──────────┬─────────┬─────────┐  │
                    │  │customers│ segments │campaigns│analytics│  │
                    │  └─────────┴──────────┴─────────┴─────────┘  │
                    └──┬──────────┬───────────────┬────────────┬───┘
            dispatch   │          │ Celery        │ OpenRouter │ broadcast
            POST /send │          │ (worker+beat) │ (AI)       │ (Redis layer)
                       ▼          ▼               ▼            ▼
        ┌──────────────────┐  ┌───────┐    ┌──────────┐  ┌──────────┐
        │  Channel stub    │  │ Redis │    │ DeepSeek │  │ Postgres │
        │  (FastAPI)       │  │broker/│    │ v3.2     │  │          │
        │  simulates       │  │cache/ │    └──────────┘  └──────────┘
        │  lifecycle       │  │ chans │
        └────────┬─────────┘  └───────┘
                 │ async HMAC-signed callbacks
                 │ (delivered/failed/opened/read/clicked)
                 ▼
        POST /api/v1/webhooks/channel-event/  ──► state machine ──► stats + WS
```

**The callback loop is the heart of it.** Dispatch POSTs each communication to the stub; the stub simulates the full lifecycle and fires async, HMAC-signed callbacks back to the CRM receipt API. The CRM verifies the signature, deduplicates, applies an order-independent state machine, updates stats via `F()` expressions, and broadcasts the event over WebSocket to the live feed.

## Quick start

```bash
cp .env.example .env
# Fill in OPENROUTER_API_KEY in .env

docker compose up --build
```

Wait until all services are up, then in a second terminal:

```bash
docker compose exec crm python manage.py seed_demo
docker compose exec crm python manage.py drf_create_token admin || true
```

Open:

- Frontend → http://localhost:5173
- Django admin → http://localhost:8000/admin (admin / admin123)
- API docs (Swagger UI) → http://localhost:8000/api/docs/
- API docs (ReDoc) → http://localhost:8000/api/redoc/
- OpenAPI schema → http://localhost:8000/api/schema/
- Channel stub health → http://localhost:8001/health
- Channel stub metrics → http://localhost:8001/metrics

To use Copilot/segment-AI features, paste an API token (created via `drf_create_token` or admin) into the sidebar input.

## Services

| Service | Port | Purpose |
|---|---|---|
| `crm` | 8000 | Django ASGI (HTTP + WS) via daphne |
| `worker` | — | Celery worker (queues: default, campaigns, scoring) |
| `beat` | — | Celery beat scheduler |
| `channel_stub` | 8001 | FastAPI message-delivery simulator |
| `frontend` | 5173 | Vite dev server |
| `db` | 5432 | PostgreSQL |
| `redis` | 6379 | Redis (broker + cache + channels layer) |

## Key features

- **RFM scoring** with quintile ranks → tier labels (Champions, At Risk, Lost, …)
- **Per-customer churn risk**, predicted send-hour, LTV estimate
- **Filter DSL** with recursive AND/OR groups; `SegmentEvaluator` → Django QuerySet
- **AI segment builder** — natural-language → filter tree via OpenRouter
- **Lookalike segments** via cosine similarity on RFM/spend feature vectors
- **A/B test auto-winner** — Celery beat task picks variant by click rate
- **Multi-wave + smart retry** — failure-reason routing with exponential backoff
- **Revenue attribution** — links orders within 7 days post-click to the campaign
- **Copilot** — chat + agent modes with 16 tools spanning live data queries (customers, segments, campaigns, analytics, cohorts), AI drafting, and actions (create segment/campaign drafts, launch campaigns)
- **Live event feed** — WebSocket broadcasts every webhook event
- **Customer 360** — full timeline of orders + campaigns

## Webhook security

The CRM and channel stub share a secret (`CHANNEL_STUB_SECRET`). The stub HMAC-SHA256 signs every callback (`X-Xeno-Signature`); the CRM rejects any callback that fails verification. Each `(message_id, event_type)` is also deduplicated via Redis (24h TTL) and `CommunicationEvent.unique_together` so duplicate callbacks never inflate stats.

## Filter DSL example

```json
{
  "operator": "AND",
  "conditions": [
    {"field": "total_spend", "op": "gte", "value": 5000},
    {"field": "last_order_at", "op": "days_ago_lte", "value": 90},
    {
      "operator": "OR",
      "conditions": [
        {"field": "rfm_recency_score", "op": "gte", "value": 4},
        {"field": "tags", "op": "contains", "value": "vip"}
      ]
    }
  ]
}
```

Supported fields/ops are documented in `crm/apps/segments/evaluator.py`.

## Tests

```bash
docker compose exec crm pytest
```

Tests cover SegmentEvaluator, RFM scoring, webhook HMAC, state machine, personaliser, and Copilot tools.

## Design decisions & tradeoffs

The brief explicitly asks for explicit tradeoffs — "I'd do X at scale but did Y for this scope." The consequential ones:

- **Out-of-order callbacks (the core system-design call).** Channel callbacks are async with independent delays, so they arrive reordered. Rather than a strict linear state machine (which silently drops a `clicked` that beats `opened`), engagement is modeled as a **monotonic funnel**: every event's timestamp is recorded regardless of arrival order, status is the furthest stage reached, duplicates are suppressed, and a stale `failed` never overrides a real success. *At scale* I'd move stat aggregation out of the request path into a stream processor; *here* `F()`-expression updates inside `select_for_update()` are correct and simple.

- **Exactly-once stat counting.** Two layers: a Redis dedup key (`webhook:{id}:{event}`, 24h TTL) drops repeats at the edge, and `CommunicationEvent.unique_together(log, event_type)` is the durable guard. The Redis layer is an optimization; the DB constraint is the source of truth, so a Redis flush can't corrupt counts.

- **Dispatch is synchronous within one Celery task.** Fine for demo-scale audiences; *at scale* I'd fan out per-recipient tasks or batch into a queue with rate-limiting. The dispatcher already re-checks campaign status mid-send so a pause takes effect.

- **Revenue attribution is last-touch within a 7-day window**, run as a nightly batch. Simple and explainable; *at scale* I'd support configurable windows and multi-touch models, computed incrementally rather than re-scanning.

- **AI failures fail loud, not silent.** The NL→segment builder raises `SegmenterError` instead of returning an empty filter (which the evaluator would read as "match everyone" — a dangerous default for an audience). The copilot loop, on exhausting its tool budget, makes one final tool-free call to synthesize an answer instead of dead-ending.

- **Free-tier deployment shapes.** On Render's 512MB free dyno the worker runs single-concurrency with embedded beat (`-B`) to avoid OOM; *at scale* worker/beat are separate, horizontally scaled processes (as the local `docker-compose` already runs them).

- **Postgres-specific data model.** `Customer.tags` uses `ArrayField` and segment evaluation uses `__overlap`/`__contains`; this commits to Postgres (no sqlite fallback) in exchange for clean array querying.

## Project conventions

- All models inherit from `apps.core.models.TimestampedModel`; UUID PKs.
- Campaign stat fields are only updated via `F()` expressions.
- Webhook ingestion: `transaction.atomic()` + `select_for_update()` + Redis dedup.
- AI calls wrapped in `try/except` for `openai.APIError` / `RateLimitError`.
- Model name lives in `apps/core/ai_client.py`; everywhere else uses `settings.OPENROUTER_MODEL`.
- Production shortcuts annotated with `# TRADEOFF:` comments.

## Layout

```
xeno/
├── crm/                      Django service
│   ├── config/               Settings, URL conf, ASGI, Celery
│   └── apps/
│       ├── core/             Base model, AI client, pagination, HMAC utils
│       ├── customers/        Customer + Order + RFM + seed
│       ├── segments/         Segment + DSL evaluator + AI segmenter
│       ├── campaigns/        Campaign + dispatch + personaliser + A/B
│       ├── analytics/        Aggregators + WebSocket consumer + attribution
│       ├── copilot/          Tools, agent loop, chat/agent endpoints
│       └── webhooks/         HMAC + dedup + state machine + smart retry
├── channel_stub/             FastAPI simulator
└── frontend/                 React + Vite SPA
```
