# Xeno — AI-Native Mini CRM

See the original project spec for full details. Key conventions:

- All models inherit from `apps.core.models.TimestampedModel`. UUID primary keys.
- Campaign stat fields updated only via `F()` expressions.
- All webhook processing uses `transaction.atomic()` + `select_for_update()` on `CommunicationLog`.
- Webhook dedup via Redis key `webhook:{log_id}:{event_type}` (TTL=24h).
- AI calls wrapped in `try/except` for `openai.APIError`, `openai.RateLimitError`.
- Celery tasks use `@shared_task(bind=True, max_retries=3)`.
- ORM only — no raw SQL.
- All AI uses OpenRouter via the `openai` SDK with `base_url=https://openrouter.ai/api/v1`.
- Model name only in `apps/core/ai_client.py`; everywhere else uses `settings.OPENROUTER_MODEL`.
- OpenRouter requires `HTTP-Referer` and `X-Title` headers.
- Production shortcuts annotated with `# TRADEOFF: [what] — at scale, [better]`.

Two services, run together via docker-compose:
- `crm/` — Django + DRF + Channels + Celery
- `channel_stub/` — FastAPI message-delivery simulator
