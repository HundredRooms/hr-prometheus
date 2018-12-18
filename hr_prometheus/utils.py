from contextlib import ContextDecorator
from enum import Enum
from time import time


def apply_labels(metric, labels):
    resolved_labels = [
        label.value if isinstance(label, Enum) else label for label in labels
    ]
    return metric.labels(*resolved_labels)


class TimeMonitor(ContextDecorator):
    def __init__(self, metric, labels):
        self.metric = apply_labels(metric, labels)
        self.init_time = None

    def __enter__(self):
        self.init_time = time()
        return self

    def __exit__(self, *exc):
        self.metric.observe(time() - self.init_time)
