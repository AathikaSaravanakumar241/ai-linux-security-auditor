# Setup & Run Guide — Local/Dev Environments

This document details steps to quickly spin up the AI Linux Security Auditor on a local system.

## Docker Quickstart

The easiest way to start the entire system (React frontend, FastAPI backend, Postgres database, and an Ubuntu SSH audit target) is using Docker Compose.

### 1. Configure Environment
Copy `.env.example` to `.env` in the root workspace and add your Gemini API Key:
```bash
# Set Gemini Key (mandatory for AI analysis)
$env:GEMINI_API_KEY="YOUR_KEY_HERE"  # PowerShell
# Or edit the .env file directly.
```

### 2. Launch Services
Run the composition from the root directory:
```bash
docker compose up --build -d
```

### 3. Verify Health
Verify that the services are online:
- **Frontend Panel**: Browse to `http://localhost:3000` to interact with the auditor.
- **Backend API**: View API docs and test endpoints directly at `http://localhost:8000/docs`.
- **SSH Target**: The test target is accessible locally on port `2222` with username `auditor` and password `password123`.

---

## Local Development Mode

If you prefer to run services individually without containers during development:

### 1. Backend Setup (FastAPI)
1. Install Python 3.11.
2. Initialize virtual environment and install packages:
   ```bash
   cd backend
   python -m venv venv
   # Activate venv:
   # Windows: .\venv\Scripts\activate
   # Linux/MacOS: source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Run the development server:
   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### 2. Frontend Setup (React/Vite)
1. Install Node.js 20+.
2. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```
3. Run Vite dev server:
   ```bash
   npm run dev
   ```
   Open `http://localhost:5173` to test live changes. API calls to `/api/*` will automatically proxy to the backend running on port `8000`.
