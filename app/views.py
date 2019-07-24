from aiohttp import web
from aiohttp_jinja2 import template
import app.auth as auth

routes = web.RouteTableDef()

@routes.get('/')
@auth.required
@template('index.jinja')
async def root(request):
    return {'message': 'Hello, world!'}

@routes.view('/login', name='login')
class LoginView(web.View):

    @template('login.jinja')
    async def get(self):
        if self.request['auth'].user:
            raise web.HTTPFound('/')

    @template('login.jinja')
    async def post(self):
        data = await self.request.post()
        if await self.request['auth'].login(data['id'], data['password']):
            raise web.HTTPFound('/')
        self.request.app.logger.warn('Login failed: id={} IP={}'.format(data['id'], self.request.remote))
        return {'message': 'Invalid ID or Password.'}

@routes.post('/logout', name='logout')
async def login(request):
    await request['auth'].logout()
    raise web.HTTPFound('/login')

@routes.view('/register', name='register')
class RegisterView(web.View):

    @template('register.jinja')
    async def get(self):
        if self.request['auth'].user:
            raise web.HTTPFound('/')

    @template('register.jinja')
    async def post(self):
        data = await self.request.post()
        try:
            await self.request['auth'].register(data['id'], data['password'])
        except ValueError as e:
            return {'errors': e.args}
        else:
            await self.request['auth'].login(data['id'], data['password'])
            raise web.HTTPFound('/')
