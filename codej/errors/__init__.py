from ..auth.cu import getcu
from ..common.pg import get_conn

E404 = 'Такой страницы у нас нет.'


async def show_error(request, exc):
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    await conn.close()
    if exc.status_code == 404 and exc.detail != E404:
        exc.detail = E404
    return request.app.jinja.TemplateResponse(
        'errors/error.html',
        {'reason': exc.detail,
         'request': request,
         'cu': cu,
         'error': exc.status_code},
        status_code=exc.status_code)
