# Maven Technosoft — Enterprise Emailer Creation Tool
## Design Specification
**Date:** 2026-05-25  
**Status:** Approved  
**Phase:** 1 of 2

---

## 1. Project Overview

An enterprise-grade email campaign creation and sending platform for Maven Technosoft. Starts as an internal tool for marketing, sales, and CRM teams; architected as multi-tenant SaaS from day one so it can be licensed to enterprise clients in Phase 2.

**Company positioning:** Maven Technosoft is a domain-driven IT solutions company specialising in Application Development, Cloud Computing, Big Data & Analytics, CMS, and Travel/Transportation/Hospitality/Logistics (TTHL) solutions.

---

## 2. Scope

### Phase 1 (This spec)
- Email Template Builder (GrapesJS drag-drop editor + MJML rendering)
- Campaign Management (create, draft, schedule, send)
- AI Features (subject lines, copy optimisation, spam check, CTA suggestions via LangGraph + OpenAI)
- Email Sending (generic SMTP)
- Authentication (JWT + Google OAuth)
- Organisation management (django-organizations)
- User roles (admin / editor / viewer)

### Phase 2 (Out of scope)
- Analytics Dashboard (open rates, CTR, bounce)
- Audience / Contact Management (segmentation, import, lists)
- SaaS org signup flow

---

## 3. Technology Stack

| Layer | Technology | Version / Notes |
|-------|-----------|-----------------|
| Backend framework | Django | >= 6.0 |
| API layer | Django Ninja | Async REST, auto OpenAPI at `/api/docs` |
| Auth | django-allauth + JWT | Google OAuth only (no GitHub) |
| Multi-tenancy | django-organizations | Extended AbstractOrganization |
| Task queue | Django-Q2 | ORM broker — no Redis required |
| AI orchestration | LangGraph | Provider-agnostic agent graphs |
| AI model | OpenAI GPT-4o | Per-org API key stored on Organization |
| AI streaming | Django async SSE | `StreamingHttpResponse`, `text/event-stream` |
| Email rendering | MJML | GrapesJS → MJML → cross-client HTML |
| Email sending | Generic SMTP | `smtplib` / Django email backend |
| Password encryption | django-fernet-fields | SMTP password + OpenAI key at rest |
| Database | PostgreSQL | JSONB for template blocks, ArrayField for tags |
| Frontend framework | React + Vite | TypeScript |
| State (client) | Zustand | 3 stores: auth, editor, AI |
| State (server) | TanStack Query | API cache, background refetch |
| UI components | Tailwind CSS + shadcn/ui | |
| Email editor | GrapesJS | + grapesjs-mjml plugin (MJML-native canvas) |
| MJML compiler | mjml (Python pkg) | Wraps Node.js MJML, called server-side |

---

## 4. Architecture

### 4.1 Overview

```
Browser (React + Vite)
  ↕  REST + SSE (Server-Sent Events)
Django 6.0 + Django Ninja  ←→  LangGraph Agents  ←→  OpenAI GPT-4o
  ↕
Django-Q2 Workers (ORM broker)
  ↕  SMTP dispatch
PostgreSQL  ←→  SMTP Server (generic)
```

### 4.2 Key architectural decisions

- **No Redis.** Django-Q2 uses PostgreSQL as its message broker. SSE streaming uses Django's native async generator responses — no pub/sub needed.
- **Multi-tenant via django-organizations.** All emailer models carry an `organization` FK. An org-scoped middleware injects `request.auth.organization` so no view ever leaks cross-org data.
- **AI provider-agnostic.** Every LangGraph agent accepts a `BaseChatModel`. Swapping OpenAI for Anthropic or Gemini is a one-line config change. Per-org `openai_api_key` on the `Organization` model enables SaaS billing isolation.
- **GrapesJS state as JSONB.** The full editor canvas (`gjs_components`, `gjs_styles`) is stored in PostgreSQL JSONB columns — no file system dependency, no S3 needed for Phase 1.

---

## 5. Database Schema

### 5.1 django-organizations models (extended)

**Organization** (extends `AbstractOrganization`)
- Built-in: `name`, `slug` (unique), `is_active`
- Extensions: `logo_url TEXT`, `brand_colors JSONB`, `plan VARCHAR(20)` ['internal','saas'], `openai_api_key TEXT` (encrypted)

