import asyncio
import functools
import os

from starlette.exceptions import HTTPException
from starlette.responses import FileResponse, Response

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
    cu = None
    if cu is None:
        relm = request.query_params.get('relm')
        if relm == 'login':
            return request.app.jinja.TemplateResponse(
                'main/login.html',
                {'request': request,
                 'listed': False})
    return request.app.jinja.TemplateResponse(
        'main/index.html',
        {'request': request,
         'flashed': await get_flashed(request),
         'listed': True})


async def show_favicon(request):
    if request.method == 'GET':
        return FileResponse(
            os.path.join(static, 'images', 'favicon.ico'))
