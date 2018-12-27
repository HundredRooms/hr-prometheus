from aiohttp.web import middleware

from hr_prometheus.monitors import RequestMonitor


def hrprometheus_middleware(request_monitor=None, **monitor_args):
    @middleware
    async def middleware_handler(request, handler):
        request_manager = request_monitor or RequestMonitor
        with request_manager(request, **monitor_args) as monitor:
            response = await handler(request)
            monitor.observe(response)
            return response

    return middleware_handler
