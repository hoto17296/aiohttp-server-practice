import hashlib
from aiohttp import web
from aiohttp_session import get_session

def middleware(salt: bytes):
    @web.middleware
    async def auth_middleware(request, handler):
        session = await get_session(request)
        request['auth'] = await Auth.create(session, request.app['pg'], salt)
        return await handler(request)
    return auth_middleware

def required(func):
    async def wrapper(request, *args, **kwargs):
        if request['auth'].user is None:
            raise web.HTTPFound('/login')
        return await func(request, *args, **kwargs)
    return wrapper

def password_hash(password: str, salt: bytes) -> str:
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000).hex()

class Auth:

    def __init__(self, session, pg, salt):
        self.session = session
        self.pg = pg
        self.salt = salt
        self.user = None

    @classmethod
    async def create(cls, *args, **kwargs):
        self = cls(*args, **kwargs)
        self.user = await self.get_user()
        return self

    async def get_user(self):
        user_id = self.session.get('user_id')
        if user_id:
            return { 'id': user_id }
        else:
            return None

    async def register(self, user_id, password):
        # TODO Validation
        query = """
            INSERT
            INTO users(id, password_hash)
            VALUES ($1, $2)
            """
        res = await self.pg.execute(query, user_id, password_hash(password, self.salt))

    async def login(self, user_id, password) -> bool:
        query = """
            SELECT TRUE
            FROM users
            WHERE id = $1 AND password_hash = $2
            """
        res = bool(await self.pg.fetchval(query, user_id, password_hash(password, self.salt)))
        if res:
            self.session['user_id'] = user_id
        return res

    async def logout(self):
        self.session['user_id'] = None