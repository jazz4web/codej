import os

from starlette.responses import FileResponse

from ..dirs import static
from ..common.pg import get_conn


async def show_index(request):
    query = None
    return request.app.jinja.TemplateResponse(
        'main/index.html',
        {'request': request,
         'data': query})


async def show_favicon(request):
    if request.method == 'GET':
        return FileResponse(
            os.path.join(static, 'images', 'favicon.ico'))
