import asyncio
import functools

from datetime import datetime

from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse

from ..auth.cu import checkcu
from ..common.aparsers import parse_page
from ..common.flashed import set_flashed
from ..common.pg import get_conn
from ..common.random import get_unique_s
from .md import html_ann
from .pg import check_ann, check_last, select_announces, select_broadcast


class Broadcast(HTTPEndpoint):
    async def get(self, request):
        res = {'anns': None}
        suffix = request.query_params.get('suffix')
        if suffix:
            conn = await get_conn(request.app.config)
            art = await conn.fetchval(
                'SELECT author_id FROM articles WHERE suffix = $1', suffix)
            if art:
                res['anns'] = await select_broadcast(conn, art)
            await conn.close()
        return JSONResponse(res)


class Announce(HTTPEndpoint):
    async def delete(self, request):
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
        target = await conn.fetchrow(
            '''SELECT suffix FROM announces
                 WHERE suffix = $1 AND author_id = $2''',
            d.get('suffix', ''), cu.get('id'))
        if target is None:
            res['message'] = 'Ничего не найдено по запросу.'
            await conn.close()
            return JSONResponse(res)
        await conn.execute(
            'DELETE FROM announces WHERE suffix = $1 AND author_id = $2',
            d.get('suffix', ''), cu.get('id'))
        await conn.close()
        res['done'] = True
        res['redirect'] = request.url_for('announces:announces')._url
        await set_flashed(request, 'Объявление удалено.')
        return JSONResponse(res)

    async def get(self, request):
        conn = await get_conn(request.app.config)
        res = {'cu': await checkcu(
            request, conn, request.headers.get('x-auth-token')),
               'suffix': request.query_params.get('suffix', ''),
               'announce': None}
        cu = res['cu']
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            await conn.close()
            return JSONResponse(res)
        if cu.get('weight') < 100:
            res['message'] = 'Доступ ограничен, у вас недостаточно прав.'
            await conn.close()
            return JSONResponse(res)
        target = dict()
        await check_ann(conn, res.get('suffix'), cu.get('id'), target)
        await conn.close()
        if not target:
            res['message'] = 'Ничего не найдено по запросу.'
            return JSONResponse(res)
        res['announce'] = target
        return JSONResponse(res)

    async def put(self, request):
        res = {'done': None}
        d = await request.form()
        field, value, suffix = (
            d.get('field', ''), d.get('value', ''), d.get('suffix', ''))
        if not all((field, value, suffix)):
            res['message'] = 'Запрос содержит неверные параметры.'
            return JSONResponse(res)
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
        target = await conn.fetchrow(
            '''SELECT suffix, pub FROM announces
                 WHERE suffix = $1 AND author_id = $2''', suffix, cu.get('id'))
        if target is None:
            res['message'] = 'Ничего не найдено по запросу.'
            await conn.close()
            return JSONResponse(res)
        if field == 'pub':
            if target.get('pub'):
                message = 'Объявление скрыто.'
            else:
                message = 'Объявление опубликовано.'
            await conn.execute(
                '''UPDATE announces SET published = $1, pub = $2
                     WHERE suffix = $3''',
                datetime.utcnow(), not target.get('pub'), suffix)
            await conn.close()
            res['done'] = True
            await set_flashed(request, message)
            return JSONResponse(res)
        if field == 'headline':
            if len(value) > 50:
                res['message'] = 'Запрос содержит неверные параметры.'
                await conn.close()
                return JSONResponse(res)
            await conn.execute(
                'UPDATE announces SET headline = $1 WHERE suffix = $2',
                value, suffix)
            await conn.close()
            res['done'] = True
            await set_flashed(request, 'Заголовок объявления изменён.')
            return JSONResponse(res)
        if field == 'body':
            if len(value) > 1024:
                res['message'] = 'Запрос содержит неверные параметры.'
                await conn.close()
                return JSONResponse(res)
            loop = asyncio.get_running_loop()
            html = await loop.run_in_executor(
                None, functools.partial(html_ann, value))
            await conn.execute(
                'UPDATE announces SET body = $1, html = $2 WHERE suffix = $3',
                value, html, suffix)
            await conn.close()
            res['done'] = True
            await set_flashed(request, 'Текст объявления изменён.')
            return JSONResponse(res)
        await conn.close()
        res['message'] = 'Запрос содержит неверные параметры.'
        return JSONResponse(res)


class Announces(HTTPEndpoint):
    async def get(self, request):
        conn = await get_conn(request.app.config)
        res = {'cu': await checkcu(
            request, conn, request.headers.get('x-auth-token'))}
        cu = res['cu']
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            await conn.close()
            return JSONResponse(res)
        if cu.get('weight') < 100:
            res['message'] = 'Доступ ограничен, у вас недостаточно прав.'
            await conn.close()
            return JSONResponse(res)
        page = await parse_page(request)
        last = await check_last(
            conn, page,
            request.app.config.get('ANNS_PER_PAGE', cast=int, default=3),
            'SELECT count(*) FROM announces WHERE author_id = $1',
            cu.get('id'))
        if page > last:
            res['message'] = f'Всего страниц: {last}.'
            await conn.close()
            return JSONResponse(res)
        res['pagination'] = dict()
        await select_announces(
            conn, cu.get('id'), res['pagination'], page,
            request.app.config.get('ANNS_PER_PAGE', cast=int, default=3), last)
        res['extra'] = not res['pagination'] or \
                (res['pagination'] and res['pagination']['page'] == 1)
        if res['pagination']:
            if res['pagination']['next'] or res['pagination']['prev']:
                res['pv'] = True
        await conn.close()
        return JSONResponse(res)

    async def post(self, request):
        res = {'announce': None}
        d = await request.form()
        title, text, heap = (
            d.get('title', ''), d.get('text', ''), int(d.get('heap', '0')))
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
        if not all((title, text)) or len(title) > 50 or len(text) > 1024:
            res['message'] = 'Запрос содержит неверные параметры.'
            await conn.close()
            return JSONResponse(res)
        loop = asyncio.get_running_loop()
        html = await loop.run_in_executor(
            None, functools.partial(html_ann, text))
        suffix = await get_unique_s(conn, 'announces', 6)
        await conn.execute(
            '''INSERT INTO announces (headline, body, html, suffix, pub,
                                      adm, published, author_id)
                 VALUES ($1, $2, $3, $4, $5, $6, $7, $8)''',
            title, text, html, suffix, bool(heap),
            cu.get('weight') == 255, datetime.utcnow(), cu.get('id'))
        await conn.close()
        res['announce'] = request.url_for(
            'announces:announce', suffix=suffix)._url
        mes = 'Новое объявление создано.'
        if heap:
            mes = 'Новое объявление создано и опубликовано.'
        await set_flashed(request, mes)
        return JSONResponse(res)
