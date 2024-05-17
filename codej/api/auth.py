import asyncio

from datetime import datetime

from passlib.hash import pbkdf2_sha256
from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse
from validate_email import validate_email

from ..common.flashed import set_flashed
from ..common.pg import get_conn
from .redi import extract_cache
from .pg import check_address, create_session, filter_user
from .tasks import change_pattern, rem_old_session, request_passwd
from .tokens import check_token, create_login_token
from .tools import fix_bad_token

BADCAPTCHA = 'Тест провален, либо устарел, попробуйте снова.'


class ResetPasswd(HTTPEndpoint):
    async def get(self, request):
        res = {'aid': None}
        token = request.headers.get('x-reg-token')
        acc = await check_token(request.app.config, token)
        if acc is None:
            res['message'] = await fix_bad_token(request.app.config)
            return JSONResponse(res)
        conn = await get_conn(request.app.config)
        acc = await conn.fetchrow(
            '''SELECT accounts.id, accounts.user_id, accounts.requested,
                      accounts.swap, users.username, users.last_visit
                 FROM accounts, users
                 WHERE accounts.id = $1 AND accounts.user_id = users.id''',
            acc.get('aid'))
        await conn.close()
        if acc is None or acc.get('user_id') is None \
                or acc.get('last_visit') > acc.get('requested') \
                or acc.get('swap'):
            res['message'] = 'Действие невозможно, брелок под сомнением.'
            return JSONResponse(res)
        res['aid'] = acc.get('id')
        res['username'] = acc.get('username')
        return JSONResponse(res)

    async def post(self, request):
        res = {'done': None}
        d = await request.form()
        address, passwd, confirma, aid = (
            d.get('address'), d.get('passwd'),
            d.get('confirma'), d.get('aid'))
        if not all((address, passwd, confirma, aid)):
            res['message'] = 'Нужно заполнить все поля формы.'
            return JSONResponse(res)
        if passwd != confirma:
            res['message'] = 'Пароли не совпадают.'
            return JSONResponse(res)
        conn = await get_conn(request.app.config)
        acc = await conn.fetchrow(
            '''SELECT a.id, a.address, a.user_id, u.username
                 FROM accounts AS a, users AS u
                 WHERE a.user_id = u.id AND a.id = $1''', int(aid))
        if acc.get('address') != address or acc.get('user_id') is None:
            res['message'] = 'Действие невозможно, неверный запрос.'
            await conn.close()
            return JSONResponse(res)
        await conn.execute(
            '''UPDATE users SET password_hash = $1, last_visit = $2
                 WHERE id = $3''',
            pbkdf2_sha256.hash(passwd), datetime.utcnow(), acc.get('user_id'))
        res['done'] = True
        await conn.close()
        await set_flashed(
            request, f'Уважаемый {acc.get("username")}, у Вас новый пароль.')
        return JSONResponse(res)


class GetPasswd(HTTPEndpoint):
    async def post(self, request):
        res = {'done': False}
        d = await request.form()
        address, cache, captcha = (
            d.get('address'), d.get('cache'), d.get('captcha'))
        if not cache:
            res['message'] = BADCAPTCHA
            return JSONResponse(res)
        suffix, val = await extract_cache(request, cache)
        if captcha != val:
            res['message'] = BADCAPTCHA
            asyncio.ensure_future(
                change_pattern(request.app.config, suffix))
            return JSONResponse(res)
        if not validate_email(address):
            res['message'] = 'Нужно ввести адрес электронной почты.'
            return JSONResponse(res)
        conn = await get_conn(request.app.config)
        message, account = await check_address(request, conn, address)
        await conn.close()
        if message:
            res['message'] = message
            asyncio.ensure_future(
                change_pattern(request.app.config, suffix))
            return JSONResponse(res)
        res['done'] = True
        asyncio.ensure_future(
            change_pattern(request.app.config, suffix))
        asyncio.ensure_future(
            request_passwd(request, account, address))
        await set_flashed(
            request, 'На ваш адрес выслано письмо с инструкциями.')
        return JSONResponse(res)


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
