from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse

from ..auth.attri import groups
from ..auth.cu import checkcu
from ..common.aparsers import parse_page
from ..common.flashed import set_flashed
from ..common.pg import get_conn
from ..drafts.attri import status
from .pg import (
    check_article, check_cart, check_last, check_rel,
    select_arts, select_broadcast, select_carts, select_followed,
    select_labeled_arts, select_l_followed)


class CArt(HTTPEndpoint):
    async def get(self, request):
        slug = request.query_params.get('slug', '')
        conn = await get_conn(request.app.config)
        res = {'art': None,
               'cu': await checkcu(
                   request, conn, request.headers.get('x-auth-token'))}
        cu = res['cu']
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            await conn.close()
            return JSONResponse(res)
        if cu.get('weight') < 250:
            res['message'] = 'Доступ ограничен, у вас недостаточно прав.'
            await conn.close()
            return JSONResponse(res)
        art = dict()
        await check_cart(request, conn, slug, art)
        await conn.close()
        if not art:
            res['message'] = 'Ничего не найдено, проверьте ссылку.'
            await conn.close()
            return JSONResponse(res)
        res['art'] = art
        res['admin'] = cu.get('weight') == 255
        return JSONResponse(res)

    async def put(self, request):
        res = {'done': None}
        d = await request.form()
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, d.get('auth'))
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            await conn.close()
            return JSONResponse(res)
        if cu.get('weight') < 250:
            res['message'] = 'Доступ ограничен, у вас недостаточно прав.'
            await conn.close()
            return JSONResponse(res)
        slug = d.get('slug', '')
        if not slug:
            res['message'] = 'Запрос содержит неверные параметры.'
            await conn.close()
            return JSONResponse(res)
        art = await conn.fetchrow(
            'SELECT slug, state FROM articles WHERE slug = $1', slug)
        if art is None:
            res['message'] = 'Запрос содержит неверные данные.'
            await conn.close()
            return JSONResponse(res)
        if art.get('state') in (status.pub, status.priv, status.ffo):
            await conn.execute(
                'UPDATE articles SET state = $1 WHERE slug = $2',
                status.cens, slug)
            res['done'] = True
            res['redirect'] = request.url_for('arts:cart', slug=slug)._url
        if art.get('state') == status.cens:
            await conn.execute(
                'UPDATE articles SET state = $1 WHERE slug = $2',
                status.draft, slug)
            res['done'] = True
            res['redirect'] = request.url_for('arts:carts')._url
        await conn.close()
        return JSONResponse(res)


class CArts(HTTPEndpoint):
    async def get(self, request):
        conn = await get_conn(request.app.config)
        res = {'cu': await checkcu(
            request, conn, request.headers.get('x-auth-token'))}
        cu = res['cu']
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            await conn.close()
            return JSONResponse(res)
        if cu.get('weight') < 250:
            res['message'] = 'Доступ ограничен, у вас недостаточно прав.'
            await conn.close()
            return JSONResponse(res)
        page = await parse_page(request)
        last = await check_last(
            conn, page,
            request.app.config.get('ARTS_PER_PAGE', cast=int, default=3),
            'SELECT count(*) FROM articles WHERE state = $1', status.cens)
        if page > last:
            res['message'] = f'Всего страниц: {last}.'
            await conn.close()
            return JSONResponse(res)
        res['pagination'] = dict()
        await select_carts(
            request, conn, res['pagination'], page,
            request.app.config.get('ARTS_PER_PAGE', cast=int, default=3), last)
        if res['pagination']:
            if res['pagination']['next'] or res['pagination']['prev']:
                res['pv'] = True
        await conn.close()
        return JSONResponse(res)


class LLenta(HTTPEndpoint):
    async def get(self, request):
        label = request.query_params.get('label')
        conn = await get_conn(request.app.config)
        res = {'label': label,
               'cu': await checkcu(
                   request, conn, request.headers.get('x-auth-token'))}
        cu = res['cu']
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            await conn.close()
            return JSONResponse(res)
        page = await parse_page(request)
        last = await check_last(
            conn, page,
            request.app.config.get('ARTS_PER_PAGE', cast=int, default=3),
            '''SELECT count(*) FROM articles AS a, followers AS f, labels, als
                 WHERE a.author_id = f.author_id
                   AND f.follower_id = $1
                   AND a.id = als.article_id
                   AND labels.label = $2
                   AND labels.id = als.label_id
                   AND a.state IN ($3, $4, $5)''',
            cu.get('id'), label, status.pub, status.priv, status.ffo)
        if page > last:
            res['message'] = f'Всего страниц: {last}.'
            await conn.close()
            return JSONResponse(res)
        res['pagination'] = dict()
        await select_l_followed(
            request, conn, cu.get('id'), label, res['pagination'], page,
            request.app.config.get('ARTS_PER_PAGE', cast=int, default=3), last)
        if res['pagination']:
            if res['pagination']['next'] or res['pagination']['prev']:
                res['pv'] = True
        await conn.close()
        return JSONResponse(res)


