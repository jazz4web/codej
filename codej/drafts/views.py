from ..auth.cu import getcu
from ..common.aparsers import parse_page
from ..common.flashed import get_flashed
from ..common.pg import get_conn


async def show_labeled(request):
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    return request.app.jinja.TemplateResponse(
        'drafts/labeled.html',
        {'request': request,
         'cu': cu,
         'label': request.path_params.get('label'),
         'page': await parse_page(request),
         'listed': True,
         'flashed': await get_flashed(request)})


async def show_draft(request):
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    return request.app.jinja.TemplateResponse(
        'drafts/draft.html',
        {'request': request,
         'cu': cu,
         'slug': request.path_params.get('slug'),
         'listed': False,
         'flashed': await get_flashed(request)})


async def show_drafts(request):
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        'drafts/drafts.html',
        {'request': request,
         'cu': cu,
         'page': await parse_page(request),
         'listed': True,
         'flashed': await get_flashed(request)})
