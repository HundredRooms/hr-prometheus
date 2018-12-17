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

Default request behaviour can be modified by passing a custom `RequestMonitor` to the middleware. You can find out how to do in advanced section.

## Installation

```shell
pip install hr-prometheus
```

## Usage

Briefly, the following is all you need to do to measure and export prometheus metrics from your aiohttp web application:

```python
from aiohttp import web
from hr-prometheus import hrprometheus_middleware, hrprometheus_view

app = web.Application()
app.router.add_get("/metrics", hrprometheus_view)
app.middlewares.append(hrprometheus_middleware())
```

### Utils

This project provides some utilities to simplify the management of metrics. For now only one is provides, a context manager and decorator to measure the execution time of some function or piece of code.

This `TimeMonitor` context decorator class accepts the `metric` to be observed and a list of `labels`.

#### Decorator example

```python
from hr-prometheus.utils import TimeMonitor

FOO_METHOD = Counter("foo_method", "Number of foo method calls", ["source"])


@TimeMonitor(metric=FOO_METHOD, labels=["label1", "label2"])
def foo():
    print foo
```

#### Context manager example

```python
from hr-prometheus.utils import TimeMonitor

FOO_CODE = Counter("foo_code", "Number of foo prints", ["source"])


class EnumLabels(Enum):
    LABEL1 = "label1"
    LABEL2 = "label2"


def foo():
    with TimeMonitor(metric=FOO_CODE, labels=[EnumLabels.LABEL1]):
        print foo
```

### Advance Usage

To modify the default behavior you simply need to create a new monitor that inherits from the `BaseRequestMonitor` and pass the class to the middleware.

This clase provides two publica methods. `update_init_metrics` and `update_end_metrics`.
These methods are executed at the beginning and end of a request respectively. Simply add the metrics you want at each point.

Here's an example taken from the default monitor.

```python
from aiohttp import web
from hr-prometheus import hrprometheus_middleware, hrprometheus_view
from hr-prometheus.monitors import BaseRequestMonitor


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
