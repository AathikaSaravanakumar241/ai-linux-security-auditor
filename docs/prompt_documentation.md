# Prompt Documentation

> Module-level generation log documenting every generated component, the context, files produced, and a summary.

---

## Phase 1 — Backend Foundation

**Date:** 2026-06-08

---

### Module: `config.py` — Application Configuration

| Field | Value |
|---|---|
| **Date** | 2026-06-08 |
| **Module** | `backend/app/config.py` |
| **Prompt Context** | Create a Pydantic Settings class loading DATABASE_URL, GEMINI_API_KEY, GEMINI_MODEL, SSH_TIMEOUT, SSH_COMMAND_TIMEOUT, LOG_LEVEL, and CORS_ORIGINS from a `.env` file. Use `@lru_cache` for singleton access. |
| **Files Generated** | `backend/app/config.py`, `backend/.env.example` |
| **Summary** | Centralized configuration via `pydantic-settings`. All service modules import `get_settings()` for type-safe access. Supports `.env` file and environment variable overrides. |

---

### Module: `database.py` — SQLAlchemy Engine & Session

| Field | Value |
|---|---|
| **Date** | 2026-06-08 |
| **Module** | `backend/app/database.py` |
| **Prompt Context** | Create SQLAlchemy engine with connection pooling (pool_size=5, max_overflow=10, pool_pre_ping=True). Provide `SessionLocal` factory, `get_db()` FastAPI dependency with commit/rollback/close lifecycle, and `init_db()` for table creation on startup. |
| **Files Generated** | `backend/app/database.py` |
| **Summary** | Production-ready database layer with connection pooling and proper session lifecycle. `get_db()` commits on success, rolls back on exception, always closes. `init_db()` imports models and calls `create_all()`. |

---

### Module: `models.py` — SQLAlchemy ORM Models

| Field | Value |
|---|---|
| **Date** | 2026-06-08 |
| **Module** | `backend/app/models.py` |
| **Prompt Context** | Create `Audit` and `Finding` ORM models matching the database schema. Audit has 1-to-many relationship with Finding. Use cascade delete-orphan. Eager load findings via selectin. Use UTC timestamps. |
| **Files Generated** | `backend/app/models.py` |
| **Summary** | Two-table schema: `audits` (server_ip, audit_date, raw_report) and `findings` (audit_id FK, severity, issue, explanation, impact, fix_command). Cascade deletes, selectin eager loading, and UTC-aware timestamps. |

---

### Module: `schemas.py` — Pydantic Schemas

| Field | Value |
|---|---|
| **Date** | 2026-06-08 |
| **Module** | `backend/app/schemas.py` |
| **Prompt Context** | Create Pydantic schemas for API validation: AuditRequest (host, port, username, password), FindingResponse, SeverityBreakdown (counts per level), AuditSummary (for list view), AuditDetailResponse (full details with findings). |
| **Files Generated** | `backend/app/schemas.py` |
| **Summary** | Clean API contract decoupled from ORM. SeverityBreakdown provides dashboard card data. All response schemas use `from_attributes=True` for ORM compatibility. |

---

### Module: `ssh_service.py` — Paramiko SSH Service

| Field | Value |
|---|---|
| **Date** | 2026-06-08 |
| **Module** | `backend/app/services/ssh_service.py` |
| **Prompt Context** | Implement SSHService class with context manager protocol. `connect()` establishes SSH connection with configurable timeout. `execute_command()` runs a command and returns (stdout, stderr, exit_code). Custom exceptions: SSHConnectionError, SSHCommandError. Use AutoAddPolicy (document production hardening). |
| **Files Generated** | `backend/app/services/ssh_service.py` |
| **Summary** | Context-manager SSH client guaranteeing cleanup. Configurable timeouts from Settings. Custom exceptions enable precise error handling upstream. AutoAddPolicy documented as prototype-only. |

---

### Module: `audit_service.py` — Audit Command Runner

| Field | Value |
|---|---|
| **Date** | 2026-06-08 |
| **Module** | `backend/app/services/audit_service.py` |
| **Prompt Context** | Define AUDIT_COMMANDS list with all 10 predefined commands. `run_audit()` iterates commands, prefixes each output with `=== COMMAND: <cmd> ===`, and returns combined report string. Failed commands include error in report without aborting. |
| **Files Generated** | `backend/app/services/audit_service.py` |
| **Summary** | Single-function module with hardcoded command list. Graceful failure per command ensures partial results. Output format uses clear delimiters for Gemini parsing. |

---

### Module: `gemini_service.py` — Gemini AI Integration

| Field | Value |
|---|---|
| **Date** | 2026-06-08 |
| **Module** | `backend/app/services/gemini_service.py` |
| **Prompt Context** | Send audit report to Gemini with system prompt demanding JSON output. Enforce PermitRootLogin=Critical rule in prompt. Retry 3 times with exponential backoff. Extract JSON from markdown fences if needed. Validate findings have required fields. |
| **Files Generated** | `backend/app/services/gemini_service.py` |
| **Summary** | Prompt-engineered Gemini integration with retry/backoff, multi-strategy JSON extraction (direct parse, markdown fence, bracket matching), and field validation with graceful defaults. |

---

### Module: `database_service.py` — CRUD Operations

| Field | Value |
|---|---|
| **Date** | 2026-06-08 |
| **Module** | `backend/app/services/database_service.py` |
| **Prompt Context** | Implement CRUD: create_audit, create_findings, create_audit_with_findings (single transaction), get_audit_by_id, get_all_audits (paginated, ordered by date desc). Use flush() not commit() — caller controls transaction. |
| **Files Generated** | `backend/app/services/database_service.py` |
| **Summary** | Pure functions accepting Session dependency. Single-transaction `create_audit_with_findings` ensures data consistency. Pagination via skip/limit with most-recent-first ordering. |

