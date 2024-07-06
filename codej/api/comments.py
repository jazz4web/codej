from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse

from ..auth.cu import checkcu
from ..common.aparsers import parse_page
from ..common.flashed import set_flashed
from ..common.pg import get_conn
from .pg import (
    can_remove, check_art, check_last, check_rel, delete_commentary,
    select_commentaries, select_comments, send_comment)


class Comments(HTTPEndpoint):
    async def get(self, request):
        conn = await get_conn(request.app.config)
        res = {'cu': await checkcu(
            request, conn, request.headers.get('x-auth-token'))}
        cu = res['cu']
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            await conn.close()
            return JSONResponse(res)
        if cu.get('weight') < 200:
            res['message'] = 'Доступ ограничен, у вас недостаточно прав.'
            await conn.close()
            return JSONResponse(res)
        page = await parse_page(request)
        last = await check_last(
            conn, page,
            request.app.config.get('COMMENTS_PER_PAGE', cast=int, default=3),
            '''SELECT count(*) FROM commentaries
                 WHERE article_id IS NOT NULL
                   AND admined = false
                   AND author_id IS NOT NULL''')
        if page > last:
            res['message'] = f'Всего страниц: {last}.'
            await conn.close()
            return JSONResponse(res)
        res['pagination'] = dict()
        await select_comments(
            request, conn, res['pagination'], page,
            request.app.config.get('COMMENTS_PER_PAGE', cast=int, default=3),
            last)
        if res['pagination']:
            if res['pagination']['next'] or res['pagination']['prev']:
                res['pv'] = True
        await conn.close()
        return JSONResponse(res)


class Answer(HTTPEndpoint):
    async def post(self, request):
        res = {'perm': None}
        d = await request.form()
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, d.get('auth'))
        if cu is None:
            res['message'] = 'Нужно зарегистрироваться и авторизоваться.'
            await conn.close()
            return JSONResponse(res)
        if cu.get('weight') < 45:
            res['message'] = 'Вам закрыта возможность оставить комментарий.'
            await conn.close()
            return JSONResponse(res)
        parent = await conn.fetchrow(
            '''SELECT c.id, c.author_id AS cauthor, a.author_id AS artauthor
                 FROM articles AS a, commentaries AS c
                 WHERE c.id = $1
                   AND a.id = c.article_id''', int(d.get('cid', '0')))
        if parent is None:
            res['message'] = 'Запрос содержит неверные параметры.'
            await conn.close()
            return JSONResponse(res)
        artrel = await check_rel(conn, parent.get('artauthor'), cu.get('id'))
        if artrel['blocker'] or artrel['blocked']:
            res['message'] = 'Вы не можете комментировать в этом блоге.'
            await conn.close()
            return JSONResponse(res)
        commrel = await check_rel(conn, parent.get('cauthor'), cu.get('id'))
        if commrel['blocker'] or commrel['blocked']:
            res['message'] = 'Вы не можете ответить на этот комментарий.'
            await conn.close()
            return JSONResponse(res)
        res['perm'] = True
        res['parent_id'] = parent.get('id')
        await conn.close()
        return JSONResponse(res)

    async def put(self, request):
        res = {'done': None}
        d = await request.form()
        text = d.get('text', '')
        if not text or len(text) > 25000:
            res['message'] = 'Текст запроса не соответствует критериям.'
            return JSONResponse(res)
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, d.get('auth'))
        if cu is None:
            res['message'] = 'Нужно зарегистрироваться и авторизоваться.'
            await conn.close()
            return JSONResponse(res)
        if cu.get('weight') < 45:
            res['message'] = 'Вам закрыта возможность оставить комментарий.'
            await conn.close()
            return JSONResponse(res)
        parent = await conn.fetchrow(
            '''SELECT c.id, c.author_id AS cauthor,
                      a.author_id AS artauthor, a.id AS artid
                 FROM articles AS a, commentaries AS c
                 WHERE c.id = $1
                   AND a.slug = $2
                   AND a.id = c.article_id''',
            int(d.get('pid', '0')), d.get('slug', ''))
        if parent is None:
            res['message'] = 'Запрос содержит неверные параметры.'
            await conn.close()
            return JSONResponse(res)
        artrel = await check_rel(conn, parent.get('artauthor'), cu.get('id'))
        if artrel['blocker'] or artrel['blocked']:
            res['message'] = 'Вы не можете комментировать в этом блоге.'
            await conn.close()
            return JSONResponse(res)
        commrel = await check_rel(conn, parent.get('cauthor'), cu.get('id'))
        if commrel['blocker'] or commrel['blocked']:
            res['message'] = 'Вы не можете ответить на этот комментарий.'
            await conn.close()
            return JSONResponse(res)
        await send_comment(
            conn, text, cu.get('id'), parent.get('artid'), parent.get('id'))
        res['done'] = True
        await set_flashed(request, 'Комментарий добавлен.')
        await conn.close()
        return JSONResponse(res)


