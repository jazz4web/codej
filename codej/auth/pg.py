from datetime import datetime

from passlib.hash import pbkdf2_sha256

from ..common.pg import get_conn
from .attri import groups, weigh


async def check_username(config, username):
    conn = await get_conn(config)
    res = await conn.fetchrow(
        'SELECT username FROM users WHERE username = $1', username)
    await conn.close()
    return bool(res)


async def check_address(config, address):
    res = False
    conn = await get_conn(config)
    account = await conn.fetchrow(
        'SELECT address, user_id FROM accounts WHERE address = $1', address)
    swap = await conn.fetchrow(
        'SELECT swap FROM accounts WHERE swap = $1', address)
    await conn.close()
    if (account and account.get('user_id')) or swap:
        res = True
    return res


async def create_user_record(conn, username, passwd, group, now):
    await conn.execute(
        '''INSERT INTO users
           (username, ugroup, weight, registered, last_visit, password_hash)
           VALUES ($1, $2, $3, $4, $5, $6)''',
        username, group, await weigh(group),
        now, now, pbkdf2_sha256.hash(passwd))
    return await conn.fetchval(
        'SELECT id FROM users WHERE username = $1', username)


async def update_account(conn, address, uid, now):
    account = await conn.fetchrow(
        'SELECT * FROM accounts WHERE address = $1', address)
    if account:
        await conn.execute(
            '''UPDATE accounts
                 SET address = $1, requested = $2 WHERE user_id = $3''',
            address, now, uid)
    else:
        await conn.execute(
            '''INSERT INTO accounts (address, requested, user_id)
                 VALUES ($1, $2, $3)''', address, now, uid)


async def create_user(config, username, address, passwd, group):
    now = datetime.utcnow()
    conn = await get_conn(config)
    user_id = await create_user_record(conn, username, passwd, group, now)
    await update_account(conn, address, user_id, now)
    await conn.close()
