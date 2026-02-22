# GEMINI.md

This file provides strict guidance to GEMINI Code (and any other agentic assistants) when working with the HackURI repository.

## Project Overview

HackURI is a GitHub-integrated task management system with AI (Gemini) support, built for the "Ocean's Edge Ventures" hackathon track.

- **Frontend:** Electron + Vue 3 + TypeScript (3-stage UI: Floating Arrow -> Mini Menu -> Full Screen)
- **Backend:** Django REST Framework + MongoDB

## Commands

### Desktop (`desktop/`)

```bash
npm install          # Install dependencies
npm run dev          # Dev server with hot reload
npm run build        # Typecheck + build (all platforms)
npm run build:mac    # Build macOS .dmg
npm run build:win    # Build Windows .exe
npm run build:linux  # Build Linux packages
npm run lint         # ESLint
npm run format       # Prettier
npm run typecheck    # Type check (Node + Vue)
```

### API (`api/`)

```bash
pip install -r requirements.txt   # Install Python deps
python manage.py migrate          # Run DB migrations
python manage.py runserver        # Dev server on :8000
python manage.py shell            # Django shell
```

## 🚨 STRICT SECURITY PROTOCOLS (CRITICAL) 🚨

- **Zero Client-Side Secrets:** NEVER expose, hardcode, or log any API keys in the Electron frontend. This includes the `GEMINI_API_KEY`, `GITHUB_WEBHOOK_SECRET`, and `SLACK_BOT_TOKEN`.
- **Backend Proxying:** The Electron app MUST NEVER interact directly with the Gemini API or GitHub API. All external AI and webhook interactions must be routed through the Django backend.
- **Environment Management:** All secrets must be loaded dynamically via `django-environ` in the Django backend. Always ensure `.env` is explicitly listed in `.gitignore`.

## Architecture & Workflows

### 1. Frontend (Electron/Vue 3)

- **UI State Isolation:** Build components modularly to support the distinct 3 states: `FloatingWidget.vue`, `MiniMenu.vue`, and `FullScreenApp.vue`. Do not blend these UI states.
- **Preload Bridge:** Use Electron's `contextBridge` for all communication between the Vue renderer and the Node.js main process.
- **Authentication:** Use Axios with interceptors to attach Django session/auth tokens to every backend request securely.

- **`lib/api.ts`** — Axios instance with base URL `VITE_API_BASE_URL/api`; request interceptor attaches `Authorization: Token {token}`
- **`stores/auth.ts`** — Pinia store holding token, GitHub token, and user profile
- **`router/index.ts`** — Three routes: `/` (login), `/workspaces` (list), `/workspace/:id` (task detail)
- **`pages/`** — `LoginPage.vue`, `WorkspacesPage.vue`, `WorkspacePage.vue`

### 2. Backend (Django/MongoDB)

- **Webhook Verification:** When parsing GitHub webhook payloads, ALWAYS verify the `x-hub-signature-256` header against the `GITHUB_WEBHOOK_SECRET` before processing the commit data.
- **Agentic Evaluation Chain:** 1. Parse the incoming GitHub commit diff. 2. Securely query the MongoDB `Task` collection to retrieve the current workspace context. 3. Send the diff and context to the Gemini API securely from the Django service. 4. Parse Gemini's JSON response to update the task status, adjust deadlines, and format the "Hivemind" Slack broadcast.
- **`HackAPI/models.py`** — `Workspace` and `Task` MongoDB models using `django-mongodb-backend`. Uses `ObjectId` PKs.
- **`HackAPI/views/`** — ViewSets per domain: `auth.py` (GitHub OAuth), `workspaces.py`, `tasks.py`, `webhooks.py` (GitHub + Slack events), `slack.py`
- **`HackAPI/services/`** — External integrations: `gemini.py` (Google AI), `slack.py` (Slack SDK)
- **`api/settings.py`** — All config loaded from `.env`: MongoDB URI, GitHub OAuth, Gemini key, Slack tokens, CORS

Auth flow: GitHub OAuth → API exchanges code for token → returns Django `Token` + GitHub token + user profile.

    ### Environment Variables

**`api/.env`:**

```
DJANGO_SECRET_KEY, DEBUG, ALLOWED_HOSTS, MONGODB_URI, MONGODB_NAME,
GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, GITHUB_WEBHOOK_SECRET,
GEMINI_API_KEY, CORS_ALLOWED_ORIGINS, SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET
```

**`desktop/.env`:**

```
VITE_API_BASE_URL=http://localhost:8000
VITE_GITHUB_CLIENT_ID=<oauth-app-id>
```

## Code Style

- TypeScript/Vue: single quotes, no semicolons, 100-char line width (Prettier via `.prettierrc.yaml`)
- Python files are excluded from Prettier (`.prettierignore`)
- Indentation: 4 spaces; line endings: LF (`.editorconfig`)
