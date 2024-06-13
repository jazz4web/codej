from ..api.parse import parse_art_query
from ..drafts.attri import status as statusd
from ..pictures.attri import status


async def check_topic(request, conn, slug, target):
    query = await conn.fetchrow(
        '''SELECT a.id, a.title, a.slug, a.suffix, a.html, a.summary,
                  a.meta, a.published, a.edited, a.state, a.commented,
                  a.viewed, a.author_id, u.username
             FROM articles AS a, users AS u
             WHERE a.slug = $1 AND a.state = $2 AND u.id = a.author_id''',
        slug, statusd.pub)
    if query:
        await parse_art_query(request, conn, query, target)


async def check_friends(conn, author, friend):
    if await conn.fetchrow(
            '''SELECT author_id, friend_id FROM friends
                 WHERE author_id = $1 AND friend_id = $2''', author, friend):
        return True
    return False


async def check_state(conn, target, cu):
    if target['state'] == status.pub:
        return True
    elif target['state'] == status.priv:
        if cu:
            return True
    elif target['state'] == status.ffo:
        if cu and cu['id'] == target['author_id']:
            return True
        if cu and cu.get('weight') == 255:
            return True
        if cu and await check_friends(conn, target['author_id'], cu['id']):
            return True
    return False
