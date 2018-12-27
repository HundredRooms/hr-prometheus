import pytest
from aiohttp import web
from hr_prometheus.middleware import hrprometheus_middleware
from hr_prometheus.view import hrprometheus_view


@pytest.fixture
def client(loop, aiohttp_client):
    async def ping(request):
        return web.json_response("pong")

    app = web.Application()
    app.router.add_get("/ping", ping)
    app.router.add_get("/metrics", hrprometheus_view)
    app.middlewares.append(hrprometheus_middleware())
    return loop.run_until_complete(aiohttp_client(app))