**OrganizationUser** (extends `AbstractOrganizationUser`)
- Built-in: `organization FK`, `user FK`, `is_admin BOOLEAN`
- Extensions: `role VARCHAR(20)` ['admin','editor','viewer'], `avatar_url TEXT`, `joined_at TIMESTAMPTZ`

**OrganizationOwner** (extends `AbstractOrganizationOwner`)
- No extensions needed — tracks primary owner per org

### 5.2 Custom emailer models

**EmailTemplate**
```
id              UUID PK
organization    FK → Organization
name            VARCHAR(200)
category        VARCHAR(50)   # promo, newsletter, announcement, webinar, onboarding
thumbnail_url   TEXT
gjs_components  JSONB         # GrapesJS canvas state (round-trip editable)
gjs_styles      JSONB         # GrapesJS styles state
mjml_source     TEXT          # compiled MJML (cached)
html_output     TEXT          # final cross-client HTML (cached)
is_system       BOOLEAN       # True = built-in template, org cannot delete
created_by      FK → User
updated_at      TIMESTAMPTZ
```

**Campaign**
```
id              UUID PK
organization    FK → Organization
template        FK → EmailTemplate
name            VARCHAR(200)
tags            ArrayField(VARCHAR)
subject_line    VARCHAR(300)
preview_text    VARCHAR(200)
from_name       VARCHAR(100)
from_email      EmailField
reply_to        EmailField
status          VARCHAR(20)   # draft | scheduled | sending | sent | failed
scheduled_at    TIMESTAMPTZ (nullable)
sent_at         TIMESTAMPTZ (nullable)
created_by      FK → User
```

**CampaignRecipient**
```
id              UUID PK
campaign        FK → Campaign
email           EmailField
name            VARCHAR(200)
personalization JSONB         # {first_name, company_name, industry, designation}
status          VARCHAR(20)   # queued | sent | failed
sent_at         TIMESTAMPTZ (nullable)
error_message   TEXT (nullable)
```

**SMTPConfig** (OneToOne → Organization)
```
organization    OneToOne → Organization
host            VARCHAR(255)
port            INTEGER
username        VARCHAR(255)
password        TEXT          # encrypted via django-fernet-fields
use_tls         BOOLEAN
use_ssl         BOOLEAN
is_verified     BOOLEAN
```

**AIJob**
```
id              UUID PK
organization    FK → Organization
campaign        FK → Campaign (nullable)
job_type        VARCHAR(30)   # subject_lines | copy_optimize | spam_check | cta_suggest
status          VARCHAR(20)   # pending | running | done | failed
input_data      JSONB
output_data     JSONB (nullable, written on completion)
created_by      FK → User
completed_at    TIMESTAMPTZ (nullable)
```

---

## 6. API Structure

All routes: JWT-authenticated · Org-scoped middleware · Auto OpenAPI at `/api/docs`

### `/api/auth/`
| Method | Path | Description |
|--------|------|-------------|
| POST | `/token` | email+password → JWT pair |
| POST | `/token/refresh` | Refresh access token |
| POST | `/google` | Google OAuth code → JWT |
| POST | `/logout` | Blacklist refresh token |
| GET | `/me` | Current user + org info |

### `/api/orgs/`
| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | List user's organisations |
| GET | `/{slug}` | Org detail + brand settings |
| PATCH | `/{slug}` | Update name, logo, brand colours |
| GET | `/{slug}/users` | List members with roles |
| POST | `/{slug}/invite` | Invite user by email |
| DELETE | `/{slug}/users/{id}` | Remove member |

### `/api/templates/`
| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | List (filter: category, is_system) |
| POST | `/` | Create blank template |
| GET | `/{id}` | Get with full GrapesJS state |
| PATCH | `/{id}` | Save GrapesJS state |
| DELETE | `/{id}` | Delete (non-system only) |
| POST | `/{id}/compile` | GrapesJS → MJML → HTML |
| POST | `/{id}/duplicate` | Clone template |

### `/api/campaigns/`
| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | List (filter: status, tags) |
| POST | `/` | Create campaign |
| GET | `/{id}` | Campaign detail |
| PATCH | `/{id}` | Update draft |
| DELETE | `/{id}` | Delete draft only |
| POST | `/{id}/schedule` | Schedule via Django-Q2 |
| POST | `/{id}/send-now` | Immediate SMTP dispatch |
| POST | `/{id}/recipients` | Upload recipient CSV |
| GET | `/{id}/recipients` | List recipients + delivery status |

