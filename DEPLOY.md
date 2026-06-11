# Deploying Xeno

Frontend deploys to **Vercel** (static SPA). Everything else (CRM web, Celery worker, Celery beat, channel stub, Postgres, Redis) deploys to **Render** via the included Blueprint.

## 1 — Render (backend)

1. Push the repo to GitHub.
2. Render dashboard → **New → Blueprint** → select the repo. Render reads `render.yaml`.
3. After the first apply, set these `sync: false` env vars in the dashboard:
   - **xeno-crm** → `OPENROUTER_API_KEY`, `SITE_URL` (= `https://xeno-crm.onrender.com`), `CORS_ALLOWED_ORIGINS` (= your Vercel URL once known).
   - **xeno-worker** → `OPENROUTER_API_KEY`, `SITE_URL`.
   - **xeno-channel-stub** → `CRM_WEBHOOK_URL` (= `https://xeno-crm.onrender.com/api/v1/webhooks/channel-event/`).
4. Trigger a redeploy of `xeno-crm` so migrations run with the final env. The Blueprint runs `migrate` and `collectstatic` in the build step.
5. Seed demo data once everything is up:
   ```
   render exec xeno-crm -- python manage.py seed_demo
   ```
   Or open the **Shell** tab on the `xeno-crm` service and run it there.

The `xeno-channel-stub` is provisioned as a Render **Private Service** (`pserv`) — it has no public URL and is only reachable from the CRM via the internal `host:port` injected by `fromService.property: hostport`.

`SECRET_KEY` and `CHANNEL_STUB_SECRET` are generated once on the `xeno-crm` service and shared with the worker, beat, and stub via `fromService.envVarKey`, so the HMAC handshake works across services without manual copying.

## 2 — Vercel (frontend)

1. Vercel dashboard → **Add New → Project** → pick the same repo, set the **Root Directory** to `frontend/`. Vercel reads `frontend/vercel.json` (Vite framework preset, SPA rewrites).
2. Set one env var:
   - `VITE_API_URL` = `https://xeno-crm.onrender.com`
3. Deploy. Copy the resulting URL (e.g. `https://xeno.vercel.app`).
4. Back on Render, update `xeno-crm` → `CORS_ALLOWED_ORIGINS` to the Vercel URL and redeploy.

## Plan notes

- The Blueprint uses Render's free plan everywhere. Free web services sleep after 15 minutes of inactivity — first request after sleep takes ~30s. Upgrade `xeno-crm` and `xeno-worker` to a paid plan for production.
- Free Postgres on Render expires after 90 days — back up before then or move to a paid instance.
- WebSockets work on Render's free plan; the frontend connects to `wss://xeno-crm.onrender.com/ws/events/` automatically (the `wsUrl()` helper in `frontend/src/api/client.js` derives the scheme from `VITE_API_URL`).

## Environment variable map

| Variable | crm web | worker | beat | channel_stub | Vercel |
|---|---|---|---|---|---|
| `DATABASE_URL` | ✓ | ✓ | ✓ | | |
| `REDIS_URL` | ✓ | ✓ | ✓ | | |
| `SECRET_KEY` | ✓ | ✓ | ✓ | | |
| `CHANNEL_STUB_SECRET` | ✓ | ✓ | | ✓ | |
| `CHANNEL_STUB_URL` | ✓ | ✓ | | | |
| `CRM_WEBHOOK_URL` | | | | ✓ | |
| `OPENROUTER_API_KEY` | ✓ | ✓ | | | |
| `SITE_URL` | ✓ | ✓ | | | |
| `CORS_ALLOWED_ORIGINS` | ✓ | | | | |
| `VITE_API_URL` | | | | | ✓ |
