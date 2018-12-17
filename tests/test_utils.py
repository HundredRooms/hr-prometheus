from enum import Enum

import pytest

from hr_prometheus.utils import TimeMonitor


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
def test_decorator(labels, expected, mocker):
    mocker.patch("hr_prometheus.utils.time", return_value=3.141_592_653_59)
    metric_mock = mocker.Mock()
    context = TimeMonitor(metric_mock, labels)

    @context
    def test():
        assert context.init_time == 3.141_592_653_59

    test()
    metric_mock.labels.assert_called_once_with(*expected)
    metric_mock.labels.return_value.observe.assert_called_once_with(0)


async def test_decorator_async(mocker):
    mocker.patch("hr_prometheus.utils.time", return_value=3.141_592_653_59)
    metric_mock = mocker.Mock()
    context = TimeMonitor(metric_mock, ["label1"])

    @context
    async def test():
        assert context.init_time == 3.141_592_653_59

    await test()
    metric_mock.labels.assert_called_once_with(*["label1"])
    metric_mock.labels.return_value.observe.assert_called_once_with(0)


@pytest.mark.parametrize(
    "labels,expected",
    [
        (["label1"], ["label1"]),
        ([EnumLabels.LABEL1], ["label1"]),
        (["label1", EnumLabels.LABEL2], ["label1", "label2"]),
    ],
)
def test_contextmanager(labels, expected, mocker):
    mocker.patch("hr_prometheus.utils.time", return_value=3.141_592_653_59)
    metric_mock = mocker.Mock()
    context = TimeMonitor(metric_mock, labels)

    with context as t:
        assert t.init_time == 3.141_592_653_59

    metric_mock.labels.assert_called_once_with(*expected)
    metric_mock.labels.return_value.observe.assert_called_once_with(0)
