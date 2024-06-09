import asyncio
import functools

from datetime import datetime
from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse

from ..auth.cu import checkcu
from ..common.aparsers import parse_filename, parse_page
from ..common.flashed import set_flashed
from ..common.pg import get_conn
from ..common.random import get_unique_s
from ..pictures.attri import status
from .checkimg import read_data
from .pg import (
    check_last, create_new_album, get_album, get_pic_stat,
    get_user_stat, select_albums, select_pictures)


class Picstat(HTTPEndpoint):
    async def get(self, request):
        res = {'picture': None}
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, request.headers.get('x-auth-token'))
        if cu is None:
            res['message'] = 'Доступ ограничен, необходима авторизация.'
            await conn.close()
            return JSONResponse(res)
        if cu.get('weight') < 150:
            res['message'] = 'Доступ ограничен, у вас недостаточно прав.'
            await conn.close()
            return JSONResponse(res)
        suffix = request.query_params.get('suffix', None)
        if suffix is None:
            res['message'] = 'Не указан суффикс изображения.'
            await conn.close()
            return JSONResponse(res)
        pic = await get_pic_stat(request, conn, cu.get('id'), suffix)
        if pic is None:
            res['message'] = 'Файл не существует.'
            await conn.close()
            return JSONResponse(res)
        res['picture'] = pic
        await conn.close()
        return JSONResponse(res)


class Album(HTTPEndpoint):
    async def get(self, request):
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, request.headers.get('x-auth-token'))
        res = {'cu': cu}
        if cu is None:
            res['message'] = 'Доступ ограничен, необходима авторизация.'
            await conn.close()
            return JSONResponse(res)
        if cu.get('weight') < 150:
            res['message'] = 'Доступ ограничен, у вас недостаточно прав.'
            await conn.close()
            return JSONResponse(res)
        page = await parse_page(request)
        target = await get_album(
            conn, cu.get('id'), request.path_params.get('suffix'))
        if target is None:
            res['message'] = 'У вас нет такого альбома.'
            await conn.close()
            return JSONResponse(res)
        last = await check_last(
            conn, page,
            request.app.config.get('PICTURES_PER_PAGE', cast=int, default=3),
            'SELECT count(*) FROM pictures WHERE album_id = $1',
            target.get('id'))
        if page > last:
            res['message'] = f'Всего страниц: {last}.'
            await conn.close()
            return JSONResponse(res)
        pagination = await select_pictures(
            conn, target.get('id'), page,
            request.app.config('PICTURES_PER_PAGE', cast=int, default=3),
            last)
        if pagination:
            res['html'] = {'album': request.app.jinja.get_template(
                'pictures/album-list.html').render(
                request=request, pagination=pagination)}
            if pagination['next'] or pagination['prev']:
                res['pv'] = True
        res['album'], res['pagination'] = target, pagination
        res['extra'] = res['pagination'] is None or \
                (res['pagination'] and res['pagination']['page'] == 1)
        await conn.close()
        return JSONResponse(res)

    async def post(self, request):
        res = {'done': None}
        d = await request.form()
        img, auth = d.get('image'), d.get('token')
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, auth)
        if cu is None:
            res['message'] = 'Доступ ограничен, необходима авторизация.'
            await conn.close()
            return JSONResponse(res)
        if cu.get('weight') < 150:
            res['message'] = 'Доступ ограничен, у вас недостаточно прав.'
            await conn.close()
            return JSONResponse(res)
        if not img:
            res['message'] = 'Требуется файл изображения.'
            await conn.close()
            return JSONResponse(res)
        binary = await img.read()
        filename = await parse_filename(img.filename, 128)
        await img.close()
        if len(binary) > 5 * pow(1024, 2):
            res['message'] = 'Недопустимый размер файла.'
            await conn.close()
            return JSONResponse(res)
        loop = asyncio.get_running_loop()
        img = await loop.run_in_executor(
            None, functools.partial(read_data, binary))
        if img is None:
            res['message'] = 'Недопустимый формат файла.'
            await conn.close()
            return JSONResponse(res)
        replica = await conn.fetchrow(
            '''SELECT author_id, suffix, picture
                 FROM (SELECT albums.author_id, albums.suffix,
                              pictures.picture
                         FROM albums LEFT JOIN pictures
                         ON albums.id = pictures.album_id) AS between
                 WHERE author_id = $1 AND picture = $2''',
            cu.get('id'), binary)
        if replica:
            url = request.url_for(
                'pictures:album', suffix=replica.get('suffix'))
            res['message'] = \
                f'Файл загружен ранее в <a href="{url}">альбом</a>.'
            await conn.close()
            return JSONResponse(res)
        target = await get_album(
            conn, cu.get('id'), suffix=request.path_params.get('suffix'))
        e = {'JPEG': '.jpg', 'PNG': '.png', 'GIF': '.gif'}
        suffix = await get_unique_s(
            conn, 'pictures', 10, ext=e.get(img['format']))
        now = datetime.utcnow()
        await conn.execute(
            '''INSERT INTO
                 pictures (uploaded, picture, filename, width,
                           height, format, volume, suffix, album_id)
                 VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)''',
            now, binary, filename, img['width'], img['height'],
            img['format'], len(binary), suffix, target.get('id'))
        await conn.execute(
            'UPDATE albums SET changed = $1, volume = $2 WHERE id = $3',
            now, target.get('volume_')+len(binary), target.get('id'))
        res['done'] = True
        await set_flashed(request, 'Изображение успешно загружено.')
        await conn.close()
        return JSONResponse(res)


