# Running Maven Technosoft Enterprise Emailer

This guide explains how to run the full stack locally: the **Django backend** (REST API + AI streaming + email dispatch) and the **React + Vite frontend**.

```
project 1/
├── backend/    Django 6 + Django Ninja API   → http://localhost:8000
└── frontend/   React + Vite SPA              → http://localhost:5173
```

The frontend dev server proxies `/api` and `/ai` to the backend at `:8000`, so you run both at once during development.

---

## 1. Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| **Python** | 3.11+ (tested on 3.13) | Backend runtime |
| **Node.js** | 18+ (tested on 20) | Frontend tooling |
| **PostgreSQL** | 14+ | Primary database |
| **Git** | any | — |

Confirm they're installed:

```powershell
python --version
node --version
psql --version
```

---

## 2. Backend setup (`backend/`)

### 2.1 Create and activate a virtual environment

```powershell
cd "E:\career247\New folder (2)\project 1\backend"
python -m venv .venv
.\.venv\Scripts\Activate.ps1        # PowerShell
# .venv\Scripts\activate.bat        # cmd.exe
# source .venv/bin/activate         # macOS/Linux
```

> If PowerShell blocks the activation script, run once:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

### 2.2 Install dependencies

```powershell
pip install -r requirements.txt
```

### 2.3 Configure environment variables

The backend reads `backend/.env`. It already exists with working dev defaults:

```env
SECRET_KEY=dev-only-secret-key-change-in-prod
DB_NAME=Email-CRM
DB_USER=postgres
DB_PASSWORD=admin@123
DB_HOST=127.0.0.1
DB_PORT=5432
GOOGLE_CLIENT_ID=your-google-client-id        # optional — only for Google login
GOOGLE_CLIENT_SECRET=your-google-client-secret # optional
OPENAI_API_KEY=your-openai-key                 # optional — set per-org in Settings instead
FERNET_KEY=RqgUkzXLpMxb46dGLkGJZ6jRv6OeD4pxYF1BI3RFfJQ=
```

Edit `DB_USER` / `DB_PASSWORD` if your PostgreSQL credentials differ.

- **Google login** is optional. Without real Google credentials, use the email/password form.
- **OpenAI key** is best set per-organization in the app's **Settings → OpenAI API Key** page (stored encrypted). The AI features need a valid key to return results.

### 2.4 Create the PostgreSQL database

The database name `Email-CRM` contains a hyphen, so it must be quoted.

```powershell
# Option A — createdb CLI
createdb -U postgres "Email-CRM"

# Option B — inside psql
psql -U postgres -c "CREATE DATABASE \"Email-CRM\";"
```

### 2.5 Apply migrations

```powershell
python manage.py migrate
```

### 2.6 Seed the 6 system email templates

```powershell
python manage.py seed_templates
```

### 2.7 Create an admin user (for Django admin + first login)

```powershell
python manage.py createsuperuser
```

> **You usually don't need this for normal use.** The app has a self-serve
> **Sign up** page (`/signup`) that creates your user, organization, and
> membership in one step. `createsuperuser` is only needed for Django admin
> access. New users can register straight from the frontend.

### 2.8 Run the backend server

```powershell
python manage.py runserver
```

Backend is now live:

- API root & docs (Swagger): **http://localhost:8000/api/docs**
- Django admin: **http://localhost:8000/admin/**

---

## 3. Background worker — Django-Q (`backend/`, second terminal)

Sending a campaign (**Send Now**) and **scheduled** sends are queued through Django-Q2. The web server enqueues the job, but a separate **worker process** actually sends the emails.

Open a **second terminal**, activate the same venv, and run:

```powershell
cd "E:\career247\New folder (2)\project 1\backend"
.\.venv\Scripts\Activate.ps1
python manage.py qcluster
```

Leave it running alongside the dev server.

> You can skip this if you're only browsing the UI / editing templates / using AI features. It's required only for actually dispatching campaign emails. SMTP must also be configured in **Settings → SMTP Setup** for sends to succeed.

---

## 4. Frontend setup (`frontend/`, third terminal)

### 4.1 Install dependencies

```powershell
cd "E:\career247\New folder (2)\project 1\frontend"
npm install
```

### 4.2 (Optional) Google OAuth client ID

To use the "Continue with Google" button, create `frontend/.env` with:

```env
VITE_GOOGLE_CLIENT_ID=your-google-client-id
```

Use the same client ID as the backend's `GOOGLE_CLIENT_ID`. Skip this to use email/password login only.

### 4.3 Run the dev server

```powershell
npm run dev
```

Open **http://localhost:5173** and log in with the superuser credentials from step 2.7.

---

## 5. Typical local workflow — terminals at a glance

| Terminal | Directory | Command | Purpose |
|----------|-----------|---------|---------|
| 1 | `backend/` | `python manage.py runserver` | API + admin (`:8000`) |
| 2 | `backend/` | `python manage.py qcluster` | Email send/scheduler worker |
| 3 | `frontend/` | `npm run dev` | UI (`:5173`) |

Minimum to see the app: terminals **1** and **3**. Add **2** when sending campaigns.

---

## 6. Tests

**Backend** (41 tests):

```powershell
cd "E:\career247\New folder (2)\project 1\backend"
python -m pytest
```

**Frontend** (type-check + production build):

```powershell
cd "E:\career247\New folder (2)\project 1\frontend"
npm run build
```

---

## 7. Production build (frontend)

```powershell
cd "E:\career247\New folder (2)\project 1\frontend"
npm run build      # outputs to dist/
npm run preview    # serves the built dist/ locally to verify
```

For production, serve `dist/` from a static host (or Django/Nginx) and point it at the backend. In production you would set `changeOrigin` proxying or configure CORS and absolute API URLs accordingly.

---

## 8. Troubleshooting

| Symptom | Fix |
|---------|-----|
| `ModuleNotFoundError` on backend start | Activate the venv, then `pip install -r requirements.txt`. |
| `FATAL: database "Email-CRM" does not exist` | Run step 2.4 (remember the quotes around the hyphenated name). |
| `psycopg.OperationalError: password authentication failed` | Fix `DB_USER` / `DB_PASSWORD` in `backend/.env`. |
| Login works but dashboard is empty / "no org" | Use the **Sign up** page to provision an org, or add an Organization for the user in `/admin/`. |
| **Send Now** stays "queued" forever | Start the `qcluster` worker (section 3). |
| Campaign send fails | Configure SMTP in **Settings → SMTP Setup** and click **Test**. |
| AI panel returns an error | Set a valid OpenAI key in **Settings → OpenAI API Key**. |
| Frontend `/api` calls 404 / CORS | Ensure the backend runs on `:8000`; the Vite proxy expects that port. |
| Google button does nothing | Set `VITE_GOOGLE_CLIENT_ID` (frontend) and `GOOGLE_CLIENT_ID` (backend), or use email/password. |
| PowerShell won't run `Activate.ps1` | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` (once). |

---

## 9. Key URLs

| URL | What |
|-----|------|
| http://localhost:5173 | Frontend app |
| http://localhost:8000/api/docs | Interactive API docs (Swagger UI) |
| http://localhost:8000/admin/ | Django admin |
