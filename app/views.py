from aiohttp import web
from aiohttp_session import get_session
from aiohttp_jinja2 import template

routes = web.RouteTableDef()

@routes.get('/')
@template('index.jinja')
async def root(request):
    session = await get_session(request)
    return {'message': 'Hello, world!'}