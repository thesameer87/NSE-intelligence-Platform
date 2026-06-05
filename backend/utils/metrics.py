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
