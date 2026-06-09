# Project Documentation

> Phase-level documentation capturing objectives, architecture decisions, files created, testing instructions, deployment notes, and status for each development phase.

---

## Phase 1 — Backend Foundation

| Field | Value |
|---|---|
| **Phase** | Phase 1 — Backend Foundation |
| **Status** | ✅ Complete |
| **Date** | 2026-06-08 |

---

### Objective

Establish the complete backend foundation for the AI Linux Security Auditor: FastAPI application, service layer (SSH, audit, Gemini, database), PostgreSQL schema, configuration management, and error handling.

---

### Files Created

```
backend/
├── app/
│   ├── __init__.py                 # Python package marker
│   ├── main.py                     # FastAPI application entry point
│   ├── config.py                   # Pydantic Settings (env var management)
│   ├── database.py                 # SQLAlchemy engine, session, Base, init_db
│   ├── models.py                   # ORM models: Audit, Finding
│   ├── schemas.py                  # Pydantic request/response schemas
│   └── services/
│       ├── __init__.py             # Python package marker
│       ├── ssh_service.py          # Paramiko SSH connection & commands
│       ├── audit_service.py        # Predefined command execution & aggregation
│       ├── gemini_service.py       # Gemini API integration & JSON parsing
│       └── database_service.py     # CRUD operations for audits & findings
├── .env.example                    # Environment variable template
└── requirements.txt                # Updated (added pydantic-settings)

docs/
├── prompt_documentation.md         # Module-level generation log
└── project_documentation.md        # This file
```

**Files removed:** `services/ai_service.py`, `services/ssh_client.py`, `rules/ssh_client.py`, `rules/` directory (all were empty skeletons replaced by spec-compliant modules).

---

### Architecture Decisions

| Decision | Rationale |
|---|---|
| **Pydantic Settings (`config.py`)** | Type-safe env loading with validation at startup. Single source of truth. Supports `.env` files and env var overrides. |
| **SQLAlchemy with connection pooling** | `pool_size=5`, `max_overflow=10`, `pool_pre_ping=True`. Prevents exhaustion under load. `pool_pre_ping` detects stale connections. |
| **`get_db()` dependency with commit/rollback** | FastAPI dependency yields a session, commits on success, rolls back on exception, always closes. Ensures transactional integrity. |
| **Context-manager SSH (`SSHService`)** | Guarantees connection cleanup via `__exit__`, even if exceptions occur during audit execution. |
| **Graceful per-command failure** | A single failing audit command (e.g., `ufw` not installed) doesn't abort the entire audit. Error output is included in the report. |
| **Retry with exponential backoff (Gemini)** | 3 attempts with 1s/2s/4s backoff handles transient API failures and rate limits. |
| **Multi-strategy JSON extraction** | Handles Gemini wrapping JSON in markdown fences (`\`\`\`json ... \`\`\``), direct JSON, or embedded `[...]` arrays. |
| **flush() not commit() in CRUD** | Database service uses `flush()` to assign IDs without committing. The `get_db()` dependency controls the transaction boundary. |
| **Cascade delete on findings** | `cascade="all, delete-orphan"` on the relationship. Deleting an audit auto-removes its findings. |
| **`selectin` eager loading** | Findings are loaded with the audit in a single query round-trip, avoiding N+1 queries. |
| **CORS allow-all for development** | `CORS_ORIGINS=*` in dev. Must be restricted in production (documented in `.env.example`). |
| **Lifespan-based startup** | Uses `asynccontextmanager` lifespan (not deprecated `on_event`). Creates DB tables on startup. |

---

### Scalability & Cloud Deployment Considerations

- **DATABASE_URL** is an environment variable — trivially swappable to managed PostgreSQL (Cloud SQL, RDS, Azure Database).
- **Connection pooling** can be replaced by external pooling (PgBouncer) + `NullPool` in SQLAlchemy for serverless deployments.
- **Stateless API** — no in-process state. Horizontally scalable behind a load balancer.
- **SSH connections are synchronous** — future phases should offload to background workers (Celery, Cloud Tasks) for concurrent audits.
- **Gemini API key** is per-instance; for teams, use a secrets manager (GCP Secret Manager, AWS Secrets Manager, HashiCorp Vault).

---

### Testing Instructions

#### Prerequisites

1. **PostgreSQL** — Start via Docker Compose:
   ```bash
   cd infrastructure
   docker compose up -d
   ```

2. **SSH Test Target** — Add to `docker-compose.yml` or build/run separately:
   ```bash
   docker build -t audit-target -f Dockerfile.audit .
   docker run -d -p 2222:22 --name audit-target audit-target
   ```

3. **Environment** — Copy `.env.example` to `backend/.env` and set `GEMINI_API_KEY`:
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env and set GEMINI_API_KEY=<your-key>
   ```

4. **Dependencies** — Activate venv and install:
   ```bash
   cd backend
   venv\Scripts\activate        # Windows
   pip install -r requirements.txt
   ```

#### Running the Server

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Endpoint Testing

```bash
# Health check
curl http://localhost:8000/health

# Run a full audit (against Docker SSH target)
curl -X POST http://localhost:8000/audit \
  -H "Content-Type: application/json" \
  -d '{"host": "localhost", "port": 2222, "username": "auditor", "password": "password123"}'

