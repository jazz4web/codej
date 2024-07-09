import os

from starlette.exceptions import HTTPException
from starlette.responses import FileResponse, PlainTextResponse

from ..auth.cu import getcu
from ..common.flashed import get_flashed
from ..common.pg import get_conn


async def show_tools(request):
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        'admin/tools.html',
        {'request': request,
         'cu': cu,
         'listed': True,
         'flashed': await get_flashed(request)})


async def show_log(request):
    l = request.path_params.get('log')
    if l not in ('access.log', 'previous.log'):
        raise HTTPException(404, detail='Такой страницы у нас нет.')
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    await conn.close()
    if cu and cu.get('weight') in (250, 255):
        if l == 'access.log':
            l = f'/var/log/nginx/{l}'
        else:
            l = '/var/log/nginx/access.log.1'
        if os.path.exists(l):
            response = FileResponse(l)
        else:
            a = 'Файл не существует.\n'
            m = 'Убедитесь, что вы не используете Nginx.'
            response = PlainTextResponse(a + m)
        return response
    raise HTTPException(404, detail='Такой страницы у нас нет.')
