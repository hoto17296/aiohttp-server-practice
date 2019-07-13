import os
from aiohttp import web
from aiohttp_session import session_middleware
from aiohttp_session.cookie_storage import EncryptedCookieStorage
import asyncpg
from app.views import routes

async def startup(app: web.Application):
    app['pg'] = await asyncpg.create_pool(dsn=os.environ.get('DATABASE_URL'))

async def cleanup(app: web.Application):
    await app['pg'].close()

app = web.Application(middlewares=[
    session_middleware(EncryptedCookieStorage(os.environ.get('SESSION_SECRET'))),
])
app.add_routes(routes)
app.on_startup.append(startup)
app.on_cleanup.append(cleanup)