class Ustat(HTTPEndpoint):
    async def get(self, request):
        res = {'stat': None}
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, request.headers.get('x-auth-token'))
        if cu is None:
            res['message'] = 'Доступ ограничен, необходима авторизация.'
            await conn.close()
            return JSONResponse(res)
        if cu.get('weight') < 150:
            res['message'] = 'Доступ ограничен, у вас недостаточно прав.'
            await conn.close()
            return JSONResponse(res)
        res['stat'] = await get_user_stat(conn, cu.get('id'))
        res['cu'] = cu
        await conn.close()
        return JSONResponse(res)


class Albumstat(HTTPEndpoint):
    async def get(self, request):
        res = {'album': None}
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, request.headers.get('x-auth-token'))
        if cu is None:
            res['message'] = 'Доступ ограничен, необходима авторизация.'
            await conn.close()
            return JSONResponse(res)
        if cu.get('weight') < 150:
            res['message'] = 'Доступ ограничен, у вас недостаточно прав.'
            await conn.close()
            return JSONResponse(res)
        suffix = request.query_params.get('suffix', None)
        if suffix is None:
            res['message'] = 'Не указан альбом.'
            await conn.close()
            return JSONResponse(res)
        album = await get_album(conn, cu.get('id'), suffix)
        await conn.close()
        if album is None:
            res['message'] = 'Альбом не существует.'
            return JSONResponse(res)
        res['album'] = album
        return JSONResponse(res)


class Albums(HTTPEndpoint):
    async def get(self, request):
        conn = await get_conn(request.app.config)
        res = {'cu': await checkcu(
            request, conn, request.headers.get('x-auth-token'))}
        cu = res['cu']
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            await conn.close()
            return JSONResponse(res)
        if cu.get('weight') < 150:
            res['message'] = 'Доступ ограничен, у вас недостаточно прав.'
            await conn.close()
            return JSONResponse(res)
        page = await parse_page(request)
        last = await check_last(
            conn, page,
            request.app.config.get('ALBUMS_PER_PAGE', cast=int, default=3),
            'SELECT count(*) FROM albums WHERE author_id = $1', cu.get('id'))
        if page > last:
            res['message'] = f'Всего страниц: {last}.'
            await conn.close()
            return JSONResponse(res)
        res['pagination'] = await select_albums(
            conn, cu.get('id'), page,
            request.app.config.get('ALBUMS_PER_PAGE', cast=int, default=3),
            last)
        if res['pagination']:
            res['html'] = {'albums': request.app.jinja.get_template(
                'pictures/albums-list.html').render(
                request=request, pagination=res['pagination'])}
            if res['pagination']['next'] or res['pagination']['prev']:
                res['pv'] = True
        res['extra'] = res['pagination'] is None or \
                (res['pagination'] and res['pagination']['page'] == 1)
        res['stat'] = await get_user_stat(conn, cu.get('id'))
        await conn.close()
        return JSONResponse(res)

    async def post(self, request):
        res = {'done': None}
        d = await request.form()
        conn = await get_conn(request.app.config)
        cu = await checkcu(request, conn, d.get('auth'))
        if cu is None:
            res['message'] = 'Доступ ограничен, необходима авторизация.'
            await conn.close()
            return JSONResponse(res)
        if cu.get('weight') < 150:
            res['message'] = 'Доступ ограничен, у вас недостаточно прав.'
            await conn.close()
            return JSONResponse(res)
        title, state = d.get('title', ''), d.get('state')
        if not title or len(title) > 100 or \
                d.get('state') not in status:
            res['message'] = 'Запрос содержит неверные параметры.'
            await conn.close()
            return JSONResponse(res)
        rep = await conn.fetchval(
            '''SELECT suffix FROM albums
                 WHERE title = $1 AND author_id = $2''',
            title.strip(), cu.get('id'))
        if rep:
            res['message'] = 'Альбом с таким именем уже есть.'
            await conn.close()
            return JSONResponse(res)
        new = await create_new_album(
            conn, cu.get('id'), title.strip(), state.strip())
        await conn.close()
        res['done'] = True
        res['target'] = request.url_for('pictures:album', suffix=new)._url
        await set_flashed(request, 'Альбом успешно создан.')
        return JSONResponse(res)
