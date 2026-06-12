# Xeno — AI-Native Mini CRM

Two-service AI-native CRM for consumer brands. Marketers can segment customers, draft personalized campaigns with an AI copilot, dispatch messages over a simulated multi-channel gateway, and track delivery + revenue end-to-end in real time.

## Stack

- **CRM** — Django 4.2 + DRF + Channels 4 + Celery 5 + PostgreSQL 16 + Redis
- **Channel stub** — FastAPI async simulator with HMAC-signed callbacks
- **Frontend** — React 18 + Vite + TanStack Query + Recharts + Tailwind
- **AI** — OpenRouter via the `openai` SDK (model: `anthropic/claude-sonnet-4-5` by default)

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
- **Copilot** — chat + agent modes with 9 tools (live queries, drafts, summaries)
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

## Project conventions

- All models inherit from `apps.core.models.TimestampedModel`; UUID PKs.
- Campaign stat fields are only updated via `F()` expressions.
- Webhook ingestion: `transaction.atomic()` + `select_for_update()` + Redis dedup.
- AI calls wrapped in `try/except` for `openai.APIError` / `RateLimitError`.
- Model name lives in `apps/core/ai_client.py`; everywhere else uses `settings.OPENROUTER_MODEL`.
- All shortcuts annotated with `# TRADEOFF:` comments.

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
