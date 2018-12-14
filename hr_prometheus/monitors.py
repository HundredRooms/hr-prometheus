import time

from prometheus_client import Counter, Gauge, Histogram


class BaseRequestMonitor:
    """
    Base context manager from which to inherit for request monitoring
    """

    def __init__(self, request, init_metrics=True, end_metrics=True):
        self.request_description = (request.method, request.path)
        self.init_time = None
        self.response_status = None
        self.init_metrics = init_metrics
        self.end_metrics = end_metrics

    def __enter__(self):
        self.init_time = time.time()
        if self.init_metrics:
            self.update_init_metrics()
        return self

    def __exit__(self, exc_type, *args):
        if exc_type is None:
            self._check_response_is_observed()
        else:
            self.response_status = 500
        if self.end_metrics:
            self.update_end_metrics()

    def observe(self, response):
        self.response_status = response.status

    def _check_response_is_observed(self):
        if self.response_status is None:
            raise Exception(
                "The request response has not been observed. "
                "Use the method 'observe'"
            )

    def update_init_metrics(self):
        raise NotImplementedError()

    def update_end_metrics(self):
        raise NotImplementedError()


class RequestMonitor(BaseRequestMonitor):
    """
    Default context manager with request count, latency and in progress
    metrics.
    """

    REQUEST_COUNT = Counter(
        "request_count", "Number of requests received", ["method", "path", "status"]
    )
    REQUEST_LATENCY = Histogram(
        "request_latency", "Elapsed time per request", ["method", "path"]
    )
    REQUEST_IN_PROGRESS = Gauge(
        "requests_in_progress", "Requests in progress", ["method", "path"]
    )

    def update_init_metrics(self):
        self.REQUEST_IN_PROGRESS.labels(*self.request_description).inc()

    def update_end_metrics(self):
        resp_time = time.time() - self.init_time
        self.REQUEST_COUNT.labels(*self.request_description, self.response_status).inc()
        self.REQUEST_LATENCY.labels(*self.request_description).observe(resp_time)
        self.REQUEST_IN_PROGRESS.labels(*self.request_description).dec()
