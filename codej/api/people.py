from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse

from ..auth.attri import groups, kgroups, weigh
from ..auth.cu import checkcu
from ..common.aparsers import parse_page
from ..common.flashed import set_flashed
from ..common.pg import get_conn
from .pg import check_last, check_rel, filter_target_user, select_users
from .tools import check_profile_permissions


class Relation(HTTPEndpoint):
    async def post(self, request):
        res = {'done': None}
        d = await request.form()
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, d.get('auth'))
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            await conn.close()
            return JSONResponse(res)
        if cu.get('weight') < 100:
            res['message'] = 'Доступ ограниен, у вас недостаточно прав.'
            await conn.close()
            return JSONResponse(res)
        target = await conn.fetchrow(
            'SELECT id, username FROM users WHERE id = $1',
            int(d.get('uid', '0')))
        if target is None:
            res['message'] = 'Запрос содержит неверные данные.'
            await conn.close()
            return JSONResponse(res)
        rel = await check_rel(conn, cu.get('id'), target.get('id'))
        if rel['friend']:
            await conn.execute(
                'DELETE FROM friends WHERE author_id = $1 AND friend_id = $2',
                cu.get('id'), target.get('id'))
            await set_flashed(
                request, f'{target.get("username")} удалён из списка друзей.')
        else:
            message = None
            if rel['blocker']:
                message = '{0} заблокирован, действие отменено.'.format(
                    target.get('username'))
            if rel['blocked']:
                message = '{0} заблокировал вас, действие отменено.'.format(
                    target.get('username'))
            if rel['blocker'] or rel['blocked']:
                res['message'] = message
                await conn.close()
                return JSONResponse(res)
            else:
                await conn.execute(
                    '''INSERT INTO friends (author_id, friend_id)
                         VALUES ($1, $2)''', cu.get('id'), target.get('id'))
                await set_flashed(
                    request,
                    f'{target.get("username")} добавлен в список друзей.')
        res['done'] = True
        await conn.close()
        return JSONResponse(res)

    async def put(self, request):
        res = {'done': None}
        d = await request.form()
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, d.get('auth'))
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            await conn.close()
            return JSONResponse(res)
        target = await conn.fetchrow(
            'SELECT id, username, weight FROM users WHERE id = $1',
            int(d.get('uid', '0')))
        if target is None:
            res['message'] = 'Запрос содержит неверные данные.'
            await conn.close()
            return JSONResponse(res)
        if cu.get('weight') >= 250 or target.get('weight') >= 250:
            res['message'] = 'Вам недоступно это действие.'
            await conn.close()
            return JSONResponse(res)
        rel = await check_rel(conn, cu.get('id'), target.get('id'))
        if rel['friend']:
            res['message'] = 'Вы не можете блокировать друзей.'
            await conn.close()
            return JSONResponse(res)
        if rel['blocker']:
            await conn.execute(
                '''DELETE FROM blockers
                     WHERE target_id = $1 AND blocker_id = $2''',
                target.get('id'), cu.get('id'))
            await set_flashed(request, 'Блокировка снята.')
        else:
            await conn.execute(
                '''INSERT INTO blockers (target_id, blocker_id)
                     VALUES ($1, $2)''', target.get('id'), cu.get('id'))
            if await conn.fetchrow(
                    '''SELECT * FROM followers
                         WHERE author_id = $1 AND follower_id = $2''',
                    cu.get('id'), target.get('id')):
                await conn.execute(
                    '''DELETE FROM followers
                         WHERE author_id = $1 AND follower_id = $2''',
                    cu.get('id'), target.get('id'))
            if await conn.fetchrow(
                    '''SELECT * FROM friends
                         WHERE author_id = $1 AND friend_id = $2''',
                    target.get('id'), cu.get('id')):
                await conn.execute(
                    '''DELETE FROM friends
                         WHERE author_id = $1 AND friend_id = $2''',
                    target.get('id'), cu.get('id'))
            await set_flashed(
                request, f'{target.get("username")} заблокирован.')
        await conn.close()
        res['done'] = True
        return JSONResponse(res)


class People(HTTPEndpoint):
    async def get(self, request):
        conn = await get_conn(request.app.config)
        res = {'cu': await checkcu(
            request, conn, request.headers.get('x-auth-token'))}
        cu = res['cu']
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            await conn.close()
            return JSONResponse(res)
        page = await parse_page(request)
        last = await check_last(
            conn, page,
            request.app.config.get('ARTS_PER_PAGE', cast=int, default=3),
            'SELECT count(*) FROM users WHERE id != $1', cu.get('id'))
        if page > last:
            res['message'] = f'Всего страниц: {last}.'
            await conn.close()
            return JSONResponse(res)
        res['pagination'] = dict()
        is_admin = cu.get('weight') == 255
        await select_users(
            request, conn, cu.get('id'), is_admin, res['pagination'], page,
            request.app.config.get('ARTS_PER_PAGE', cast=int, default=3), last)
        if res['pagination'] and \
                (res['pagination']['next'] or res['pagination']['prev']):
            res['pv'] = True
        await conn.close()
        return JSONResponse(res)


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

    async def put(self, request):
        res = {'done': None}
        d = await request.form()
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, d.get('auth'))
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            await conn.close()
            return JSONResponse(res)
        if cu.get('weight') < 100:
            res['message'] = 'Доступ ограничен, у вас недостаточно прав.'
            await conn.close()
            return JSONResponse(res)
        text = d.get('text')
        if text:
            await conn.execute(
                'UPDATE users SET description = $1 WHERE id = $2',
                text.strip()[:500], cu.get('id'))
        else:
            await conn.execute(
                'UPDATE users SET description = $1 WHERE id = $2',
                None, cu.get('id'))
        await conn.close()
        res['done'] = True
        await set_flashed(request, 'Описание блога обновлено.')
        return JSONResponse(res)
