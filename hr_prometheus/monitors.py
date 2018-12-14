import time


class RequestMonitor:
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