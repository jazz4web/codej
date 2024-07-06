from ..auth.cu import getcu
from ..common.aparsers import parse_page
from ..common.flashed import get_flashed
from ..common.pg import get_conn


async def show_comments(request):
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    return request.app.jinja.TemplateResponse(
        'comments/comments.html',
        {'request': request,
         'cu': cu,
         'page': await parse_page(request),
         'listed': True,
         'flashed': await get_flashed(request)})
