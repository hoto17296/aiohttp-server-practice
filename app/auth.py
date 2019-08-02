import re
import hashlib
from logging import getLogger
from aiohttp import web
from aiohttp.abc import AbstractView
from aiohttp_session import get_session

logger = getLogger(__name__)

def middleware(salt: bytes):
    @web.middleware
    async def auth_middleware(request, handler):
        session = await get_session(request)
        request['auth'] = await Auth.create(session, request.app['pg'], salt)
        return await handler(request)
    return auth_middleware

async def jinja2_context_processor(request):
    return { 'auth': request['auth'] }

def required(func):
    async def wrapper(*args, **kwargs):
        # Supports class based views
        request = args[0].request if isinstance(args[0], AbstractView) else args[0]
        if request['auth'].user is None:
            raise web.HTTPFound('/login')
        return await func(*args, **kwargs)
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

    async def check_user_exists(self, user_id: str) -> bool:
        query = """
            SELECT TRUE
            FROM users
            WHERE id = $1
            """
        return bool(await self.pg.fetchval(query, user_id))

    async def register(self, user_id: str, password: str):
        # Validation
        errors = []
        if len(user_id) == 0:
            errors.append(('id', 'ID is empty.'))
        elif not re.match(r'^\w+$', user_id, flags=re.ASCII):
            errors.append(('id', 'ID can only contain alphabets, numbers and underscores.'))
        elif await self.check_user_exists(user_id):
            errors.append(('id', 'This ID has already taken.'))
        if len(password) == 0:
            errors.append(('password', 'Password is empty.'))
        elif len(password) < 8:
            errors.append(('password', 'Password should be at least 8 characters.'))
        elif not re.match(r'^[\x21-\x7e]+$', password):
            errors.append(('password', 'Password should be ASCII string.'))
        if len(errors) > 0:
            raise ValueError(*errors)

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
