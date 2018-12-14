from aiohttp.web import middleware

from hr_prometheus.monitors import RequestMonitor


def hrprometheus_middleware(request_monitor=None):
    @middleware
    async def middleware_handler(request, handler):
        request_manager = request_monitor or RequestMonitor
        with request_manager(request) as monitor:
            response = await handler(request)
            monitor.observe(response)
            return response

    return middleware_handler
