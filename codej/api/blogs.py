from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse

from ..auth.cu import checkcu
from ..common.aparsers import parse_page
from ..common.pg import get_conn
from .pg import check_last, select_authors


class Authors(HTTPEndpoint):
    async def get(self, request):
        conn = await get_conn(request.app.config)
        res = {'cu': await checkcu(
            request, conn, request.headers.get('x-auth-token'))}
        cu = res['cu']
        page = await parse_page(request)
        last = await check_last(
            conn, page,
            request.app.config.get('ARTS_PER_PAGE', cast=int, default=3),
            '''SELECT count(*) FROM users
                 WHERE last_published IS NOT null
                   AND description IS NOT null''')
        if page > last:
            res['message'] = f'Всего страниц: {last}.'
            await conn.close()
            return JSONResponse(res)
        res['pagination'] = dict()
        await select_authors(
            request, conn, res['pagination'],
            page, request.app.config.get('ARTS_PER_PAGE', cast=int, default=3),
            last)
        if res['pagination']:
            if res['pagination']['next'] or res['pagination']['prev']:
                res['pv'] = True
        await conn.close()
        return JSONResponse(res)
