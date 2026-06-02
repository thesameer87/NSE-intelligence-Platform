# V1 Architecture Summary

This document outlines the strictly isolated module boundaries and deterministic logic flow executed in V1 of the NSE Intelligence Platform.

## Backend Determinism
The backend executes via a strictly async `FastAPI` lifecycle:

1. **Environment Gate**: `config_validator.py` ensures the application aborts instantly prior to HTTP port binding if critical secrets are missing.
2. **Persistence Layer**: `SQLAlchemy 2.0` (asyncpg) strictly isolates domain models (`IntradayTick`, `TradingSignal`) using async-safe session dependency injection (`get_db_session`).
3. **Ingestion Orchestrator**: `scheduler.py` coordinates continuous `Angel One` ingestion loops, protected by isolated `Exception` traps that route failures to deterministic `logger.exception()` stack outputs rather than crashing the loop.
4. **WebSocket Manager**: Predictable pub/sub implementation that broadcasts specific typed events (`market_tick`, `signal_alert`, `prediction_update`, `portfolio_update`) to authorized dashboard clients. Connection telemetry (active counts) is deterministically logged without modifying runtime behavior.

## Frontend Presentation Isolation
The frontend (`React`, `Vite`) strictly consumes DTOs and handles real-time synchronization deterministically:

1. **State Synchronization**: `useDashboardData.ts` consumes REST primitives on mount and patches updates via WebSocket `message` events using strict deduplication semantics (prepending unique items, bounding array queues, slicing to deterministic limits).
2. **Graceful Degradation**: Error handling is isolated horizontally. Individual layout units (`MarketTickTable`, `SignalTable`) are wrapped in strictly typed `ErrorBoundary` boundary instances. If an ingested tick is malformed and causes a render crash, it only gracefully degrades the single widget, preserving the remainder of the active dashboard connection.
3. **Deterministic Observability**: Overridden `logger.ts` pipes unhandled error boundary stacks straight to standard `console.error` in a clean, typed payload without utilizing V2 telemetry vendors (Sentry/DataDog).
