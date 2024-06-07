import math

from datetime import datetime, timedelta
from validate_email import validate_email

from ..auth.attri import groups
from ..common.aparsers import iter_pages, parse_title, parse_units, parse_url
from ..common.random import get_unique_s


async def get_user_stat(conn, uid):
    return {'albums': await conn.fetchval(
        'SELECT count(*) FROM albums WHERE author_id = $1', uid),
            'files': await conn.fetchval(
        '''SELECT count(*) FROM albums, pictures
             WHERE author_id = $1
             AND pictures.album_id = albums.id''', uid),
            'volume': await parse_units(await conn.fetchval(
        'SELECT sum(volume) FROM albums WHERE author_id = $1', uid) or 0)}


async def select_albums(conn, uid, page, per_page, last):
    query = await conn.fetch(
        '''SELECT title, suffix FROM albums
             WHERE author_id = $1
             ORDER BY changed DESC LIMIT $2 OFFSET $3''',
        uid, per_page, per_page*(page-1))
    if query:
        return {'page': page,
                'next': page + 1 if page + 1 <= last else None,
                'prev': page - 1 or None,
                'pages': await iter_pages(page, last),
                'albums': [{'title': record.get('title'),
                            'parsed': await parse_title(
                                record.get('title'), 40),
                            'suffix': record.get('suffix')}
                           for record in query]}
    return None


async def select_aliases(request, conn, uid, target, page, per_page, last):
    query = await conn.fetch(
        '''SELECT url, created, clicked, suffix FROM aliases
             WHERE author_id = $1
             ORDER BY created DESC LIMIT $2 OFFSET $3''',
        uid, per_page, per_page*(page-1))
    if query:
        target['page'] = page
        target['next'] = page + 1 if page + 1 <= last else None
        target['prev'] = page - 1 or None
        target['pages'] = await iter_pages(page, last)
        target['aliases'] = [
            {'url': record.get('url'),
             'parsed': await parse_url(record.get('url')),
             'created': f'{record.get("created").isoformat()}Z',
             'clicked': record.get('clicked'),
             'suffix': record.get('suffix'),
             'alias': request.url_for(
                 'jump', suffix=record.get('suffix'))._url}
             for record in query]


async def select_users(
        request, conn, uid, is_admin, target, page, per_page, last):
    if is_admin:
        query = await conn.fetch(
            '''SELECT username, ugroup, registered, last_visit
                 FROM users WHERE id != $1
                 ORDER BY last_visit DESC LIMIT $2 OFFSET $3''',
            uid, per_page, per_page*(page-1))
    else:
        query = await conn.fetch(
            '''SELECT username, ugroup, registered, last_visit
                 FROM users WHERE id != $1 AND weight > 0
                 ORDER BY last_visit DESC LIMIT $2 OFFSET $3''',
            uid, per_page, per_page*(page-1))
    if query:
        target['page'] = page
        target['next'] = page + 1 if page + 1 <= last else None
        target['prev'] = page - 1 or None
        target['pages'] = await iter_pages(page, last)
        target['users'] = [
            {'username': record.get('username'),
             'group': record.get('ugroup'),
             'last_visit': f'{record.get("last_visit").isoformat()}Z',
             'registered': f'{record.get("registered").isoformat()}Z',
             'ava': request.url_for(
                 'ava', username=record.get('username'), size=98)._url}
            for record in query]


async def check_last(conn, page, per_page, *args):
    num = await conn.fetchval(*args)
    return math.ceil(num / per_page) or 1


async def check_account(config, conn, account, address):
    length = timedelta(
        seconds=round(3600*config.get('TOKEN_LENGTH', cast=float)))
    interval = timedelta(
        seconds=round(3600*config.get('REQUEST_INTERVAL', cast=float)))
    if datetime.utcnow() - account.get('requested') < interval:
        return 'Сервис временно недоступен, попробуйте зайти позже.'
    if account.get('address') == address:
        return 'Задан Ваш текущий адрес, запрос не имеет смысла.'
    if await check_swap(conn, address, length):
        return 'Адрес в свопе, выберите другой или повторите попытку позже.'
    requested = await conn.fetchrow(
        'SELECT requested, user_id FROM accounts WHERE address = $1', address)
    if requested and requested.get('user_id'):
        return 'Этот адрес уже зарегистрирован, запрос отклонён.'
    if requested and datetime.utcnow() - requested.get('requested') < length:
        return 'Адрес регистрируется, выберите другой или попробуйте позже.'
    return None


