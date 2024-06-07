from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse

from ..auth.cu import checkcu
from ..common.aparsers import parse_page
from ..common.pg import get_conn
from .pg import check_last, get_user_stat, select_albums


class Albums(HTTPEndpoint):
    async def get(self, request):
        conn = await get_conn(request.app.config)
        res = {'cu': await checkcu(
            request, conn, request.headers.get('x-auth-token'))}
        cu = res['cu']
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            await conn.close()
            return JSONResponse(res)
        if cu.get('weight') < 150:
            res['message'] = 'Доступ ограничен, у вас недостаточно прав.'
            await conn.close()
            return JSONResponse(res)
        page = await parse_page(request)
        last = await check_last(
            conn, page,
            request.app.config.get('ALBUMS_PER_PAGE', cast=int, default=3),
            'SELECT count(*) FROM albums WHERE author_id = $1', cu.get('id'))
        if page > last:
            res['message'] = f'Всего страниц: {last}.'
            await conn.close()
            return JSONResponse(res)
        res['pagination'] = await select_albums(
            conn, cu.get('id'), page,
            request.app.config.get('ALBUMS_PER_PAGE', cast=int, default=3),
            last)
        res['extra'] = res['pagination'] is None or \
                (res['pagination'] and res['pagination']['page'] == 1)
        res['stat'] = await get_user_stat(conn, cu.get('id'))
        await conn.close()
        return JSONResponse(res)
