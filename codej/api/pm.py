from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse

from ..auth.cu import checkcu
from ..common.aparsers import parse_page
from ..common.flashed import set_flashed
from ..common.pg import get_conn
from .pg import (
    check_last, check_outgoing, check_postponed, check_rel,
    edit_pm, receive_incomming, select_m, send_message)


class Conversation(HTTPEndpoint):
    async def get(self, request):
        conn = await get_conn(request.app.config)
        res = {'cu': await checkcu(
            request, conn, request.headers.get('x-auth-token'))}
        cu = res['cu']
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            await conn.close()
            return JSONResponse(res)
        if cu.get('weight') < 50:
            res['message'] = 'Доступ ограничен, у вас недостаточно прав.'
            await conn.close()
            return JSONResponse(res)
        target = await conn.fetchrow(
            'SELECT id, username, weight FROM users WHERE username= $1',
            request.query_params.get('username'))
        if target is None:
            res['message'] = 'Получатель не определён.'
            await conn.close()
            return JSONResponse(res)
        if cu.get('id') == target.get('id'):
            res['message'] = 'Запрос отклонён.'
            await conn.close()
            return JSONResponse(res)
        if target.get('weight') < 50:
            u = target.get('username')
            res['nopm'] = f'{u} не может получать приватные сообщения.'
        rel = await check_rel(conn, cu.get('id'), target.get('id'))
        if rel['blocker'] or rel['blocked']:
            res['blocked'] = 'Приват заблокирован. Вы поссорились?'
        await check_postponed(conn, cu.get('id'), target.get('id'))
        page = await parse_page(request)
        last = await check_last(
            conn, page,
            request.app.config.get('PM_PER_PAGE', cast=int, default=3),
            '''SELECT count(*) FROM
                 (SELECT id FROM messages
                    WHERE sender_id = $1
                      AND recipient_id = $2
                      AND postponed = false
                      AND removed_by_sender = false
                  UNION
                  SELECT id FROM messages
                    WHERE sender_id = $2
                      AND recipient_id = $1
                      AND postponed = false
                      AND removed_by_recipient = false) AS m''',
            cu.get('id'), target.get('id'))
        if page > last:
            res['message'] = f'Всего страниц: {last}.'
            await conn.close()
            return JSONResponse(res)
        if request.query_params.get('nopage') == '0':
            page = last
        if page == last:
            res['incomming'] = await receive_incomming(
                conn, target.get('id'), cu.get('id'))
        res['outgoing'] = await check_outgoing(
            conn, cu.get('id'), target.get('id'))
        res['shform'] = target.get('weight') >= 50 and \
                (not rel['blocker'] and not rel['blocked']) and \
                not res['outgoing']
        res['pagination'] = dict()
        await select_m(
            request, conn, cu.get('id'), target.get('id'), res['pagination'],
            page, request.app.config.get('PM_PER_PAGE', cast=int, default=3),
            last)
        if res['pagination']:
            if res['pagination']['next'] or res['pagination']['prev']:
                res['pv'] = True
        await conn.close()
        return JSONResponse(res)

    async def patch(self, request):
        res = {'done': None}
        d = await request.form()
        mid, text = int(d.get('mid', '0')), d.get('text', '')
        if not text:
            res['message'] = 'Запрос содержит неверные параметры.'
            return JSONResponse(res)
        if len(text) > 25000:
            res['message'] = 'Превышен лимит в 25000 знаков.'
            return JSONResponse(res)
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, d.get('auth'))
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            await conn.close()
            return JSONResponse(res)
        if cu.get('weight') < 50:
            res['message'] = 'Доступ ограничен, у вас недостаточно прав.'
            await conn.close()
            return JSONResponse(res)
        target = await conn.fetchrow(
            '''SELECT id, body, received, sender_id
                 FROM messages WHERE id = $1 AND sender_id = $2''',
            mid, cu.get('id'))
        if target is None:
            res['message'] = 'Запрос содержит неверные параметры.'
            await conn.close()
            return JSONResponse(res)
        if target.get('body') != text and target.get('received') is None:
            await edit_pm(conn, target.get('id'), text)
            await set_flashed(request, 'Сообщение отредактировано.')
        res['done'] = True
        await conn.close()
        return JSONResponse(res)

    async def post(self, request):
        res = {'done': None}
        d = await request.form()
        recipient, text = d.get('recipient'), d.get('message')
        if not all((recipient, text)):
            res['message'] = 'Запрос содержит неверные параметры.'
            return JSONResponse(res)
        if len(text) > 25000:
            res['message'] = 'Превышен лимит в 25000 знаков.'
            return JSONResponse(res)
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, d.get('auth'))
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            await conn.close()
            return JSONResponse(res)
        if cu.get('weight') < 50:
            res['message'] = 'Доступ ограничен, у вас недостаточно прав.'
            await conn.close()
            return JSONResponse(res)
        if cu.get('username') == recipient:
            res['message'] = 'Запрос отклонён.'
            await conn.close()
            return JSONResponse(res)
        recipient = await conn.fetchrow(
            'SELECT id, username, weight FROM users WHERE username = $1',
            recipient)
        if recipient is None:
            res['message'] = 'Получатель не определён.'
            await conn.close()
            return JSONResponse(res)
        if recipient.get('weight') < 50:
            u = recipient.get('username')
            res['message'] = f'{u} не может получать приватные сообщения.'
            await conn.close()
            return JSONResponse(res)
        rel = await check_rel(conn, cu.get('id'), recipient.get('id'))
        if rel['blocker'] or rel['blocked']:
            res['message'] = 'Приват заблокирован, вы поссорились.'
            await conn.close()
            return JSONResponse(res)
        await send_message(conn, cu.get('id'), recipient.get('id'), text)
        await set_flashed(request, 'Сообщение отправлено.')
        res['done'] = True
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
        if cu.get('weight') < 50:
            res['message'] = 'Доступ ограничен, у вас недостаточно прав.'
            await conn.close()
            return JSONResponse(res)
        target = await conn.fetchrow(
            '''SELECT id, body, received, sender_id FROM messages
                 WHERE id = $1 AND sender_id = $2''',
            int(d.get('mid', '0')), cu.get('id'))
        if target is None:
            res['message'] = 'Запрос содержит неверные параметры.'
            await conn.close()
            return JSONResponse()
        if target.get('received'):
            res['done'] = True
            res['update'] = True
            await conn.close()
            await set_flashed(request, 'Сообщение уже получено.')
            return JSONResponse(res)
        await conn.execute(
            'UPDATE messages SET postponed = true WHERE id = $1',
            target.get('id'))
        res['done'] = True
        res['text'] = target.get('body')
        res['id'] = target.get('id')
        await conn.close()
        return JSONResponse(res)
