import pytest
from hr_prometheus.monitors import (
    RequestMonitor,
    _path_with_fixed_parameters,
    _resolve_path,
)

PATH = "hr_prometheus.monitors"


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


def test_request_monitor_no_fixed_routes_parameters(mocker):
    request_mock = mocker.Mock(method="GET", path="/path")
    monitor = RequestMonitor(request_mock)
    assert monitor.request_description[1] == "/path"


@pytest.mark.parametrize(
    "wrong_fixed_routes_parameters",
    [
        (["resource_id"]),
        (23,),
        ({"route_name": {"some": "dict"}}),
        ({"route_name": 16}),
    ],
)
def test_request_monitor_wrong_fixed_routes_parameters(
    mocker, wrong_fixed_routes_parameters
):
    request_mock = mocker.Mock(method="GET", path="/path")
    request_mock.match_info.route.name = "route_name"

    with pytest.raises(ValueError):
        RequestMonitor(
            request_mock, fixed_routes_parameters=wrong_fixed_routes_parameters
        )


def test_resolve_path_no_fixed_parameters(mocker):
    request_path = "/v1/resource"
    fixed_parameters_routes_dispatcher = {}
    request = mocker.Mock(path=request_path)
    assert _resolve_path(request, fixed_parameters_routes_dispatcher) == request_path


def test_resolve_path_fixed_parameters(mocker):
    request_path = "/v1/resource/666"
    custom_path = "/v1/resource/{resource_id}"

    fixed_parameters_routes_dispatcher = {"sample_route": ["resource_id"]}

    request = mocker.Mock(path=request_path)
    request.match_info.route.name = "sample_route"
    with mocker.patch(f"{PATH}._path_with_fixed_parameters", return_value=custom_path):
        resolved_path = _resolve_path(request, fixed_parameters_routes_dispatcher)
        assert resolved_path == custom_path


def test_path_with_fixed_parameters(mocker):
    base_url = "/{version}/resource/{resource_id}"
    fixed_parameters = ["resource_id"]

    request_match_info = {"resource_id": "1234", "version": "v1"}
    resource_info_pattern = mocker.Mock()
    resource_info_pattern.groupindex.keys.return_value = request_match_info.keys()
    resource_info = {"formatter": base_url, "pattern": resource_info_pattern}
    request = mocker.Mock()
    request.match_info.route.resource.get_info.return_value = resource_info
    request.match_info.__getitem__ = lambda self, x: request_match_info.get(x)

    path_1234 = _path_with_fixed_parameters(request, fixed_parameters)
    request_match_info["resource_id"] = "4321"
    path_4321 = _path_with_fixed_parameters(request, fixed_parameters)
    assert "/v1/resource/{resource_id}" == path_1234 == path_4321
