from datetime import datetime

from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse

from ..auth.cu import checkcu
from ..common.aparsers import parse_page, parse_url
from ..common.flashed import set_flashed
from ..common.pg import get_conn
from ..common.random import get_unique_s
from .pg import check_last, select_aliases


class Aliases(HTTPEndpoint):
    async def delete(self, request):
        res = {'done': None}
        d = await request.form()
        suffix, page = d.get('suffix', ''), int(d.get('page', '0'))
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, d.get('auth'))
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            await conn.close()
            return JSONResponse(res)
        if cu.get('weight') < 55:
            res['message'] = 'Доступ ограничен, у вас недостаточно прав.'
            await conn.close()
            return JSONResponse(res)
        if page >= 2:
            url = request.url_for('aliases:aliases')._url + f'?page={page}'
        else:
            url = request.url_for('aliases:aliases')._url
        alias = await conn.fetchrow(
            'SELECT suffix FROM aliases WHERE suffix = $1 AND author_id = $2',
            suffix, cu.get('id'))
        if alias is None:
            res['message'] = 'Запрос содержит неверные параметры.'
            await conn.close()
            return JSONResponse(res)
        await conn.execute(
            'DELETE FROM aliases WHERE suffix = $1 AND author_id = $2',
            suffix, cu.get('id'))
        await conn.close()
        await set_flashed(request, 'Алиас успешно удалён.')
        res['done'] = True
        res['url'] = url
        return JSONResponse(res)

    async def get(self, request):
        conn = await get_conn(request.app.config)
        res = {'cu': await checkcu(
            request, conn, request.headers.get('x-auth-token'))}
        cu = res['cu']
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            await conn.close()
            return JSONResponse(res)
        if cu.get('weight') < 55:
            res['message'] = 'Доступ ограничен, у вас недостаточно прав.'
            await conn.close()
            return JSONResponse(res)
        page = await parse_page(request)
        last = await check_last(
            conn, page,
            request.app.config.get('ALIASES_PER_PAGE', cast=int, default=3),
            'SELECT count(*) FROM aliases WHERE author_id = $1',
            cu.get('id'))
        if page > last:
            res['message'] = f'Всего страниц: {last}.'
            await conn.close()
            return JSONResponse(res)
        res['pagination'] = dict()
        await select_aliases(
            request, conn, cu.get('id'), res['pagination'], page,
            request.app.config.get('ALIASES_PER_PAGE', cast=int, default=3),
            last)
        res['extra'] = not res['pagination'] or \
                (res['pagination'] and res['pagination']['page'] == 1)
        if res['pagination'] and \
                (res['pagination']['next'] or res['pagination']['prev']):
            res['pv'] = True
        await conn.close()
        return JSONResponse(res)

    async def post(self, request):
        res = {'done': None}
        d = await request.form()
        link = d.get('link')
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, d.get('auth'))
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            await conn.close()
            return JSONResponse(res)
        if cu.get('weight') < 55:
            res['message'] = 'Доступ ограничен, у вас недостаточно прав.'
            await conn.close()
            return JSONResponse(res)
        if not link:
            res['message'] = 'Запрос содержит неверные параметры.'
            await conn.close()
            return JSONResponse(res)
        if not link.startswith('https://') and not link.startswith('http://'):
            res['message'] = 'Поддерживаются только http/https ссылки.'
            await conn.close()
            return JSONResponse(res)
        target = await conn.fetchrow(
            '''SELECT url, created, clicked, suffix FROM aliases
                 WHERE url = $1 AND author_id = $2''', link, cu.get('id'))
        if target:
            res['done'] = True
            res['alias'] = {'url': target.get('url'),
                            'parsed': await parse_url(target.get('url')),
                            'created': f'{target.get("created").isoformat()}Z',
                            'clicked': target.get('clicked'),
                            'suffix': target.get('suffix'),
                            'alias': request.url_for(
                                'jump', suffix=target.get('suffix'))._url}
            await conn.close()
            return JSONResponse(res)
        suffix = await get_unique_s(conn, 'aliases', 6)
        await conn.execute(
            '''INSERT INTO aliases (url, created, suffix, author_id)
                 VALUES ($1, $2, $3, $4)''',
            link, datetime.utcnow(), suffix, cu.get('id'))
        res['done'] = True
        await set_flashed(request, 'Алиас для вашего URL создан.')
        await conn.close()
        return JSONResponse(res)