### `/api/ai/`
| Method | Path | Description |
|--------|------|-------------|
| POST | `/stream` | Start SSE stream (returns job_id) |
| GET | `/stream/{job_id}` | Reconnect to existing SSE stream |
| GET | `/jobs` | List AI job history for org |
| GET | `/jobs/{id}` | Get completed job output |

### `/api/settings/`
| Method | Path | Description |
|--------|------|-------------|
| GET | `/smtp` | Get SMTP config (password masked) |
| PUT | `/smtp` | Save SMTP credentials |
| POST | `/smtp/test` | Send test email via configured SMTP |
| PUT | `/ai-key` | Update org OpenAI API key |

---

## 7. Frontend Architecture

### 7.1 Directory structure

```
src/
├── app/
│   ├── router.tsx
│   └── queryClient.ts
├── features/
│   ├── auth/          # LoginPage, GoogleOAuthCallback, ProtectedRoute
│   ├── campaigns/     # CampaignList, CampaignDetail, CreateCampaign, ScheduleSend
│   ├── editor/        # GrapesJSEditor, SubjectLineBar, CTAPanel, MobilePreview
│   ├── templates/     # TemplateLibrary, TemplateCard, TemplatePreview
│   ├── ai/            # AIPanel, SubjectSuggestions, CopyOptimizer, SpamChecker, useSSEStream
│   └── settings/      # OrgSettings, SMTPSetup, UserManagement, BrandColors
├── components/
│   ├── ui/            # shadcn/ui primitives
│   └── shared/        # AppShell, Sidebar, TopBar, PageHeader
├── stores/            # Zustand stores
├── hooks/             # shared hooks
├── lib/               # api client (axios), utils, constants
└── types/             # TypeScript interfaces
```

### 7.2 Routes

| Path | Component | Access |
|------|-----------|--------|
| `/login` | LoginPage | Public |
| `/` | → redirect to `/campaigns` | Auth |
| `/campaigns` | CampaignList | Auth |
| `/campaigns/new` | CreateCampaign (wizard) | Auth: editor+ |
| `/campaigns/:id` | CampaignDetail | Auth |
| `/editor/:templateId` | GrapesJSEditor (full-screen) | Auth: editor+ |
| `/templates` | TemplateLibrary | Auth |
| `/templates/new` | NewTemplate | Auth: editor+ |
| `/settings` | OrgSettings | Auth: admin |
| `/settings/smtp` | SMTPSetup | Auth: admin |

### 7.3 State management

**Zustand stores (client-only UI state):**

| Store | State |
|-------|-------|
| `useAuthStore` | `currentUser`, `orgSlug`, `accessToken`, `logout()` |
| `useEditorStore` | `gjsData`, `isDirty`, `previewMode` (desktop\|mobile), `activeBlock` |
| `useAIStore` | `isStreaming`, `streamBuffer`, `suggestions[]`, `selectedJobType` |

**TanStack Query (server state, auto-cached):**
- `useCampaignsQuery`, `useCampaignMutation`
- `useTemplatesQuery`, `useTemplateMutation`
- `useOrgQuery`, `useSmtpMutation`

---

## 8. AI & LangGraph Workflow

### 8.1 Request flow

1. Frontend POSTs `{ job_type, context }` to `POST /api/ai/stream`
2. Django Ninja async endpoint creates `AIJob` row (status: `running`)
3. LangGraph routes to the correct agent graph by `job_type`
4. Agent calls OpenAI GPT-4o with `stream=True`
5. Django returns `StreamingHttpResponse` (`Content-Type: text/event-stream`)
6. `useSSEStream` hook in React pipes tokens into `useAIStore` — UI updates word-by-word
7. On completion, `AIJob.output_data` is written and status set to `done`

### 8.2 Agent definitions

**SubjectLineAgent** (`job_type: subject_lines`)
- Input: campaign name, industry, tone, existing draft
- Nodes: `analyze_context` → `generate_variants` → `score_and_rank`
- Output: 5 ranked subject lines with predicted engagement score

**CopyOptimizerAgent** (`job_type: copy_optimize`)
- Input: email body HTML, tone target, brand voice descriptor
- Nodes: `extract_text` → `rewrite_copy` → `validate_tone`
- Output: improved copy streamed word-by-word

**SpamCheckerAgent** (`job_type: spam_check`)
- Input: subject line, preview text, email body
- Nodes: `flag_spam_words` → `score_deliverability` → `suggest_fixes`
- Output: spam score 0–100, list of flagged terms, actionable fix suggestions

