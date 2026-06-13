# Walkthrough Video Script (~5–6 min)

A narration script for the submission video, following the structure suggested in the
brief. Times are targets, not hard limits. Speak to the *why*, not just the *what* —
the brief rewards thought clarity over feature tours.

Live URL: `https://xeno-crm-xrut.onrender.com` · Repo: `github.com/ditsa5104/xeno-crm`

---

## 1 · Product intro (~30s)

> "This is Xeno, an AI-native mini CRM for consumer brands. The problem I chose to
> solve: a marketer should be able to run the whole reach-a-shopper loop — figure out
> *who* to message, *what* to say, send it over a channel, and see *what happened* —
> from one place, with AI woven into each of those decisions rather than bolted on.
>
> My opinionated bet was to build a copilot that can both **answer** questions about
> the data (chat) and **act** on a goal end-to-end (agent), backed by a realistic
> two-service delivery loop. I deliberately skipped real provider integrations,
> multi-tenancy, and billing — they add surface area without showing anything the
> brief is testing."

## 2 · Functional demo (~90s)

Show it actually working, end to end. Suggested flow:

1. **Dashboard** — "Here's the brand's state: 200 seeded customers, the two demo
   campaigns, delivery and open rates, and a 30-day performance chart." (point at the
   metric cards + chart)
2. **Segments** — open "Skirt Buyers — Last 12 Months". "This segment was built from a
   behaviour filter — customers who bought a skirt in the last year. 60 customers."
3. **Copilot chat** — type *"show me top customers by spend"*. "It calls a real tool,
   queries the DB, and answers with a table — not a guess."
4. **Copilot agent** — give it a goal: *"re-engage skirt buyers with a 15% off offer on
   WhatsApp"*. "It reuses the existing segment, drafts message variants, and assembles a
   draft campaign. Nothing is sent until I confirm."
5. **Launch + live feed** — launch a campaign and switch to the dashboard live feed.
   "As the channel stub simulates delivery, callbacks stream in over WebSocket —
   delivered, opened, clicked — and the stats update in real time."

## 3 · Technical architecture (~60s)

Pull up the diagram in `README.md` (the Architecture section).

> "Two services. The CRM is Django — DRF for the API, Channels for WebSockets, Celery
> for async work. The channel stub is a separate FastAPI service that simulates the
> full delivery lifecycle.
>
> The interesting part is the **callback loop**. The CRM dispatches a communication to
> the stub's send API. The stub doesn't deliver anything — it simulates outcomes and
> fires asynchronous, HMAC-signed callbacks back into the CRM's receipt API:
> delivered, failed, opened, read, clicked. The CRM verifies each signature,
> deduplicates, and updates stats.
>
> The key system-design call: those callbacks arrive **out of order** because each has
> an independent delay. So instead of a strict linear state machine, I model
> engagement as a monotonic funnel — every event is recorded regardless of arrival
> order, and status is the furthest stage reached. A click that beats its own 'opened'
> callback is never lost."

## 4 · Code walkthrough (~60s)

Open two or three files and explain the shape:

- `crm/apps/webhooks/state_machine.py` — "The order-independent funnel. Notice it
  records timestamps and derives status, rather than gating on a transition table."
- `crm/apps/webhooks/views.py` — "Ingestion: signature check → Redis dedup →
  `select_for_update` → state machine → `F()` stat update → WebSocket broadcast.
  Exactly-once counting comes from the `CommunicationEvent` unique constraint."
- `crm/apps/copilot/tools.py` + `agent.py` — "16 tools the copilot can call. The agent
  loop runs tool rounds, and if it exhausts its budget it makes one final tool-free
  call so it always produces a real answer."

> "The code is organised by Django app — customers, segments, campaigns, analytics,
> copilot, webhooks — each owning its models, serializers, and logic."

## 5 · AI-native workflow (~60s)

> "I built this AI-native end to end. I used an agentic coding assistant to scaffold
> the apps, then directed it through tight review loops — I diffed every change, ran
> the build and tests, and pushed back when something was wrong. Two examples:
>
> - When I swapped the LLM to DeepSeek, the copilot started stalling with 'stopped
>   after maximum tool rounds'. I traced it to the agent reading tool calls off
>   `finish_reason` — DeepSeek attaches them differently — and fixed the detection plus
>   added a final-answer fallback.
> - When I diffed the project against this brief, the AI helped me see the real gap
>   wasn't a missing feature but the out-of-order callback handling — which maps
>   directly to the 'how you handle ordering' criterion.
>
> The point wasn't *using* AI — it was directing it, reviewing its output, and owning
> every decision it shipped."

## Closing (~10s)

> "A working deployed product is the baseline. Where I tried to stand out: a sharp
> product bet, a realistic callback loop with thought-through failure and ordering
> handling, and an AI copilot that genuinely acts. Thanks for watching."

---

### Recording tips
- Have the demo data seeded and the Render service warm (hit it once before recording —
  free tier sleeps after 15 min).
- Pre-open tabs: dashboard, segments, copilot, and the two code files.
- Keep the agent goal prompt short so the tool loop finishes on camera.
