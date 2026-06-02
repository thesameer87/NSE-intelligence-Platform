# NSE Intelligence Platform (V1)

A production-grade, deterministically synchronized full-stack platform for market data ingestion, prediction modeling, and real-time dashboard presentation.

## V1 Scope
The V1 release establishes a strict deterministic foundation:
- **Backend**: Async Python (FastAPI, SQLAlchemy, Pytest) handling market data ingestion (Angel One), deterministic background orchestration, and WebSocket telemetry.
- **Frontend**: Typed React/Vite dashboard presenting strictly isolated Market, Signal, Portfolio, and Model states with graceful error degradation.
- **Deployment**: Bare-metal CI/CD readiness with exact environment validation. No cloud lock-in, Docker, or Kubernetes is utilized in V1.

## Getting Started

### 1. Environment Setup
Copy the production-safe environment template:
```bash
cp .env.example .env
```
Ensure all `PRODUCTION REQUIRED SECRETS` are populated correctly. The system implements a fail-fast startup gate that will immediately abort if security keys or database URLs are malformed.

### 2. Backend Initialization (Python 3.11+)
The backend relies on strict dependency pinning for 100% reproducible environments.
```bash
cd backend
python -m pip install -r requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```
*Note: The backend will perform a static configuration check upon startup.*

### 3. Frontend Initialization (Node 20+)
The frontend utilizes strict lockfile installation (`npm ci`) to guarantee deterministic execution matching the CI pipeline.
```bash
cd frontend
npm ci
npm run build
npm run preview -- --host 0.0.0.0 --port 3000
```

## Quality Gates & Local Development
All contributions must pass strict quality gates matching the CI matrix:

**Backend Validation:**
```bash
cd backend
mypy backend/     # Static type analysis
pytest backend/   # Dependency-injected test execution
```

**Frontend Validation:**
```bash
cd frontend
npm run lint      # React/Hook safety checks
npx vitest run    # Component & Error Boundary deterministic tests
```

## Documentation Directory
- `docs/ARCHITECTURE_V1.md`: Detailed module-boundary design and dependency flows.
- `docs/VALIDATION.md`: V1 release validation and troubleshooting procedures.
- `DEPLOYMENT.md`: Exact startup sequence and CI integration logic.
