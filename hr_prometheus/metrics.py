from prometheus_client import Counter, Gauge, Histogram

REQUEST_COUNT = Counter(
    "request_count", "Number of requests received", ["method", "path", "status"]
)
REQUEST_LATENCY = Histogram(
    "request_latency", "Elapsed time per request", ["method", "path"]
)
REQUEST_IN_PROGRESS = Gauge(
    "requests_in_progress", "Requests in progress", ["method", "path"]
)