---

### Module: `main.py` — FastAPI Application

| Field | Value |
|---|---|
| **Date** | 2026-06-08 |
| **Module** | `backend/app/main.py` |
| **Prompt Context** | Create FastAPI app with lifespan (init_db on startup). CORS middleware. POST /audit (full pipeline orchestration), GET /audits (paginated history with severity breakdown), GET /audit/{id} (full details). GET /health readiness probe. Map custom exceptions to HTTP errors. |
| **Files Generated** | `backend/app/main.py` |
| **Summary** | Entry point orchestrating the entire audit pipeline. Lifespan-based startup creates DB tables. Three audit endpoints plus health check. Custom exceptions mapped to 502 (SSH/Gemini) and 404 (not found). |

---

## Phase 1 — Frontend Scaffold & Monorepo Configuration

**Date:** 2026-06-08

---

### Module: Vite & Tailwind Configuration

| Field | Value |
|---|---|
| **Date** | 2026-06-08 |
| **Module** | `frontend/vite.config.js`, `frontend/src/index.css` |
| **Prompt Context** | Configure Vite with path aliases (`@` pointing to `src`) and API proxy forwarding `/api` to backend at `http://localhost:8000`. Configure Tailwind v4 design system with cyber-security HSL dark palette and custom animations. |
| **Files Generated** | `frontend/vite.config.js`, `frontend/index.html`, `frontend/src/index.css`, `frontend/src/App.css` |
| **Summary** | Configured dev server with API proxy, custom CSS-first design tokens, styling resets, custom fonts (Inter), and animations (pulse, shake, scan) using Tailwind v4. |

---

### Module: App Shell & Routing

| Field | Value |
|---|---|
| **Date** | 2026-06-08 |
| **Module** | `frontend/src/main.jsx`, `frontend/src/App.jsx` |
| **Prompt Context** | Create React app entry wrapper with `BrowserRouter` and setup client-side routing. Route configurations: login, dashboard, new audit, audit results, audit history. Wrap authenticated routes in `AppLayout`. |
| **Files Generated** | `frontend/src/main.jsx`, `frontend/src/App.jsx` |
| **Summary** | Completed routing skeleton with layout routing, path redirects, and placeholder pages. Ready for state integration. |

---

### Module: API Client & Service Wrapper

| Field | Value |
|---|---|
| **Date** | 2026-06-08 |
| **Module** | `frontend/src/api/client.js`, `frontend/src/api/audits.js` |
| **Prompt Context** | Build Axios client with 120s timeout and auth header injectors, and create helper functions for `/audit`, `/audits`, `/audit/{id}`, `/health`. |
| **Files Generated** | `frontend/src/api/client.js`, `frontend/src/api/audits.js` |
| **Summary** | Abstracted API layer with interceptors for error logging and token management. Wrappers return parsed data from API. |

---

### Module: Shared UI Components

| Field | Value |
|---|---|
| **Date** | 2026-06-08 |
| **Module** | `frontend/src/components/` |
| **Prompt Context** | Scaffold components: `AppLayout` (responsive sidebar navigation), `SeverityBadge` (styled severity levels), `StatCard` (clickable audit KPI stats), `LoadingSpinner` (animated spinner). |
| **Files Generated** | `frontend/src/components/layout/AppLayout.jsx`, `frontend/src/components/common/SeverityBadge.jsx`, `frontend/src/components/common/StatCard.jsx`, `frontend/src/components/common/LoadingSpinner.jsx` |
| **Summary** | Implemented responsive layout shell and common presentation components with proper CSS classes and micro-interactions. |

---

### Module: Page Components & Hooks

| Field | Value |
|---|---|
| **Date** | 2026-06-08 |
| **Module** | `frontend/src/pages/`, `frontend/src/hooks/` |
| **Prompt Context** | Create page shells: `LoginPage`, `DashboardPage`, `NewAuditPage`, `AuditResultsPage`, `AuditHistoryPage`. Create `useAudit` custom hook stub and helpers under `src/utils/helpers.js`. |
| **Files Generated** | `frontend/src/pages/LoginPage.jsx`, `frontend/src/pages/DashboardPage.jsx`, `frontend/src/pages/NewAuditPage.jsx`, `frontend/src/pages/AuditResultsPage.jsx`, `frontend/src/pages/AuditHistoryPage.jsx`, `frontend/src/hooks/useAudit.js`, `frontend/src/utils/helpers.js` |
| **Summary** | Pages completed with mock forms, tabular structures, and stats. Stub hook and utility functions implemented for formatting dates, server IPs, and severity counts. |

---

### Module: Containerization Configuration

| Field | Value |
|---|---|
| **Date** | 2026-06-08 |
| **Module** | `docker-compose.yml`, `Dockerfile.backend`, `Dockerfile.frontend`, `frontend/nginx.conf` |
| **Prompt Context** | Add Docker orchestration configurations for all parts of the monorepo: PostgreSQL database, SSH test target, FastAPI backend, and React/Vite/Nginx frontend. Ensure frontend requests to `/api` are proxied to backend via Nginx in production container. |
| **Files Generated** | `docker-compose.yml`, `Dockerfile.backend`, `Dockerfile.frontend`, `frontend/nginx.conf` |
| **Summary** | Full multi-container composition. Nginx serves production build of frontend and routes backend requests. |

