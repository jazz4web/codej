from ..pictures.attri import status


async def check_friends(conn, author, fiend):
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
