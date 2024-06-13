from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse

from ..common.pg import get_conn


class Art(HTTPEndpoint):
    async def put(self, request):
        res = {'done': None}
        d = await request.form()
        field, suffix = d.get('field', ''), d.get('suffix', 'empty')
        if field == 'viewed':
            conn = await get_conn(request.app.config)
            art = await conn.fetchrow(
                'SELECT suffix, viewed FROM articles WHERE suffix = $1',
                suffix)
            if art:
                await conn.execute(
                    'UPDATE articles SET viewed = $1 WHERE suffix = $2',
                    art.get('viewed') + 1, suffix)
            await conn.close()
            res['done'] = True
            res['views'] = art.get('viewed') + 1
        return JSONResponse(res)
