from ..auth.cu import getcu
from ..common.flashed import get_flashed
from ..common.pg import get_conn


async def show_profile(request):
    conn = await get_conn(request.app.config)
    cu = await getcu(request, conn)
    return request.app.jinja.TemplateResponse(
        'people/profile.html',
        {'request': request,
         'cu': cu,
         'listed': True,
         'interval': request.app.config.get('REQUEST_INTERVAL', cast=int),
         'username': request.path_params.get('username'),
         'flashed': await get_flashed(request)})
