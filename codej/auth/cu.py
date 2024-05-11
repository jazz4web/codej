import asyncio

from ..api.tasks import ping_user
from ..api.tokens import check_token
from ..auth.attri import groups

session = '''SELECT u,id, u.username, u.ugroup, s.brkey
                 FROM users AS u, sessions AS s
                 WHERE u.id = s.user_id AND s.suffix = $1'''


async def checkcu(request, conn, token):
    cache = await check_token(request.app.config, token)
    if cache:
        cache = cache.get('cache')
        query = await conn.fetchrow(session, cache)
        if query and query.get('ugroup') == groups.pariah:
            if request.session.get('_uid'):
                request.session.pop('_uid')
            await conn.execute(
                'DELETE FROM sessions WHERE suffix = $1', cache)
            return None
        if query:
            asyncio.ensure_future(
                ping_user(request.app.config, query.get('id')))
            return {'id': query.get('id'),
                    'username': query.get('username'),
                    'group': query.get('ugroup'),
                    'brkey': query.get('brkey'),
                    'ava': request.url_for(
                        'ava', username=query.get('username'), size=22)._url}
    else:
        if request.session.get('_uid'):
            request.session.pop('_uid')
    return None


async def getcu(request, conn):
    if cache := request.session.get('_uid'):
        query = await conn.fetchrow(session, cache)
        if query and query.get('ugroup') == groups.pariah:
            request.session.pop('_uid')
            await conn.execute(
                'DELETE FROM sessions WHERE suffix = $1', cache)
            await set_flashed(
                request, 'Ваше присутствие в сервисе нежелательно.')
            return None
        if query:
            asyncio.ensure_future(
                ping_user(request.app.config, query.get('id')))
            return {'id': query.get('id'),
                    'username': query.get('username'),
                    'group': query.get('ugroup'),
                    'brkey': query.get('brkey'),
                    'ava': request.url_for(
                        'ava', username=query.get('username'), size=22)._url}
        else:
            request.session.pop('_uid')
    return None
