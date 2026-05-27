# Testing Guide — Maven Technosoft Enterprise Emailer

This project has three test layers:

| Layer | Tool | Location | What it covers |
|-------|------|----------|----------------|
| **Backend unit/API** | pytest + pytest-django | `backend/apps/**/tests/` | Models, API endpoints, services, AI agents, management commands |
| **Frontend build/type** | `tsc` + Vite | `frontend/` | TypeScript correctness, production bundle |
| **End-to-end (E2E)** | Playwright | `frontend/e2e/` | Real browser flows across the running frontend + backend |

---

## 1. Backend tests (pytest)

**53 tests** covering auth, organizations, templates, campaigns, recipients, SMTP, AI agents, SSE views, and the seed command.

```powershell
cd "E:\career247\New folder (2)\project 1\backend"
python -m pytest            # full suite
python -m pytest -q         # quiet
python -m pytest apps/campaigns/tests/test_api.py -v   # one file
python -m pytest -k recipients                          # by keyword
```

- Uses a throwaway test database (pytest-django creates/destroys it). Your `Email-CRM` dev data is untouched.
- No external services required — AI/LLM calls and the task queue are mocked.

---

## 2. Frontend build / type check

There are no frontend unit tests; correctness is enforced by the TypeScript compiler and the production build.

```powershell
cd "E:\career247\New folder (2)\project 1\frontend"
npm run build      # tsc -b && vite build — fails on any type error
```

A chunk-size warning about GrapesJS is expected and harmless.

---

## 3. End-to-end tests (Playwright)

E2E drives a real Chromium browser against a **live frontend + backend**. Playwright starts both servers automatically on dedicated test ports, so it won't clash with a dev stack you're already running.

### One-time setup

Already done in this repo (`@playwright/test` is a dev dependency). If browsers are missing on a new machine:

```powershell
cd "E:\career247\New folder (2)\project 1\frontend"
npx playwright install chromium
```

### Prerequisites

E2E runs against the **real PostgreSQL `Email-CRM` database** (it's a full-stack browser test, not an isolated unit test). Before running:

1. The database exists and migrations are applied (see `RUNNING.md` §2.4–2.5).
2. `python` on your PATH has the backend dependencies installed. Run E2E from a shell where `python -c "import django"` works (the global interpreter used for pytest is fine). **Do not** run it from a venv that lacks the requirements.
3. Ports **8000** (test backend) and **5174** (test frontend) are free.

> Each test creates its own account with a timestamped email (e.g. `e2e-1716740000-1234@example.com`), so re-runs never collide. These rows accumulate in the dev DB — see "Cleaning up" below.

### Run

```powershell
cd "E:\career247\New folder (2)\project 1\frontend"
npm run e2e            # headless, all specs
npm run e2e:headed     # watch it drive a real browser
npm run e2e:ui         # interactive Playwright UI mode
npm run e2e:report     # open the HTML report from the last run
```

Playwright boots the servers, waits for `http://127.0.0.1:8000/api/docs` and `http://localhost:5174`, runs the specs, then shuts the servers down.

### What E2E covers (22 tests)

| Spec | Scenarios |
|------|-----------|
| `auth.spec.ts` | Unauth redirect to `/login`; signup → dashboard; short-password rejected; login of existing user; wrong-password error; logout |
| `campaigns.spec.ts` | Empty state; create campaign from scratch; **send blocked with 0 recipients**; add recipients → send → status `SENDING`; **add recipients in the create wizard**; remove a recipient |
| `templates.spec.ts` | Library renders; create template → opens GrapesJS editor; category filter |
| `settings.spec.ts` | Org settings prefilled; rename org; navigate to SMTP; save SMTP config |
| `navigation-and-ai.spec.ts` | Sidebar navigation; AI panel opens with all four tabs; switch AI tabs |

### What E2E does **not** cover (needs external credentials)

These are intentionally excluded because they call third-party services. Test them manually:

- **Actual email delivery.** `Send Now` queues a job; a `python manage.py qcluster` worker plus a real SMTP config in **Settings → SMTP Setup** are required for messages to actually go out. E2E asserts the status transition to `SENDING`, not delivery.
- **AI generation output.** The AI panel opens and tabs switch, but clicking *Generate* needs a valid OpenAI key (set per-org in **Settings → OpenAI API Key**). Without one the SSE stream returns an error event. E2E verifies the panel/tabs render, not the generated text.
- **Google OAuth login.** Requires real Google client credentials; E2E uses email/password.

### Cleaning up E2E data

E2E writes real users/orgs to the dev DB. To wipe the accumulated test accounts:

```powershell
cd "E:\career247\New folder (2)\project 1\backend"
python manage.py shell -c "from apps.accounts.models import User; User.objects.filter(email__startswith='e2e-').delete()"
```

(Deleting the users cascades to their orgs/campaigns/recipients.)

---

## 4. Quick "everything" check

```powershell
# Backend
cd "E:\career247\New folder (2)\project 1\backend";  python -m pytest -q

# Frontend type/build
cd "E:\career247\New folder (2)\project 1\frontend"; npm run build

# E2E (boots its own servers)
cd "E:\career247\New folder (2)\project 1\frontend"; npm run e2e
```

All three green = the stack is healthy.

---

## 5. CI notes

- Set `CI=1` to make Playwright forbid `test.only`, retry once, and never reuse an externally-started server.
- The Playwright config reads `process.env.VITE_API_TARGET`, so CI can point the frontend at any backend host.
- For isolated CI runs, point the backend at a disposable database (e.g. a CI Postgres service) via `backend/.env` so test accounts don't accumulate.
