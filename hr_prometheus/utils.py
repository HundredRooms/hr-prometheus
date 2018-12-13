from enum import Enum


def apply_labels(metric, labels):
    resolved_labels = [
        label.value if isinstance(label, Enum) else label for label in labels
    ]
    return metric.labels(*resolved_labels)
