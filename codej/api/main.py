from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse

from ..auth.cu import checkcu
from ..common.pg import get_conn
from .redi import assign_cache


class Index(HTTPEndpoint):
    async def post(self, request):
        conn = await get_conn(request.app.config)
        await checkcu(
            request, conn, (await request.form()).get('auth'))
        res = {'empty': True}
        await conn.close()
        return JSONResponse(res)


class Captcha(HTTPEndpoint):
    async def get(self, request):
        conn = await get_conn(request.app.config)
        captcha = await conn.fetchrow(
            'SELECT val, suffix FROM captchas ORDER BY random() LIMIT 1')
        res = await assign_cache(
            request, 'captcha:',
            captcha.get('suffix'), captcha.get('val'), 180)
        url = request.url_for('captcha', suffix=captcha.get('suffix'))._url
        return JSONResponse({'captcha': res, 'url': url})
