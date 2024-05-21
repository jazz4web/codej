from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse

from ..auth.cu import checkcu
from ..common.pg import get_conn
from .pg import filter_target_user


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
            await conn.close()
            return JSONResponse(res)
        await conn.close()
        return JSONResponse(res)
