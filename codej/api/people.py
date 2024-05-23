from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse

from ..auth.attri import groups, kgroups, weigh
from ..auth.cu import checkcu
from ..common.flashed import set_flashed
from ..common.pg import get_conn
from .pg import check_rel, filter_target_user
from .tools import check_profile_permissions


class Profile(HTTPEndpoint):
    async def get(self, request):
        conn = await get_conn(request.app.config)
        res = {'cu': await checkcu(
            request, conn, request.headers.get('x-auth-token')),
               'user': None}
        username = request.query_params.get('username')
        cu = res['cu']
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            await conn.close()
            return JSONResponse(res)
        if cu and username:
            target = await filter_target_user(request, conn, username)
            if target is None:
                res['message'] = f'{username}? Такого пользователя у нас нет.'
                await conn.close()
                return JSONResponse(res)
            res['user'] = target
            rel = await check_rel(conn, cu.get('id'), target.get('uid'))
            await check_profile_permissions(request, cu, target, rel, res)
            if res['address']:
                res['user']['address'] = await conn.fetchval(
                    'SELECT address FROM accounts WHERE user_id = $1',
                    target.get('uid'))
            await conn.close()
            return JSONResponse(res)
        await conn.close()
        return JSONResponse(res)

    async def post(self, request):
        res = {'done': None}
        d = await request.form()
        username, group, auth = (
            d.get('username'), d.get('group'), d.get('auth'))
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, auth)
        if cu.get('weight') < 200:
            res['message'] = 'У вас недостаточно прав.'
            await conn.close()
            return JSONResponse(res)
        if cu.get('username') == username:
            res['message'] = 'Действие не позволено.'
            await conn.close()
            return JSONResponse(res)
        if (cu.get('weight') < 255 and group not in kgroups) or \
                (cu.get('weight') == 255 and group not in groups):
            res['message'] = 'Недопустимая группа, действие отменено.'
            await conn.close()
            return JSONResponse()
        user = await conn.fetchrow(
            'SELECT username, ugroup FROM users WHERE username = $1',
            username)
        if user is None:
            res['message'] = 'Неизвестный пользователь, действие отменено.'
            await conn.close()
            return JSONResponse(res)
        await conn.execute(
            'UPDATE users SET ugroup = $1, weight = $2 WHERE username = $3',
            group, await weigh(group), user.get('username'))
        res['done'] = True
        await set_flashed(
            request, f'Для {user.get("username")} установлена новая группа.')
        await conn.close()
        return JSONResponse(res)
