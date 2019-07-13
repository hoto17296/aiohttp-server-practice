from aiohttp import web

routes = web.RouteTableDef()

@routes.get('/')
async def root(request):
    return web.json_response({'message': 'Hello, world!'}, status=200)