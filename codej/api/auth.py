import asyncio

from passlib.hash import pbkdf2_sha256
from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse

from ..common.flashed import set_flashed
from ..common.pg import get_conn
from .redi import extract_cache
from .pg import create_session, filter_user
from .tasks import change_pattern, rem_old_session
from .tokens import check_token, create_login_token

BADCAPTCHA = 'Тест провален, либо устарел, попробуйте снова.'


class LogoutAll(HTTPEndpoint):
    async def delete(self, request):
        res = {'result': None}
        token = (await request.form()).get('token')
        if token:
            cache = await check_token(request.app.config, token)
            if cache:
                cache = cache.get('cache')
                if request.session.get('_uid') == cache:
                    conn = await get_conn(request.app.config)
                    user = await conn.fetchrow(
                        '''SELECT users.id, users.username
                             FROM users, sessions
                             WHERE sessions.suffix = $1
                               AND sessions.user_id = users.id''', cache)
                    await conn.execute(
                        'DELETE FROM sessions WHERE user_id = $1',
                        user.get('id'))
                    await conn.close()
                    request.session.pop('_uid')
                    await set_flashed(
                        request, f'Пока, {user.get("username")}!')
                    res['result'] = True
        return JSONResponse(res)


class Logout(HTTPEndpoint):
    async def delete(self, request):
        res = {'result': None}
        token = (await request.form()).get('token')
        if token:
            cache = await check_token(request.app.config, token)
            if cache:
                cache = cache.get('cache')
                if request.session.get('_uid') == cache:
                    conn = await get_conn(request.app.config)
                    username = await conn.fetchval(
                        '''SELECT users.username FROM users, sessions
                             WHERE sessions.suffix = $1
                               AND sessions.user_id = users.id''', cache)
                    await conn.execute(
                        'DELETE FROM sessions WHERE suffix = $1', cache)
                    await conn.close()
                    request.session.pop('_uid')
                    await set_flashed(request, f'Пока, {username}!')
                    res['result'] = True
        return JSONResponse(res)


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
            asyncio.ensure_future(
                rem_old_session(request.app.config, user.get('id')))
        else:
            res['message'] = 'Неверный логин или пароль, вход невозможен.'
            await conn.close()
            return JSONResponse(res)
        await conn.close()
        return JSONResponse(res)
