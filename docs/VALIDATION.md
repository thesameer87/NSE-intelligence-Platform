# V1 Release Validation & Troubleshooting

This document serves as the final reproducibility checklist, validation script guidance, and troubleshooting manual for the V1 release.

## Final Reproducibility Checklist
Before confirming any environment deployment, verify the following deterministic criteria:

- [ ] **Dependencies**: The backend strictly consumes exactly pinned definitions inside `requirements.txt`. The frontend strictly resolves via `package-lock.json` using `npm ci`.
- [ ] **Startup Environment**: `.env` is fully populated. Running `uvicorn backend.main:app` successfully passes `config_validator.py` logic.
- [ ] **CI Parity**: The execution of `mypy backend/` and `pytest backend/` return `0` exit codes locally exactly as they do within GitHub Actions.
- [ ] **Graceful Degradation**: Dashboard cards individually handle UI crashes via `ErrorBoundary`. No global application crash is triggered by malformed WebSocket messages.

## Troubleshooting

### Config Validation Failures
**Symptom**: Process exits immediately on startup with `ValidationError`.
**Resolution**: The `ENVIRONMENT` variable explicitly enforces constraints. If `ENVIRONMENT=production`, `SCHEDULER_INTERVAL_SECONDS` must not be drastically low (e.g., < 30). Ensure `JWT_SECRET`, `SUPABASE_URL`, and Angel One keys are explicitly defined in `.env`.

### Alembic Offline Migration Errors (Windows)
**Symptom**: `FileNotFoundError: [WinError 2]` during `pytest` on Alembic targets.
**Resolution**: The tests execute `subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head", "--sql"])` to ensure Windows local environments execute properly. Verify `alembic` is installed inside the active virtual environment by running `python -m alembic --version`.

### WebSocket Disconnections
**Symptom**: Constant frontend websocket disconnection/reconnection cycles.
**Resolution**: V1 isolates connection logging. Check the backend stdout for active connection counts: `Active connections: <N>`. Ensure the frontend's `VITE_WS_URL` is pointing to the correct API host without trailing slashes.

### React Error Boundary Infinite Loops
**Symptom**: Clicking "Try Again" on an Error State immediately re-triggers the Error State without a clean render attempt.
**Resolution**: The `ErrorBoundary` relies on a pure `hasError: false` setState loop. Ensure that the component unmounts correctly. In V1, we maintain determinism by ensuring `Try Again` initiates a clean React reconciliation rather than re-requesting arbitrary network calls or mutating global context outside the component boundary.

## Known V1 Production Risks & Toolchain Bounds

1. **Vitest Windows Teardown Memory Issue**: On Windows native runs, repeated `vitest run` executions may leak memory across watch contexts. We restrict runs strictly to single-pass CI parity (`npx vitest run`) without watch mode to circumvent dangling processes.
2. **Platform Wheel & Toolchain Mismatch**: Because V1 avoids Docker/Kubernetes containerization in favor of bare-metal isolation, backend dependencies containing C-extensions (`asyncpg`, `bcrypt`) rely on pre-compiled Python `.whl` files matching the host architecture. Cross-platform bridging (e.g. developing on MacOS ARM and deploying to Windows AMD64) requires pip to explicitly resolve target architectures.
3. **Python / Node Version Mismatch**: V1 determinism relies on Node 20+ and Python 3.11+. Running the validation gates on earlier versions (e.g., Python 3.9) will result in typing failures (`|` union operators) and unhandled dependency resolutions. Strict version adherence is required to validate the release accurately.