class Alabels(HTTPEndpoint):
    async def get(self, request):
        label = request.query_params.get('label')
        conn = await get_conn(request.app.config)
        res = {'cu': await checkcu(
            request, conn, request.headers.get('x-auth-token')),
               'label': label}
        page = await parse_page(request)
        last = await check_last(
            conn, page,
            request.app.config.get('ARTS_PER_PAGE', cast=int, default=3),
            '''SELECT count(*) FROM articles, labels, als
                 WHERE articles.id = als.article_id
                   AND labels.label = $1
                   AND labels.id = als.label_id
                   AND articles.state IN ($2, $3)''',
            label, status.pub, status.priv)
        if page > last:
            res['message'] = f'Всего страниц: {last}.'
            await conn.close()
            return JSONResponse(res)
        res['pagination'] = dict()
        await select_labeled_arts(
            request, conn, label, res['pagination'], page,
            request.app.config.get('ARTS_PER_PAGE', cast=int, default=3), last)
        if res['pagination']:
            if res['pagination']['next'] or res['pagination']['prev']:
                res['pv'] = True
        await conn.close()
        return JSONResponse(res)


class Dislike(HTTPEndpoint):
    async def put(self, request):
        res = {'done': None}
        d = await request.form()
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, d.get('auth'))
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            await conn.close()
            return JSONResponse(res)
        art = await conn.fetchrow(
            '''SELECT a.id, a.author_id, u.weight, u.ugroup
                 FROM articles AS a, users AS u
                 WHERE a.author_id = u.id
                   AND a.slug = $1 AND a.state IN ($2, $3, $4)''',
            d.get('slug', ''), status.pub, status.priv, status.ffo)
        if art is None:
            res['message'] = 'Запрос содержит неверные параметры.'
            await conn.close()
            return JSONResponse(res)
        rel = await check_rel(conn, art.get('author_id'), cu.get('id'))
        if cu.get('weight') < 50 or art.get('weight') == 255 or \
                rel['blocked'] or rel['blocker']:
            res['message'] = 'Запрос отклонён.'
            await conn.close()
            return JSONResponse(res)
        l = await conn.fetchrow(
            'SELECT * FROM likes WHERE article_id = $1 AND user_id = $2',
            art.get('id'), cu.get('id'))
        d = await conn.fetchrow(
            'SELECT * FROM dislikes WHERE article_id = $1 AND user_id = $2',
            art.get('id'), cu.get('id'))
        if l:
            await conn.execute(
                'DELETE FROM likes WHERE article_id = $1 AND user_id = $2',
                art.get('id'), cu.get('id'))
        if not l and not d:
            await conn.execute(
                'INSERT INTO dislikes (article_id, user_id) VALUES ($1, $2)',
                art.get('id'), cu.get('id'))
        res = {'done': True,
               'likes': await conn.fetchval(
                   'SELECT count(*) FROM likes WHERE article_id = $1',
                   art.get('id')),
               'dislikes': await conn.fetchval(
                   'SELECT count(*) FROM dislikes WHERE article_id = $1',
                   art.get('id'))}
        await conn.close()
        return JSONResponse(res)


