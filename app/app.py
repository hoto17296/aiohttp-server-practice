from aiohttp import web
from app.views import routes

app = web.Application()
app.add_routes(routes)