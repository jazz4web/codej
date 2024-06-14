import asyncio
import functools
import os

from starlette.exceptions import HTTPException
from starlette.responses import (
    FileResponse, RedirectResponse, Response)

from ..auth.cu import getcu
from ..common.flashed import get_flashed
from ..common.pg import get_conn
from ..dirs import static
from ..errors import E404
from ..pictures.attri import status
from .pg import check_state, check_topic
from .tools import resize


async def show_sitemap(request):
    conn = await get_conn(request.app.config)
    arts = await conn.fetch(
         '''SELECT slug, published, edited FROM articles
              WHERE state = $1 ORDER BY published DESC LIMIT 250''',
         status.pub)
    await conn.close()
    response = request.app.jinja.TemplateResponse(
         'main/sitemap.xml',
         {'request': request,
          'arts': arts})
    response.media_type = 'application/xml'
    response.headers['content-type'] = 'application/xml'
    return response


async def show_public(request):
    slug = request.path_params.get('slug')
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    if cu:
        return RedirectResponse(request.url_for('arts:art', slug=slug), 301)
    topic = dict()
    await check_topic(request, conn, slug, topic)
    await conn.close()
    if not topic:
        raise HTTPException(
            status_code=404, detail='Такой страницы у нас нет.')
    return request.app.jinja.TemplateResponse(
        'main/show-public.html',
        {'request': request,
         'topic': topic,
         'listed': False})


async def show_picture(request):
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    target = await conn.fetchrow(
        '''SELECT albums.state, albums.author_id, pictures.suffix,
                  pictures.picture, pictures.format FROM albums, pictures
             WHERE pictures.suffix = $1
             AND albums.id = pictures.album_id''',
        request.path_params.get('suffix'))
    if target is None:
        response = FileResponse(
            os.path.join(static, 'images', '404.png'))
        response.headers.append(
            'cache-control',
            'max-age=0, no-store, no-cache, must-revalidate')
    else:
        if await check_state(conn, target, cu):
            response = Response(
                target.get('picture'),
                media_type=f'image/{target.get("format").lower()}')
            response.headers.append(
                'cache-control',
                'public, max-age={0}'.format(
                    request.app.config.get(
                        'SEND_FILE_MAX_AGE', cast=int, default=0)))
        else:
            if target['state'] == status.ffo:
                picname = '403a.png'
            else:
                picname = '403.png'
            response = FileResponse(
                os.path.join(static, 'images', picname))
            response.headers.append(
                'cache-control',
                'max-age=0, no-store, no-cache, must-revalidate')
    await conn.close()
    return response


async def jump(request):
    suffix = request.path_params.get('suffix')
    conn = await get_conn(request.app.config)
    if len(suffix) in (6, 7, 9, 10):
        alias = await conn.fetchrow(
            'SELECT url, clicked, author_id FROM aliases WHERE suffix = $1',
            suffix)
        if alias and alias.get('author_id'):
            cu = await getcu(request, conn)
            jumps = request.session.get('jumps', list())
            if suffix not in jumps and \
                    (not cu or cu.get('id') != alias.get('author_id')):
                clicked = alias.get('clicked') + 1
                if clicked > 9999:
                    clicked = 9
                await conn.execute(
                    'UPDATE aliases SET clicked = $1 WHERE suffix = $2',
                    clicked, suffix)
                jumps.append(suffix)
                if len(jumps) > 20:
                    del jumps[0]
                request.session['jumps'] = jumps
            await conn.close()
            return RedirectResponse(alias.get('url'), 301)
    elif len(suffix) in (8, 11, 12, 13):
        art = await conn.fetchrow(
            'SELECT suffix, slug FROM articles WHERE suffix = $1', suffix)
        await conn.close()
        if art:
            curl = request.url_for('public', slug=art.get('slug'))
            rurl = request.url_for('arts:art', slug=art.get('slug'))
            response = RedirectResponse(rurl, 301)
            response.headers.append('Link', f'<{curl}>; rel="canonical"')
            return response
    await conn.close()
    raise HTTPException(status_code=404, detail='Такой страницы у нас нет.')


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