async def check_rel(conn, uid1, uid2):
    friend = bool(await conn.fetchrow(
        '''SELECT author_id, friend_id FROM friends
             WHERE author_id = $1 AND friend_id = $2''', uid1, uid2))
    follower = bool(await conn.fetchrow(
        '''SELECT author_id, follower_id FROM followers
             WHERE author_id = $1 AND follower_id = $2''', uid1, uid2))
    blocker = bool(await conn.fetchrow(
        '''SELECT target_id, blocker_id FROM blockers
             WHERE target_id = $1 AND blocker_id = $2''', uid2, uid1))
    blocked = bool(await conn.fetchrow(
        '''SELECT target_id, blocker_id FROM blockers
             WHERE target_id = $1 AND blocker_id = $2''', uid1, uid2))
    return {'friend': friend, 'follower': follower,
            'blocker': blocker, 'blocked': blocked}


async def filter_target_user(request, conn, username):
    query = await conn.fetchrow(
        '''SELECT id, username, ugroup, weight, registered,
                  last_visit, description, last_published FROM users
             WHERE username = $1''', username)
    if query:
        return {'uid': query.get('id'),
                'username': query.get('username'),
                'group': query.get('ugroup'),
                'weight': query.get('weight'),
                'registered': f'{query.get("registered").isoformat()}Z',
                'last_visit': f'{query.get("last_visit").isoformat()}Z',
                'description': query.get('description'),
                'last_published': f'{query.get("last_published").isoformat()}Z'
                if query.get('last_published') else None,
                'ava': request.url_for(
                    'ava', username=query.get('username'), size=160)._url}


async def define_acc(conn, account):
    if account and account.get('user_id'):
        username = await conn.fetchval(
            'SELECT username FROM users WHERE id = $1', account.get('user_id'))
        return username, 'Сброс забытого пароля', 'emails/resetpwd.html'
    return 'Гость', 'Регистрация', 'emails/invitation.html'


async def get_acc(conn, account, address):
    now = datetime.utcnow()
    if account:
        address = account.get('address')
        await conn.execute(
            '''UPDATE accounts SET swap = null, requested = $1
                 WHERE address = $2''', now, address)
    else:
        await conn.execute(
            '''INSERT INTO accounts (address, requested)
                 VALUES ($1, $2)''', address, now)
    return await conn.fetchrow(
        'SELECT id, address, user_id FROM accounts WHERE address = $1',
        address)


async def check_swap(conn, address, length):
    swapped = await conn.fetchrow(
        'SELECT id, swap, requested FROM accounts WHERE swap = $1', address)
    if swapped:
        if datetime.utcnow() - swapped.get('requested') > length:
            await conn.execute(
                'UPDATE accounts SET swap = null WHERE id = $1',
                swapped.get('id'))
            return None
        else:
            return True


async def check_address(request, conn, address):
    message = None
    interval = timedelta(
        seconds=round(
            3600*request.app.config.get('REQUEST_INTERVAL', cast=float)))
    length = timedelta(
        seconds=round(
            3600*request.app.config.get('TOKEN_LENGTH', cast=float)))
    acc = await conn.fetchrow(
        'SELECT address, requested, user_id FROM accounts WHERE address = $1',
        address)
    if acc and datetime.utcnow() - acc.get('requested') < interval:
        message = 'Сервис временно недоступен, попробуйте зайти позже.'
    if await check_swap(conn, address, length):
        message = 'Адрес в свопе, выберите другой или повторите попытку позже.'
    return message, acc


async def create_session(config, conn, rme, user, brkey):
    now = datetime.utcnow()
    if rme:
        expire = now + timedelta(
            seconds=config.get('SESSION_LIFETIME', cast=int))
    else:
        expire = now + timedelta(seconds=2*60*60)
    suffix = await get_unique_s(conn, 'sessions', 13)
    await conn.execute(
        '''INSERT INTO sessions (suffix, brkey, logedin, expire, user_id)
             VALUES ($1, $2, $3, $4, $5)''',
        suffix, brkey, now, expire, user.get('id'))
    return suffix, now


async def filter_user(conn, login):
    squery = '''SELECT users.id, users.username,
                       users.password_hash, users.ugroup
                  FROM users, accounts
                    WHERE users.id = accounts.user_id '''
    if validate_email(login):
        squery += ' AND accounts.address = $1'
    else:
        squery += ' AND users.username = $1'
    query = await conn.fetchrow(squery, login)
    if query and query.get('ugroup') != groups.pariah:
        return {'id': query.get('id'),
                'username': query.get('username'),
                'password_hash': query.get('password_hash')}
