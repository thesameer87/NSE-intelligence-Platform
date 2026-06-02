# V1 Deployment Readiness & Startup Guide

This document outlines the deterministic deployment flow and startup safety checks for the NSE Intelligence Platform.

## 1. Environment Hardening
Before booting the system in a production environment (`ENVIRONMENT=production`), ensure all required environment variables are set.

Copy the example template:
```bash
cp .env.example .env
```
Update all fields under `PRODUCTION REQUIRED SECRETS` with actual production keys. 
**Note:** In production, `LOG_LEVEL` defaults to `INFO` unless explicitly overridden to minimize I/O overhead.

## 2. Startup Verification
The backend enforces deterministic startup validation. If any required configuration variables are missing or malformed, the `config_validator.py` will fail-fast and exit the process before any network ports are opened or database connections are established.

## 3. CI/CD Quality Gates
Every commit pushed to the `main` branch or a pull request is validated against strict quality gates via GitHub Actions (`.github/workflows/ci.yml`):

### Frontend Verification
- **Lint**: Enforces code consistency and React hook safety (`npm run lint`).
- **Tests**: Validates deterministic rendering, formatters, and error boundary isolation (`npx vitest run`).
- **Build**: Compiles the strictly-typed TypeScript bundle (`npm run build`).

### Backend Verification
- **MyPy**: Static type analysis across all core modules (`mypy backend/`).
- **PyTest**: Ensures robust validation, dependency injection limits, and async-safe orchestration (`pytest backend/`).

## 4. Reproducible Startup Flow
To run the validated bundle locally or on a bare-metal server (no Docker required for V1):

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm ci
npm run build
npm run preview -- --host 0.0.0.0 --port 3000
```

*Note: For V1, deployment is performed directly on target hosts. V2 will introduce containerized orchestration (Docker/Kubernetes).*
