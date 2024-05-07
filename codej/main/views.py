import os

from starlette.responses import FileResponse

from ..dirs import static
from ..common.flashed import get_flashed, set_flashed
from ..common.pg import get_conn


async def show_index(request):
    await set_flashed(request, 'This is a flashed message again.')
    return request.app.jinja.TemplateResponse(
        'main/index.html',
        {'request': request,
         'flashed': await get_flashed(request),
         'listed': True})


async def show_favicon(request):
    if request.method == 'GET':
        return FileResponse(
            os.path.join(static, 'images', 'favicon.ico'))