class Comment(HTTPEndpoint):
    async def delete(self, request):
        res = {'done': None}
        d = await request.form()
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, d.get('auth'))
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            await conn.close()
            return JSONResponse(res)
        if cu.get('weight') < 45:
            res['message'] = 'У вас нет права удалять комментарии.'
            await conn.close()
            return JSONResponse(res)
        co = await conn.fetchrow(
            '''SELECT id, author_id, article_id, parent_id FROM commentaries
                 WHERE id = $1''', int(d.get('cid', '0')))
        if co is None:
            res['message'] = 'Запрос содержит неверные параметры.'
            await conn.close()
            return JSONResponse(res)
        art = await conn.fetchrow(
            'SELECT commented, author_id FROM articles WHERE id = $1',
            co.get('article_id'))
        if art is None:
            res['message'] = 'Запрос содержит неверные параметры.'
            await conn.close()
            return JSONResponse(res)
        author = await conn.fetchrow(
            'SELECT id, username FROM users WHERE id = $1',
            co.get('author_id'))
        if author is None:
            res['message'] = 'Запрос содержит неверные параметры.'
            await conn.close()
            return JSONResponse(res)
        if await can_remove(art, cu, author):
            await delete_commentary(conn, co)
            res['done'] = True
            await conn.close()
            await set_flashed(request, 'Комментарий удалён.')
            return JSONResponse(res)
        res['message'] = 'Упс.., действие невозможно.'
        await conn.close()
        return JSONResponse(res)

    async def get(self, request):
        res = {'commentaries': None}
        conn = await get_conn(request.app.config)
        cu = await checkcu(
            request, conn, request.headers.get('x-auth-token'))
        slug = request.query_params.get('slug')
        art = await check_art(conn, slug)
        if art:
            res = {'commentaries': await select_commentaries(
                request, conn, art, cu)}
        await conn.close()
        return JSONResponse(res)

    async def post(self, request):
        res = {'done': None}
        d = await request.form()
        text = d.get('text', '')
        if not text or len(text) > 25000:
            res['message'] = 'Текст запроса не соответствует критериям.'
            return JSONResponse(res)
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, d.get('auth'))
        if cu is None:
            res['message'] = 'Нужно зарегистрироваться и авторизоваться.'
            await conn.close()
            return JSONResponse(res)
        if cu.get('weight') < 45:
            res['message'] = 'Вам закрыта возможность оставить комментарий.'
            await conn.close()
            return JSONRespose(res)
        art = await check_art(conn, d.get('slug', ''))
        if art is None:
            res['message'] = 'Запрос содержит неверные параметры.'
            await conn.close()
            return JSONResponse(res)
        rel = await check_rel(conn, art.get('author_id'), cu.get('id'))
        if rel['blocked'] or rel['blocker']:
            res['message'] = 'Вы не можете комментировать этот блог.'
            await conn.close()
            return JSONResponse(res)
        await send_comment(conn, text, cu.get('id'), art.get('id'), None)
        res['done'] = True
        await set_flashed(request, 'Комментарий добавлен.')
        await conn.close()
        return JSONResponse(res)

    async def put(self, request):
        res = {'done': None}
        d = await request.form()
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, d.get('auth'))
        if cu is None:
            res['message'] = 'Действие ограничено, требуется авторизация.'
            await conn.close()
            return JSONResponse(res)
        if cu.get('weight') < 200:
            res['message'] = 'Действие ограничено, у вас недостаточно прав.'
            await conn.close()
            return JSONResponse(res)
        co = await conn.fetchrow(
            '''SELECT id, admined FROM commentaries
                 WHERE id = $1
                   AND article_id IS NOT NULL
                   AND admined = false''', int(d.get('id', '0')))
        if co:
            await conn.execute(
                'UPDATE commentaries SET admined = true WHERE id = $1',
                co.get('id'))
        await conn.close()
        res['done'] = True
        await set_flashed(request, 'Комментарий проверен.')
        return JSONResponse(res)
