from contextlib import ContextDecorator
from enum import Enum
from time import time


class TimeMonitor(ContextDecorator):
    def __init__(self, metric, labels):
        self.metric = metric
        self.labels = labels
        self.init_time = None

    def __enter__(self):
        self.init_time = time()
        return self

    def __exit__(self, *exc):
        self._apply_labels().observe(time() - self.init_time)

    def _apply_labels(self):
        resolved_labels = [
            label.value if isinstance(label, Enum) else label for label in self.labels
        ]
        return self.metric.labels(*resolved_labels)
