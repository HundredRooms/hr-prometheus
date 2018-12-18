from enum import Enum

import pytest

from hr_prometheus.utils import TimeMonitor, apply_labels


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


def test_decorator(mocker):
    metric_mock = mocker.Mock()
    mocker.patch("hr_prometheus.utils.time", return_value=3.141_592_653_59)
    apply_labels_mock = mocker.patch(
        "hr_prometheus.utils.apply_labels", return_value=metric_mock
    )
    context = TimeMonitor(metric_mock, ["label1"])

    @context
    def test():
        assert context.init_time == 3.141_592_653_59
        assert context.metric == metric_mock

    test()
    apply_labels_mock.assert_called_once_with(metric_mock, ["label1"])
    metric_mock.observe.assert_called_once_with(0)


async def test_decorator_async(mocker):
    metric_mock = mocker.Mock()
    mocker.patch("hr_prometheus.utils.time", return_value=3.141_592_653_59)
    apply_labels_mock = mocker.patch(
        "hr_prometheus.utils.apply_labels", return_value=metric_mock
    )
    context = TimeMonitor(metric_mock, ["label1"])

    @context
    async def test():
        assert context.init_time == 3.141_592_653_59

    await test()
    apply_labels_mock.assert_called_once_with(metric_mock, ["label1"])
    metric_mock.observe.assert_called_once_with(0)


def test_contextmanager(mocker):
    metric_mock = mocker.Mock()
    mocker.patch("hr_prometheus.utils.time", return_value=3.141_592_653_59)
    apply_labels_mock = mocker.patch(
        "hr_prometheus.utils.apply_labels", return_value=metric_mock
    )
    context = TimeMonitor(metric_mock, ["label1"])

    with context as t:
        assert t.init_time == 3.141_592_653_59

    apply_labels_mock.assert_called_once_with(metric_mock, ["label1"])
    metric_mock.observe.assert_called_once_with(0)
