import pytest

from hr_prometheus.monitors import RequestMonitor


def test_monitor_response_not_observed(mocker):
    request_mock = mocker.Mock(method="GET", path="/path")
    with pytest.raises(Exception):
        with RequestMonitor(request_mock):
            pass


def test_monitor_observe(mocker):
    request_mock = mocker.Mock(method="GET", path="/path")
    with RequestMonitor(request_mock) as monitor:
        monitor.observe(mocker.Mock(status=200))
        assert monitor.response_status == 200


def test_monitor_exception_always_500(mocker):
    request_mock = mocker.Mock(method="GET", path="/path")
    monitor = None
    with pytest.raises(Exception), RequestMonitor(request_mock) as monitor:
        monitor = monitor
        monitor.observe(mocker.Mock(status=200))
        raise Exception
    assert monitor.response_status == 500
