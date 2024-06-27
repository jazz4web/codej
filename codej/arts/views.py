from starlette.responses import RedirectResponse

from ..auth.cu import getcu
from ..common.aparsers import parse_page
from ..common.flashed import get_flashed
from ..common.pg import get_conn


async def show_l_followed(request):
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        'arts/llenta.html',
        {'request': request,
         'cu': cu,
         'page': await parse_page(request),
         'label': request.path_params.get('label'),
         'listed': True,
         'flashed': await get_flashed(request)})


async def show_followed(request):
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        'arts/lenta.html',
        {'request': request,
         'page': await parse_page(request),
         'cu': cu,
         'listed': True,
         'flashed': await get_flashed(request)})


async def show_l_author(request):
    username = request.path_params.get('username')
    label = request.path_params.get('label')
    url = request.url_for('blogs:blog-l', username=username, label=label)
    return RedirectResponse(url, 301)


async def show_author(request):
    username = request.path_params.get('username')
    url = request.url_for('blogs:blog', username=username)
    return RedirectResponse(url, 301)


async def show_labeled_arts(request):
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        'arts/labeled-arts.html',
        {'request': request,
         'cu': cu,
         'page': await parse_page(request),
         'label': request.path_params.get('label'),
         'listed': True,
         'flashed': await get_flashed(request)})


async def show_arts(request):
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        'arts/arts.html',
        {'request': request,
         'cu': cu,
         'page': await parse_page(request),
         'listed': True,
         'flashed': await get_flashed(request)})


async def show_art(request):
    slug = request.path_params.get('slug')
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        'arts/art.html',
        {'request': request,
         'cu': cu,
         'slug': slug,
         'listed': False,
         'flashed': await get_flashed(request)})
