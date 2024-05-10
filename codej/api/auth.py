import asyncio

from passlib.hash import pbkdf2_sha256
from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse

from ..common.flashed import set_flashed
from ..common.pg import get_conn
from .redi import extract_cache
from .pg import create_session, filter_user
from .tasks import change_pattern
from .tokens import create_login_token

BADCAPTCHA = 'Тест провален, либо устарел, попробуйте снова.'


class Login(HTTPEndpoint):
    async def post(self, request):
        d = await request.form()
        login, passwd, rme, cache, captcha, brkey = (
            d.get('login'), d.get('passwd'),
            int(d.get('rme')), d.get('cache'),
            d.get('captcha'), d.get('brkey'))
        res = {'token': None}
        if not cache:
            res['message'] = BADCAPTCHA
            return JSONResponse(res)
        suffix, val = await extract_cache(request, cache)
        if captcha != val:
            res['message'] = BADCAPTCHA
            asyncio.ensure_future(
                change_pattern(request.app.config, suffix))
            return JSONResponse(res)
        conn = await get_conn(request.app.config)
        user = await filter_user(conn, login)
        if user and pbkdf2_sha256.verify(
                passwd, user.get('password_hash')):
            d, now = await create_session(
                request.app.config, conn, rme, user, brkey)
            request.session['_uid'] = d
            res['token'] = await create_login_token(request, rme, d, now)
            await set_flashed(request, f'Привет, {user.get("username")}!')
            asyncio.ensure_future(
                change_pattern(request.app.config, suffix))
            # rem old session?
        else:
            res['message'] = 'Неверный логин или пароль, вход невозможен.'
            await conn.close()
            return JSONResponse(res)
        await conn.close()
        return JSONResponse(res)
