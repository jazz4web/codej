from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse

from ..auth.attri import groups
from ..auth.cu import checkcu
from ..common.pg import get_conn
from ..drafts.attri import status
from .pg import check_article, check_rel


class Art(HTTPEndpoint):
    async def get(self, request):
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, request.headers.get('x-auth-token'))
        res = {'art': None,
               'cu': cu}
        slug = request.query_params.get('slug', '')
        art = dict()
        await check_article(request, conn, slug, art)
        if not art:
            res['message'] = 'Ничего не найдено по запросу, проверьте ссылку.'
            await conn.close()
            return JSONRespose(res)
        if art.get('state') in (status.priv, status.ffo) and cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            await conn.close()
            return JSONResponse(res)
        if cu:
            res['own'] = cu.get('id') == art.get('author_id')
            res['cens'] = (cu.get('weight') == 255 and
                           art.get('weight') < 255) or \
                          (cu.get('weight') == 250 and
                           art.get('weight') < 200 and not res['own'])
            res['admin'] = cu.get('weight') == 255
            rel = await check_rel(
                conn, art.get('author_id'), cu.get('id'))
            if art.get('state') == status.ffo and not rel['friend'] and\
                    cu.get('weight') < 255 and \
                    not res['own']:
                res['message'] = 'Доступ ограничен, топик для друзей автора.'
                await conn.close()
                return JSONResponse(res)
            res['follow'] = not rel['follower'] and not rel['blocker'] \
                    and not rel['blocked'] and \
                    not res['own']
            res['like'] = not res['own']
            res['dislike'] = cu.get('weight') > 45 and \
                    not res['own'] and \
                    not rel['blocker'] and not rel['blocked'] and \
                    art.get('weight') < 255
            res['follower'] = rel['follower']
        res['art'] = art
        await conn.close()
        return JSONResponse(res)

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
