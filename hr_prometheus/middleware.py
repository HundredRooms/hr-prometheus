from aiohttp.web import middleware

from hr_prometheus.request_monitor import RequestMonitor


def hrprometheus_middleware(request_monitor=None):
    @middleware
    async def middleware_handler(request, handler):
        request_monitor = request_monitor or RequestMonitor(request)
        with request_monitor(request) as monitor:
            response = await handler(request)
            monitor.observe(response)
            return response

    return middleware_handler
