# hr-prometheus

[![Build Status](https://travis-ci.com/HundredRooms/hr-prometheus.svg?branch=master)](https://travis-ci.com/HundredRooms/hr-prometheus)
[![codecov](https://codecov.io/gh/HundredRooms/hr-prometheus/branch/master/graph/badge.svg)](https://codecov.io/gh/HundredRooms/hr-prometheus)
[![PyPI version](https://badge.fury.io/py/hr-prometheus.svg)](https://badge.fury.io/py/hr-prometheus)

Prometheus integration for aiohttp projects.

hr-prometheus adds support for providing [aiohttp](https://aiohttp.readthedocs.io/en/stable/) applications metrics to [prometheus](https://prometheus.io/docs/introduction/overview/). It is implemented as a aiohttp middleware.

Currently, it exports the following metrics via the /metrics endpoint by default:

- request_latency: Elapsed time per request in seconds.
  - Labels exported: method (HTTP method), path
- request_count: Number of requests received.
  - Labels exported: method (HTTP method), path, status (HTTP status)
- requests_in_progress: In progress requests.
  - Labels exported: method (HTTP method), path

Default request behaviour can be modified by passing a custom `RequestMonitor` to the middleware. You can find out how to do it in [advanced section](#advance-usage).

## Installation

```shell
pip install hr-prometheus
```

## Usage

Briefly, the following is all you need to do to measure and export prometheus metrics from your aiohttp web application:

```python
from aiohttp import web
from hr_prometheus import hrprometheus_middleware, hrprometheus_view

app = web.Application()
app.router.add_get("/metrics", hrprometheus_view)
app.middlewares.append(hrprometheus_middleware())
```

### Advanced usage

#### Custom monitors

To modify the default behavior you simply need to create a new monitor that inherits from the `BaseRequestMonitor` and pass the class to the middleware.

This class provides two public methods. `update_init_metrics` and `update_end_metrics`.
These methods are executed at the beginning and end of a request respectively. Simply add the metrics you want at each point.

Here's an example taken from the default monitor.

```python
from aiohttp import web
from hr_prometheus import hrprometheus_middleware, hrprometheus_view
from hr_prometheus.monitors import BaseRequestMonitor


class RequestMonitor(BaseRequestMonitor):
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


app = web.Application()
app.router.add_get("/metrics", hrprometheus_view)
app.middlewares.append(hrprometheus_middleware(RequestMonitor))
```

#### Grouping dynamic routes
In aiohttp you may define dynamic routes by parametrizing the route path (e.g. `/v1/resource/{resource_id}`). If you are interested in grouping the different values for a given parameter under the same metrics you can do so by specifying the fixed parameters for a named route to the request monitor (you can do so trhough the middleware for convinience).

Here is an example of an api returning neighbouring cells from a matrix
```python
from aiohttp import web
from hr_prometheus import hrprometheus_middleware
from my_project.views import get_cell_neighbour_view

middleware = hrprometheus_middleware(fixed_routes_parameter={"get_cell_neighbour": ["cell_id"]})
app = web.Application(middlewares=[middleware])
app.add_route("GET", "/cell_neighbour/{cell_id}/direction/{direction}", get_cell_neighbour_view, name="get_cell_neighbour")
```
This way requests with path `/cell_neighbour/1948/direction/north` and `/cell_neighbour/874/direction/north` are both collapsed into `"/cell_neighbour/{cell_id}/direction/north"`

This is especially useful when you have a wide range of possible values for a path parameter and you are only interested in the overall monitoring, thus avoiding metrics namespace pollution.