# List audit history
curl http://localhost:8000/audits

# Get specific audit details
curl http://localhost:8000/audit/1
```

#### Verify Database

```bash
docker exec -it linux_audit_db psql -U postgres -d linux_audit -c "\dt"
docker exec -it linux_audit_db psql -U postgres -d linux_audit -c "SELECT id, server_ip, audit_date FROM audits;"
docker exec -it linux_audit_db psql -U postgres -d linux_audit -c "SELECT id, audit_id, severity, issue FROM findings;"
```

---

### Deployment Notes

- **Local development**: Run PostgreSQL and SSH target via Docker Compose. Run FastAPI with `uvicorn --reload`.
- **Production**: Containerize the backend and frontend. Use managed PostgreSQL. Set `CORS_ORIGINS` to specific domains. Use a secrets manager for `GEMINI_API_KEY`. Deploy behind Nginx.
- **Monitoring**: FastAPI auto-generates OpenAPI docs at `/docs` (Swagger UI) and `/redoc`.

---

## Phase 1 — Frontend Scaffold & Monorepo Configuration

| Field | Value |
|---|---|
| **Phase** | Phase 1 — Frontend Scaffold & Monorepo Configuration |
| **Status** | ✅ Complete |
| **Date** | 2026-06-08 |

---

### Objective

Establish the frontend React/Vite/Tailwind CSS-first application structure, API client layers, navigation layout shell, page view placeholders, and configure unified multi-container Docker Orchestration (FastAPI, React served by Nginx, PostgreSQL, and Ubuntu SSH target) for the monorepo architecture.

---

### Files Created

```
frontend/
├── vite.config.js                  # Vite config (proxy setup, aliases)
├── index.html                      # Main HTML page (meta tags & SEO layout)
├── nginx.conf                      # Production Nginx reverse-proxy setup
├── src/
│   ├── index.css                   # Tailwind v4 import + cybersecurity theme
│   ├── App.css                     # App layout CSS rules
│   ├── main.jsx                    # React app entry point (BrowserRouter)
│   ├── App.jsx                     # Router config with all route mappings
│   ├── api/
│   │   ├── client.js               # Axios instance (custom interceptors)
│   │   └── audits.js               # Wrapper for audit API calls
│   ├── components/
│   │   ├── layout/
│   │   │   └── AppLayout.jsx       # App sidebar shell with routes integration
│   │   └── common/
│   │       ├── SeverityBadge.jsx   # Severity level label component
│   │       ├── StatCard.jsx        # Clickable counts display card
│   │       └── LoadingSpinner.jsx  # Page-level spinner with messages
│   ├── pages/
│   │   ├── LoginPage.jsx           # Form placeholder (simulated authentication)
│   │   ├── DashboardPage.jsx       # Severe findings and count summary
│   │   ├── NewAuditPage.jsx        # Host credential input form
│   │   ├── AuditResultsPage.jsx    # Display table of findings
│   │   └── AuditHistoryPage.jsx    # Audited servers chronological logs
│   ├── hooks/
│   │   └── useAudit.js             # API wrapper hook skeleton
│   └── utils/
│       └── helpers.js              # Formatting functions (dates, counters)

./
├── Dockerfile.backend              # Multi-stage Docker image for FastAPI
├── Dockerfile.frontend             # Build + Nginx Docker image for React/Vite
└── docker-compose.yml              # Root docker-compose configuration
```

---

### Architecture Decisions

| Decision | Rationale |
|---|---|
| **Vite Dev Server Proxy** | Routes all `/api/*` requests in development to `localhost:8000/*` to avoid CORS issues. |
| **Nginx Production Proxy** | Production container runs Nginx serving static frontend assets and routing `/api/` traffic directly to the FastAPI container. No hardcoded backend URLs in frontend code. |
| **Tailwind v4 (CSS-first)** | Integrates directly via `@import "tailwindcss";`. Custom HSL color variables and micro-animations configured directly in CSS. |
| **React Router v7** | Unified router with explicit route definition, parameter reading (e.g. `/audit/:id`), and dynamic navigation. |
| **Axios client wrapper** | Decoupled client from page components. Attaches authorization headers automatically (stubbed) and handles timeouts (120s limit for long SSH + Gemini pipeline). |
| **Centralized custom hook** | `useAudit` manages states for API execution, making components clean and testable. |
| **Unified Docker Compose** | Root `docker-compose.yml` orchestrates frontend, backend, database, and SSH target. Allows developers to spin up the entire stack with a single command. |

---

### Testing & Verification

#### Running local dev servers

1. **Start backend**:
   ```bash
   cd backend
   # Make sure venv is active
   python -m uvicorn app.main:app --reload
   ```

2. **Start frontend**:
   ```bash
   cd frontend
   npm run dev
   ```
   Open `http://localhost:5173` to see the React shell dashboard.

#### Running unified Docker containers

```bash
# Set Gemini API key
$env:GEMINI_API_KEY="your-key-here"   # Windows Powershell
# Or set in environment

# Start the full orchestration
docker compose up --build -d
```
- Open `http://localhost:3000` to interact with the application.
- API requests will proxy seamlessly to backend at `http://localhost:8000`.
- PostgreSQL database starts and runs on port `5432`.
- SSH target starts on port `2222`.

