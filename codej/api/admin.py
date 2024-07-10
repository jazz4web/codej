from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse

from ..auth.attri import defaultg, dgroups
from ..auth.cu import checkcu
from ..common.flashed import set_flashed
from ..common.pg import get_conn


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
        await conn.close()
        return JSONResponse(res)