**CTAOptimizerAgent** (`job_type: cta_suggest`)
- Input: campaign goal, current CTA text, industry vertical
- Nodes: `identify_goal` → `generate_ctas` → `rank_by_conversion`
- Output: 4 CTA variants ranked by predicted conversion rate

### 8.3 Provider swapping

All agents accept a `BaseChatModel` instance. Swapping from OpenAI to Anthropic or Google is a one-line change in `config/ai.py`. The per-org `openai_api_key` from the `Organization` model is injected at request time.

---

## 9. Email Builder (GrapesJS + MJML)

- GrapesJS loaded with `grapesjs-mjml` plugin — the canvas IS MJML-native; blocks map directly to MJML components (`mj-section`, `mj-column`, `mj-button`, etc.)
- `gjs_components` + `gjs_styles` store the MJML component tree as JSONB (round-trip editable)
- `mjml_source` column stores the serialised MJML string exported from the GrapesJS canvas
- `POST /api/templates/{id}/compile` runs `mjml(mjml_source)` via the Python `mjml` package (wraps Node.js MJML) → stores result in `html_output`
- MJML ensures cross-client compatibility (Gmail, Outlook, Apple Mail, mobile clients)
- Mobile preview toggle renders the compiled HTML at 375px width in an iframe
- Personalization tags (`{{first_name}}`, `{{company_name}}`, `{{industry}}`, `{{designation}}`) are replaced at send time using `CampaignRecipient.personalization` JSONB values

---

## 10. Email Sending Flow

1. User uploads recipient CSV to `POST /api/campaigns/{id}/recipients`
2. User triggers `POST /api/campaigns/{id}/send-now` or `/schedule`
3. Django Ninja endpoint creates a Django-Q2 task: `dispatch_campaign(campaign_id)`
4. Django-Q2 worker picks up the task, fetches `Campaign` + all `CampaignRecipient` rows with `status=queued`
5. For each recipient: render personalized HTML (replace `{{tags}}`), send via `SMTPConfig`, update `CampaignRecipient.status`
6. Campaign `status` updated to `sent` or `failed` on completion

---

## 11. Security

- All API routes require JWT in `Authorization: Bearer <token>` header
- Org-scoped middleware: every queryset filtered by `request.auth.organization` — impossible to leak cross-org data
- SMTP passwords and OpenAI API keys encrypted at rest via `django-fernet-fields`
- Role enforcement: `admin` — full access; `editor` — create/edit/send; `viewer` — read-only
- Google OAuth only — no password reset flows to maintain for SSO users
- CSRF not required (JWT-only API, no cookie sessions)

---

## 12. Project Structure

```
project-root/
├── backend/
│   ├── config/              # Django settings, urls, wsgi, asgi
│   ├── apps/
│   │   ├── accounts/        # Extended User, allauth config
│   │   ├── organizations/   # Extended django-organizations models
│   │   ├── templates_app/   # EmailTemplate model + API
│   │   ├── campaigns/       # Campaign, CampaignRecipient + API
│   │   ├── ai/              # LangGraph agents, SSE endpoint
│   │   └── settings_app/    # SMTPConfig + API
│   ├── core/
│   │   ├── middleware.py     # Org-scoped request middleware
│   │   ├── permissions.py    # Role-based permission classes
│   │   └── pagination.py
│   └── requirements.txt
├── frontend/
│   ├── src/                 # React + Vite (structure per Section 7)
│   ├── package.json
│   └── vite.config.ts
└── docs/
    └── superpowers/specs/
```

---

## 13. Django Apps Breakdown

| App | Models | Responsibility |
|-----|--------|----------------|
| `accounts` | Custom User | Extended AbstractUser, allauth config, JWT views |
| `organizations` | Organization, OrgUser, OrgOwner | Extended django-organizations |
| `templates_app` | EmailTemplate | GrapesJS CRUD, MJML compile endpoint |
| `campaigns` | Campaign, CampaignRecipient | Campaign lifecycle, CSV upload, send/schedule |
| `ai` | AIJob | LangGraph agents, SSE streaming |
| `settings_app` | SMTPConfig | SMTP CRUD, test-send, AI key management |

---

## 14. Out of Scope (Phase 1)

The following are explicitly deferred to Phase 2:
- Analytics dashboard (open rates, CTR, bounce rates, heatmaps)
- Audience / contact management (import lists, segmentation, suppression lists)
- SaaS org self-signup and billing
- A/B testing
- Dark mode email preview
- Webhook tracking (email opens, link clicks)
