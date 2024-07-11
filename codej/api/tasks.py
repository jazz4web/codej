import asyncio
import functools

from datetime import datetime

from aiosmtplib import send
from email.message import EmailMessage

from ..auth.attri import defaultg
from ..auth.pg import create_user_record
from ..captcha.common import check_val
from ..captcha.picturize.picture import generate_image
from ..common.pg import get_conn
from .pg import define_acc, get_acc
from .tokens import get_request_token
from .tools import define_target_url

remswap = 'UPDATE accounts SET swap = null WHERE id = $1'


async def check_swapped(config):
    conn = await get_conn(config)
    swapped = await conn.fetch(
        'SELECT id, requested FROM accounts WHERE swap IS NOT null')
    length = 3600 * config.get('TOKEN_LENGTH', cast=float)
    now = datetime.utcnow()
    while swapped:
        cur = swapped.pop()
        req = (now - cur.get('requested')).seconds
        if req > length:
            await conn.execute(remswap, cur['id'])
        else:
            asyncio.ensure_future(
                remove_swap_on_startup(config, cur.get('id'), length - req))
    await conn.close()


async def remove_swap_on_startup(config, aid, interval):
    await asyncio.sleep(interval)
    conn = await get_conn(config)
    await conn.execute(remswap, aid)
    await conn.close()


async def remove_swap(config, account):
    await asyncio.sleep(
        3600*config.get('TOKEN_LENGTH', cast=float))
    conn = await get_conn(config)
    await conn.execute(remswap, account.get('id'))
    await conn.close()


async def request_email_change(request, account, address, cu):
    conn = await get_conn(request.app.config)
    requested = await conn.fetchrow(
        'SELECT address, user_id FROM accounts WHERE address = $1', address)
    if requested and not requested.get('user_id'):
        await conn.execute('DELETE FROM accounts WHERE address = $1', address)
    await conn.execute(
        'UPDATE accounts SET swap = $1, requested = $2 WHERE address = $3',
        address, datetime.utcnow(), account.get('address'))
    await conn.close()
    token = await get_request_token(request, account.get('id'))
    url = f'{request.url_for("index")}?realm=chem&key={token}'
    content = request.app.jinja.get_template(
        'emails/change-email.html').render(
            username=cu.get('username'),
            index=request.url_for('index'), target=url,
            length=request.app.config.get('TOKEN_LENGTH', cast=float),
            interval=request.app.config.get('REQUEST_INTERVAL', cast=float),
            old=account.get('address'), new=address)
    if request.app.config.get('DEBUG', cast=bool):
        print(content)
    else:
        message = EmailMessage()
        message["From"] = request.app.config.get('SENDER', cast=str)
        message["To"] = address
        message["Subject"] = request.app.config.get(
            'SUBJECT_PREFIX', cast=str) + "Смена e-mail адреса"
        message.set_content(content)
        message.replace_header('Content-Type', 'text/html; charset="utf-8"')
        await send(
            message,
            recipients=[address],
            hostname=request.app.config.get('MAIL_SERVER', cast=str),
            port=request.app.config.get('MAIL_PORT', cast=str),
            username=request.app.config.get('MAIL_USERNAME', cast=str),
            password=request.app.config.get('MAIL_PASSWORD', cast=str),
            use_tls=request.app.config.get('MAIL_USE_SSL', cast=bool))


async def create_user(request, username, passwd, aid):
    conn = await get_conn(request.app.config)
    now = datetime.utcnow()
    dg = await conn.fetchval('SELECT dgroup FROM settings') or defaultg
    user_id = await create_user_record(conn, username, passwd, dg, now)
    await conn.execute(
        'UPDATE accounts SET user_id = $1 WHERE id = $2', user_id, aid)
    await conn.close()


async def request_passwd(request, account, address):
    conn = await get_conn(request.app.config)
    username, subject, template = await define_acc(conn, account)
    account = await get_acc(conn, account, address)
    await conn.close()
    url = await define_target_url(
        request, account,
        await get_request_token(request, account.get('id')))
    content = request.app.jinja.get_template(template).render(
        username=username, index=request.url_for('index'),
        target=url, length=request.app.config.get('TOKEN_LENGTH', cast=float),
        interval=request.app.config.get('REQUEST_INTERVAL', cast=float))
    if request.app.config.get('DEBUG', cast=bool):
        print(content)
    else:
        message = EmailMessage()
        message["From"] = request.app.config.get('SENDER', cast=str)
        message["To"] = account.get('address')
        message["Subject"] = request.app.config.get(
            'SUBJECT_PREFIX', cast=str) + subject
        message.set_content(content)
        message.replace_header('Content-Type', 'text/html; charset="utf-8"')
        await send(
            message,
            recipients=[account.get('address')],
            hostname=request.app.config.get('MAIL_SERVER', cast=str),
            port=request.app.config.get('MAIL_PORT', cast=str),
            username=request.app.config.get('MAIL_USERNAME', cast=str),
            password=request.app.config.get('MAIL_PASSWORD', cast=str),
            use_tls=request.app.config.get('MAIL_USE_SSL', cast=bool))
    return None


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
