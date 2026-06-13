# Deploying Xeno

Frontend deploys to **Vercel** (static SPA). Everything else deploys to **Render** via the included Blueprint (`render.yaml`). To fit Render's free tier, the CRM web service, Celery worker, and Celery beat all run inside a single web dyno (see `crm/start.sh`), and the channel stub runs as its own public web service.

## 1 — Render (backend)

1. Push the repo to GitHub.
2. Render dashboard → **New → Blueprint** → select the repo. Render reads `render.yaml`.
3. After the first apply, set these `sync: false` env vars in the dashboard:
   - **xeno-crm** → `OPENROUTER_API_KEY`, `SITE_URL` (= `https://xeno-crm-xrut.onrender.com`), `CORS_ALLOWED_ORIGINS` (= your Vercel URL once known).
   - **xeno-channel-stub** → `CRM_WEBHOOK_URL` (= `https://xeno-crm-xrut.onrender.com/api/v1/webhooks/channel-event/`).
4. Trigger a redeploy of `xeno-crm` so migrations run with the final env. The Blueprint runs `migrate`, `seed_demo`, and `collectstatic` in the build step, so demo data is populated automatically on first deploy (the seed is idempotent — it no-ops if customers already exist).

The `xeno-channel-stub` runs as a public Render web service. The CRM reaches it via `CHANNEL_STUB_URL` (injected from the stub service host), and the stub calls back to the CRM via `CRM_WEBHOOK_URL`.

## 2 — Vercel (frontend)

1. Vercel dashboard → **Add New → Project** → pick the same repo, set the **Root Directory** to `frontend/`. Vercel reads `frontend/vercel.json` (Vite framework preset, SPA rewrites).
2. Set one env var:
   - `VITE_API_URL` = `https://xeno-crm.onrender.com`
3. Deploy. Copy the resulting URL (e.g. `https://xeno.vercel.app`).
4. Back on Render, update `xeno-crm` → `CORS_ALLOWED_ORIGINS` to the Vercel URL and redeploy.

## Plan notes

- The Blueprint uses Render's free plan everywhere. Free web services sleep after 15 minutes of inactivity — first request after sleep takes ~30s. Upgrade `xeno-crm` and `xeno-worker` to a paid plan for production.
- Free Postgres on Render expires after 90 days — back up before then or move to a paid instance.
- WebSockets work on Render's free plan; the frontend connects to `wss://xeno-crm-xrut.onrender.com/ws/events/` automatically (the `wsUrl()` helper in `frontend/src/api/client.js` derives the scheme from `VITE_API_URL`).

## Environment variable map

| Variable | crm web (worker+beat embedded) | channel_stub | Vercel |
|---|---|---|---|
| `DATABASE_URL` | ✓ | | |
| `REDIS_URL` | ✓ | | |
| `SECRET_KEY` | ✓ | | |
| `CHANNEL_STUB_SECRET` | ✓ | ✓ | |
| `CHANNEL_STUB_URL` | ✓ | | |
| `CRM_WEBHOOK_URL` | | ✓ | |
| `OPENROUTER_API_KEY` | ✓ | | |
| `OPENROUTER_MODEL` | ✓ | | |
| `SITE_URL` | ✓ | | |
| `CORS_ALLOWED_ORIGINS` | ✓ | | |
| `VITE_API_URL` | | | ✓ |
