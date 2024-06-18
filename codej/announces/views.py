from ..auth.cu import getcu
from ..common.aparsers import parse_page
from ..common.flashed import get_flashed
from ..common.pg import get_conn


async def show_announces(request):
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        'announces/announces.html',
        {'request': request,
         'cu': cu,
         'listed': True,
         'page': await parse_page(request),
         'flashed': await get_flashed(request)})
