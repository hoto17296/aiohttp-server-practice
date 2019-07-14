from aiohttp import web
from aiohttp_jinja2 import template
import app.auth as auth

routes = web.RouteTableDef()

@routes.get('/')
@auth.required
@template('index.jinja')
async def root(request):
    return {'message': 'Hello, world!'}

@routes.get('/login')
@template('login.jinja')
async def login(request):
    if request['auth'].user:
        raise web.HTTPFound('/')

@routes.post('/login')
@template('login.jinja')
async def post_login(request):
    data = await request.post()
    if await request['auth'].login(data['id'], data['password']):
        raise web.HTTPFound('/')
    return {'message': 'Invalid ID or Password.'}

@routes.get('/logout')
async def login(request):
    await request['auth'].logout()
    raise web.HTTPFound('/login')

@routes.get('/register')
@template('register.jinja')
async def register(request):
    if request['auth'].user:
        raise web.HTTPFound('/')

@routes.post('/register')
@template('register.jinja')
async def post_register(request):
    data = await request.post()
    await request['auth'].register(data['id'], data['password'])
    await request['auth'].login(data['id'], data['password'])
    raise web.HTTPFound('/')