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
from ..common.redi import get_rc
from .pg import define_acc, get_acc
from .tokens import get_request_token
from .tools import define_target_url


async def create_user(request, username, passwd, aid):
    conn = await get_conn(request.app.config)
    now = datetime.utcnow()
    rc = await get_rc(request, future=True)
    dg = await rc.get('def:group') or defaultg
    await rc.aclose()
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
