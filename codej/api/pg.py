from datetime import datetime, timedelta
from validate_email import validate_email

from ..auth.attri import groups
from ..common.random import get_unique_s


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
