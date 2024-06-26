from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse

from ..auth.cu import checkcu
from ..common.aparsers import parse_page
from ..common.pg import get_conn
from ..drafts.attri import status
from .pg import check_last, select_authors, select_authored, select_l_blog


class LBlog(HTTPEndpoint):
    async def get(self, request):
        conn = await get_conn(request.app.config)
        res = {'cu': await checkcu(
            request, conn, request.headers.get('x-auth-token'))}
        username = request.query_params.get('username')
        label = request.query_params.get('label')
        page = await parse_page(request)
        author = await conn.fetchval(
            'SELECT id FROM users WHERE username = $1', username)
        if author is None:
            res['message'] = f'Автор {username} не существует.'
            await conn.close()
            return JSONResponse(res)
        last = await check_last(
            conn, page,
            request.app.config.get('ARTS_PER_PAGE', cast=int, default=3),
            '''SELECT count(*) FROM articles, labels, als
                 WHERE articles.author_id = $1
                   AND articles.id = als.article_id
                   AND labels.label = $2
                   AND labels.id = als.label_id
                   AND articles.state IN ($3, $4, $5)''',
            author, label, status.pub, status.priv, status.ffo)
        if page > last:
            res['message'] = f'Всего страниц: {last}.'
            await conn.close()
            return JSONResponse(res)
        res['pagination'] = dict()
        await select_l_blog(
            request, conn, res['pagination'],
            author, label, page,
            request.app.config.get('ARTS_PER_PAGE', cast=int, default=3), last)
        if res['pagination']:
            if res['pagination']['next'] or res['pagination']['prev']:
                res['pv'] = True
        await conn.close()
        return JSONResponse(res)


class Blog(HTTPEndpoint):
    async def get(self, request):
        conn = await get_conn(request.app.config)
        res = {'cu': await checkcu(
            request, conn, request.headers.get('x-auth-token'))}
        page = await parse_page(request)
        username = request.query_params.get('username')
        author = await conn.fetchrow(
            'SELECT id, description FROM users WHERE username = $1', username)
        if author is None:
            res['message'] = f'Автор {username} не существует.'
            await conn.close()
            return JSONResponse(res)
        last = await check_last(
            conn, page,
            request.app.config.get('ARTS_PER_PAGE', cast=int, default=3),
            '''SELECT count(*) FROM articles
                 WHERE author_id = $1 AND state IN ($2, $3, $4)''',
            author.get('id'), status.pub, status.priv, status.ffo)
        if page > last:
            res['message'] = f'Всего страниц: {last}.'
            await conn.close()
            return JSONResponse(res)
        res['pagination'] = dict()
        await select_authored(
            request, conn, res['pagination'], author.get('id'), page,
            request.app.config.get('ARTS_PER_PAGE', cast=int, default=3), last)
        if author and author['description'] and res['pagination'] and \
                res['pagination']['page'] == 1:
            res['author'] = author.get('description')
        if res['pagination']:
            if res['pagination']['next'] or res['pagination']['prev']:
                res['pv'] = True
        await conn.close()
        return JSONResponse(res)


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
