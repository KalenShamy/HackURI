# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

HackURI is a GitHub-integrated task management system with Slack and AI (Gemini) support. It has two components:

- **`api/`** — Django REST Framework backend with MongoDB
- **`desktop/`** — Electron + Vue 3 + TypeScript desktop application

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

## Architecture

### Backend (`api/`)

- **`HackAPI/models.py`** — `Workspace` and `Task` MongoDB models using `django-mongodb-backend`. Uses `ObjectId` PKs.
- **`HackAPI/views/`** — ViewSets per domain: `auth.py` (GitHub OAuth), `workspaces.py`, `tasks.py`, `webhooks.py` (GitHub + Slack events), `slack.py`
- **`HackAPI/services/`** — External integrations: `gemini.py` (Google AI), `slack.py` (Slack SDK)
- **`api/settings.py`** — All config loaded from `.env`: MongoDB URI, GitHub OAuth, Gemini key, Slack tokens, CORS

Auth flow: GitHub OAuth → API exchanges code for token → returns Django `Token` + GitHub token + user profile.

### Frontend (`desktop/src/renderer/src/`)

- **`lib/api.ts`** — Axios instance with base URL `VITE_API_BASE_URL/api`; request interceptor attaches `Authorization: Token {token}`
- **`stores/auth.ts`** — Pinia store holding token, GitHub token, and user profile
- **`router/index.ts`** — Three routes: `/` (login), `/workspaces` (list), `/workspace/:id` (task detail)
- **`pages/`** — `LoginPage.vue`, `WorkspacesPage.vue`, `WorkspacePage.vue`

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