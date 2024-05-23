import asyncio
import functools
import os

from starlette.exceptions import HTTPException
from starlette.responses import FileResponse, Response

from ..auth.cu import getcu
from ..common.flashed import get_flashed
from ..common.pg import get_conn
from ..dirs import static
from ..errors import E404
from .tools import resize


async def show_avatar(request):
    size = request.path_params.get('size')
    if size < 22 or size > 160:
        raise HTTPException(status_code=404, detail=E404)
    conn = await get_conn(request.app.config)
    res = await conn.fetchrow(
        'SELECT id, username FROM users WHERE username = $1',
        request.path_params.get('username'))
    if res is None:
        await conn.close()
        raise HTTPException(status_code=404, detail=E404)
    ava = await conn.fetchval(
        'SELECT picture FROM avatars WHERE user_id = $1', res.get('id'))
    await conn.close()
    loop = asyncio.get_running_loop()
    image = await loop.run_in_executor(
        None, functools.partial(resize, size, ava))
    response = Response(image, media_type='image/png')
    if ava is None:
        response.headers.append('cache-control', 'public, max-age=0')
    else:
        response.headers.append(
            'cache-control',
            'public, max-age={0}'.format(
                request.app.config.get(
                    'SEND_FILE_MAX_AGE', cast=int, default=0)))
    return response


async def show_index(request):
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    await conn.close()
    realm = request.query_params.get('realm')
    if realm == 'chem':
        return request.app.jinja.TemplateResponse(
            'main/chem.html',
            {'request': request,
             'key': request.query_params.get('key'),
             'cu': cu,
             'listed': True})
    if cu is None:
        if realm == 'gpasswd':
            return request.app.jinja.TemplateResponse(
                'main/setpwd.html',
                {'request': request,
                 'key': request.query_params.get('key'),
                 'interval': request.app.config.get(
                     'REQUEST_INTERVAL', cast=int),
                 'listed': False})
        if realm == 'rpasswd':
            return request.app.jinja.TemplateResponse(
                'main/resetpwd.html',
                {'request': request,
                 'key': request.query_params.get('key'),
                 'interval': request.app.config.get(
                     'REQUEST_INTERVAL', cast=int),
                 'listed': False})
        if realm == 'reg':
            return request.app.jinja.TemplateResponse(
                'main/reg.html',
                {'request': request,
                 'listed': False})
        if realm == 'login':
            return request.app.jinja.TemplateResponse(
                'main/login.html',
                {'request': request,
                 'listed': False})
    logout,lall = 0, 0
    if cu and realm == 'logoutall':
        lall = 1
    if cu and realm == 'logout':
        logout = 1
    return request.app.jinja.TemplateResponse(
        'main/index.html',
        {'request': request,
         'flashed': await get_flashed(request),
         'cu': cu,
         'logout': logout,
         'lall': lall,
         'listed': True})


async def show_favicon(request):
    if request.method == 'GET':
        return FileResponse(
            os.path.join(static, 'images', 'favicon.ico'))
