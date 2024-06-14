from starlette.responses import PlainTextResponse

from ..auth.cu import getcu
from ..common.flashed import get_flashed
from ..common.pg import get_conn


async def show_arts(request):
    return PlainTextResponse('Сайт в стадии разработки, зайдите позже.')


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
