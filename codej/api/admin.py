import asyncio
import re

from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse
from validate_email import validate_email

from ..auth.attri import defaultg, dgroups, USER_PATTERN
from ..auth.cu import checkcu
from ..auth.pg import check_username, create_user
from ..common.flashed import set_flashed
from ..common.pg import get_conn
from ..drafts.attri import status


class IndexPage(HTTPEndpoint):
    async def put(self, request):
        res = {'done': None}
        d = await request.form()
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, d.get('auth'))
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            await conn.close()
            return JSONResponse(res)
        if cu.get('weight') < 255:
            res['message'] = 'Доступ ограничен, у вас недостаточно прав.'
            await conn.close()
            return JSONResponse(res)
        val = d.get('value', '')
        if val:
            d = await conn.fetchval(
                '''SELECT suffix FROM articles
                     WHERE suffix = $1 AND author_id = $2 AND state = $3''',
                val, cu.get('id'), status.draft)
            if d:
                await conn.execute('UPDATE settings SET indexpage = $1', d)
            else:
                res['message'] = 'Ничего не найдено по суффиксу.'
                await conn.close()
                return JSONResponse(res)
        else:
            await conn.execute('UPDATE settings SET indexpage = NULL')
        await conn.close()
        res['done'] = True
        return JSONResponse(res)


class Robots(HTTPEndpoint):
    async def put(self, request):
        res = {'done': None}
        d = await request.form()
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, d.get('auth'))
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            await conn.close()
            return JSONResponse(res)
        if cu.get('weight') < 255:
            res['message'] = 'Доступ ограничен, у вас недостаточно прав.'
            await conn.close()
            return JSONResponse(res)
        val = d.get('value', '')
        await conn.execute('UPDATE settings SET robots=$1', val or None)
        res['done'] = True
        await conn.close()
        return JSONResponse(res)


class DGroup(HTTPEndpoint):
    async def put(self, request):
        res = {'done': None}
        d = await request.form()
        dgroup = d.get('dgroup', '')
        if dgroup not in dgroups:
            res['message'] = 'Запрос содержит неверные параметры.'
            return JSONResponse(res)
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, d.get('auth'))
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            await conn.close()
            return JSONResponse(res)
        if cu.get('weight') < 255:
            res['message'] = 'Доступ ограничен, у вас недостаточно прав.'
            await conn.close()
            return JSONResponse(res)
        await conn.execute('UPDATE settings SET dgroup = $1', dgroup)
        await conn.close()
        res['done'] = True
        await set_flashed(request, 'Группа по-умолчанию изменена.')
        return JSONResponse(res)


class Admin(HTTPEndpoint):
    async def get(self, request):
        conn = await get_conn(request.app.config)
        res = {'cu': await checkcu(
            request, conn, request.headers.get('x-auth-token'))}
        cu = res['cu']
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            await conn.close()
            return JSONResponse(res)
        if cu.get('weight') < 255:
            res['message'] = 'Доступ ограничен, у вас недостаточно прав.'
            await conn.close()
            return JSONResponse(res)
        res['groups'] = dgroups
        res['dgroup'] = await conn.fetchval(
            'SELECT dgroup FROM settings') or defaultg
        res['robots'] = await conn.fetchval('SELECT robots FROM settings') or \
            request.app.jinja.get_template(
                'main/robots.txt').render(request=request)
        res['index'] = await conn.fetchval('SELECT indexpage FROM settings')
        await conn.close()
        return JSONResponse(res)

    async def post(self, request):
        res = {'done': None}
        d = await request.form()
        username, address, password, confirma = (
            d.get('username'), d.get('address'),
            d.get('password'), d.get('confirma'))
        if not all((username, address, password, confirma)):
            res['message'] = 'Нужно заполнить все поля формы.'
            return JSONResponse(res)
        if not validate_email(address):
            res['message'] = 'Нужно ввести адрес электронной почты.'
            return JSONResponse(res)
        if password != confirma:
            res['message'] = 'Пароли не совпадают.'
            return JSONResponse(res)
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, d.get('auth'))
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            await conn.close()
            return JSONResponse(res)
        if cu.get('weight') < 255:
            res['message'] = 'Доступ ограничен, у вас недостаточно прав.'
            await conn.close()
            return JSONResponse(res)
        p = re.compile(USER_PATTERN)
        if not p.match(username):
            res['message'] = 'Псевдоним не удовлетворяет требованиям сервиса.'
            await conn.close()
            return JSONResponse(res)
        if await check_username(request.app.config, username):
            res['message'] = f'Псеводним {username} уже зарегистрирован.'
            await conn.close()
            return JSONResponse(res)
        acc = await conn.fetchval(
            'SELECT user_id FROM accounts WHERE address = $1', address)
        swapped = await conn.fetchval(
            'SELECT swap FROM accounts WHERE swap = $1', address)
        if acc or swapped:
            res['message'] = f'Адрес {address} уже используется.'
            await conn.close()
            return JSONResponse(res)
        dg = await conn.fetchval(
            'SELECT dgroup FROM settings') or defaultg
        await conn.close()
        asyncio.ensure_future(
            create_user(request.app.config, username, address, password, dg))
        res['redirect'] = request.url_for(
            'people:profile', username=username)._url
        res['done'] = True
        await set_flashed(request, f'Аккаунт {username} успешно создан.')
        return JSONResponse(res)
