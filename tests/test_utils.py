from enum import Enum

import pytest

from hr_prometheus.utils import apply_labels


class EnumLabels(Enum):
    LABEL1 = "label1"
    LABEL2 = "label2"


@pytest.mark.parametrize(
    "labels,expected",
    [
        (["label1"], ["label1"]),
        ([EnumLabels.LABEL1], ["label1"]),
        (["label1", EnumLabels.LABEL2], ["label1", "label2"]),
    ],
)
def test_apply_labels(labels, expected, mocker):
    metric_mock = mocker.Mock()
    apply_labels(metric_mock, labels)
    metric_mock.labels.assert_called_once_with(*expected)