class Like(HTTPEndpoint):
    async def put(self, request):
        res = {'done': None}
        d = await request.form()
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, d.get('auth'))
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            await conn.close()
            return JSONResponse(res)
        art = await conn.fetchrow(
            '''SELECT id, author_id FROM articles
                 WHERE slug = $1 AND state IN ($2, $3, $4)''',
            d.get('slug', ''), status.pub, status.priv, status.ffo)
        if art is None:
            res['message'] = 'Запрос содержит неверные параметры.'
            await conn.close()
            return JSONResponse(res)
        if cu.get('id') == art.get('author_id'):
            res['message'] = 'Запрос отклонён.'
            await conn.close()
            return JSONResponse(res)
        l = await conn.fetchrow(
            'SELECT * FROM likes WHERE article_id = $1 AND user_id = $2',
            art.get('id'), cu.get('id'))
        d = await conn.fetchrow(
            'SELECT * FROM dislikes WHERE article_id = $1 AND user_id = $2',
            art.get('id'), cu.get('id'))
        if d:
            await conn.execute(
                'DELETE FROM dislikes WHERE article_id = $1 AND user_id = $2',
                art.get('id'), cu.get('id'))
        if not d and not l:
            await conn.execute(
                'INSERT INTO likes (article_id, user_id) VALUES ($1, $2)',
                art.get('id'), cu.get('id'))
        res = {'done': True,
               'likes': await conn.fetchval(
                   'SELECT count(*) FROM likes WHERE article_id = $1',
                   art.get('id')),
               'dislikes': await conn.fetchval(
                   'SELECT count(*) FROM dislikes WHERE article_id = $1',
                   art.get('id'))}
        await conn.close()
        return JSONResponse(res)


class Lenta(HTTPEndpoint):
    async def get(self, request):
        conn = await get_conn(request.app.config)
        res = {'cu': await checkcu(
            request, conn, request.headers.get('x-auth-token'))}
        cu = res['cu']
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            await conn.close()
            return JSONResponse(res)
        page = await parse_page(request)
        last = await check_last(
            conn, page,
            request.app.config.get('ARTS_PER_PAGE', cast=int, default=3),
            '''SELECT count(*) FROM articles AS a, followers AS f
                 WHERE a.author_id = f.author_id
                   AND state IN ($1, $2, $3) AND f.follower_id = $4''',
            status.pub, status.priv, status.ffo, cu.get('id'))
        if page > last:
            res['message'] = f'Всего страниц: {last}.'
            await conn.close()
            return JSONResponse(res)
        res['pagination'] = dict()
        await select_followed(
            request, conn, res['pagination'], cu.get('id'), page,
            request.app.config.get('ARTS_PER_PAGE', cast=int, default=3), last)
        if res['pagination']:
            if res['pagination']['next'] or res['pagination']['prev']:
                res['pv'] = True
        await conn.close()
        return JSONResponse(res)

    async def put(self, request):
        res = {'done': None}
        d = await request.form()
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, d.get('auth'))
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            await conn.close()
            return JSONResponse(res)
        user = await conn.fetchval(
            'SELECT author_id FROM articles WHERE slug = $1',
            d.get('slug', ''))
        if user is None:
            res['message'] = 'Запрос содержит неверные параметры.'
            await conn.close()
            return JSONResponse(res)
        rel = await check_rel(conn, user, cu.get('id'))
        if rel['follower']:
            await conn.execute(
                '''DELETE FROM followers WHERE author_id = $1
                     AND follower_id = $2''', user, cu.get('id'))
            res['done'] = True
            await set_flashed(request, 'Автор топика удалён из вашей ленты.')
        else:
            if rel['blocked'] or rel['blocker']:
                res['message'] = 'Запрос отклонён.'
                await conn.close()
                return JSONResponse(res)
            await conn.execute(
                '''INSERT INTO followers (author_id, follower_id)
                     VALUES ($1, $2)''', user, cu.get('id'))
            res['done'] = True
            await set_flashed(request, 'Автор топика добавлен в вашу ленту.')
        await conn.close()
        return JSONResponse(res)


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
            return JSONResponse(res)
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
        res['anns'] = await select_broadcast(conn, art.get('author_id'))
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


class Arts(HTTPEndpoint):
    async def get(self, request):
        conn = await get_conn(request.app.config)
        res = {'cu': await checkcu(
            request, conn, request.headers.get('x-auth-token'))}
        page = await parse_page(request)
        last = await check_last(
            conn, page,
            request.app.config.get('ARTS_PER_PAGE', cast=int, default=3),
            'SELECT count(*) FROM articles WHERE state IN ($1, $2)',
            status.pub, status.priv)
        if page > last:
            res['message'] = f'Всего страниц: {last}.'
            await conn.close()
            return JSONResponse(res)
        res['pagination'] = dict()
        await select_arts(
            request, conn, res['pagination'], page,
            request.app.config.get('ARTS_PER_PAGE', cast=int, default=3), last)
        if res['pagination']:
            if res['pagination']['next'] or res['pagination']['prev']:
                res['pv'] = True
        await conn.close()
        return JSONResponse(res)
