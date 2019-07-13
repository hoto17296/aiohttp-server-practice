from aiohttp import web
from aiohttp_session import get_session

routes = web.RouteTableDef()

@routes.get('/')
async def root(request):
    session = await get_session(request)
    return web.json_response({'message': 'Hello, world!'}, status=200)