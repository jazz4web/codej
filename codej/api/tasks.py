import asyncio
import functools

from datetime import datetime

from ..captcha.common import check_val
from ..captcha.picturize.picture import generate_image
from ..common.pg import get_conn


async def rem_old_session(config, uid):
    conn = await get_conn(config)
    await conn.execute(
        'DELETE FROM sessions WHERE user_id = $1 AND expire < $2',
        uid, datetime.utcnow())
    sessions = [record.get('suffix') for record in await conn.fetch(
        '''SELECT suffix FROM sessions
             WHERE user_id = $1
             ORDER BY logedin ASC''', uid)]
    if len(sessions) > 3:
        await conn.execute(
            'DELETE FROM sessions WHERE suffix = $1', sessions[0])
    await conn.close()


async def rem_expired_sessions(config):
    conn = await get_conn(config)
    await conn.execute(
        'DELETE FROM sessions WHERE expire < $1', datetime.utcnow())
    await conn.close()


async def ping_user(config, uid):
    conn = await get_conn(config)
    await conn.execute(
        'UPDATE users SET last_visit = $1 WHERE id = $2',
        datetime.utcnow(), uid)
    await conn.close()


async def change_pattern(conf, suffix):
    conn = await get_conn(conf)
    val = await check_val(conn)
    loop = asyncio.get_running_loop()
    pic = await loop.run_in_executor(
        None, functools.partial(generate_image, val))
    await conn.execute(
        'UPDATE captchas SET val = $1, picture = $2 WHERE suffix = $3',
        val, pic.read(), suffix)
    await loop.run_in_executor(
        None, functools.partial(pic.close))
    await conn.close()
    return None
