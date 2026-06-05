from prometheus_client import Counter, Gauge

# Define Prometheus metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests received",
    ["method", "endpoint", "status_code"]
)

websocket_connections = Gauge(
    "websocket_connections",
    "Current number of active WebSocket connections"
)

scheduler_iterations = Counter(
    "scheduler_iterations",
    "Total number of background scheduler iterations completed"
)

model_reload_success_total = Counter(
    "model_reload_success_total",
    "Total number of successful model hot reloads"
)

model_reload_failure_total = Counter(
    "model_reload_failure_total",
    "Total number of failed model hot reloads"
)

from prometheus_client import Histogram
model_reload_duration_seconds = Histogram(
    "model_reload_duration_seconds",
    "Time taken to complete a model hot reload",
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, float("inf"))
)
