from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse

from ..auth.cu import checkcu
from ..common.flashed import set_flashed
from ..common.pg import get_conn
from .pg import check_art, check_rel, select_commentaries, send_comment


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
