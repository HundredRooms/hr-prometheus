from aiohttp.web import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest


async def hrprometheus_view(request):
    resp = Response(body=generate_latest())
    resp.content_type = CONTENT_TYPE_LATEST
    return resp
