import os
import uvloop
from aiohttp import web
from aiohttp_session import session_middleware
from aiohttp_session.cookie_storage import EncryptedCookieStorage
import aiohttp_jinja2
import jinja2
import asyncpg
from app.views import routes
import app.auth as auth

uvloop.install()

async def startup(app: web.Application):
    app['pg'] = await asyncpg.create_pool(dsn=os.environ.get('DATABASE_URL'))

async def cleanup(app: web.Application):
    await app['pg'].close()

app = web.Application(middlewares=[
    session_middleware(EncryptedCookieStorage(os.environ.get('SESSION_SECRET'))),
    auth.middleware(os.environ.get('AUTH_SALT').encode()),
])

app['name'] = 'AIOHTTP Server Practice'

app['static_root_url'] = os.environ.get('STATIC_ROOT_URL')

aiohttp_jinja2.setup(
    app,
    context_processors=[auth.jinja2_context_processor],
    loader=jinja2.FileSystemLoader('./app/templates')
)

app.add_routes(routes)

app.on_startup.append(startup)
app.on_cleanup.append(cleanup)