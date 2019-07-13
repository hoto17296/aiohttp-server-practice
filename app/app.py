import os
from aiohttp import web
from app.views import routes
import asyncpg

async def startup(app: web.Application):
    app['pg'] = await asyncpg.create_pool(dsn=os.environ.get('DATABASE_URL'))

async def cleanup(app: web.Application):
    await app['pg'].close()

app = web.Application()
app.add_routes(routes)
app.on_startup.append(startup)
app.on_cleanup.append(cleanup)