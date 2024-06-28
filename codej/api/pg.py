import asyncio
import functools
import math

from datetime import datetime, timedelta
from validate_email import validate_email

from ..auth.attri import groups
from ..common.aparsers import (
    iter_pages, parse_pic_filename, parse_title, parse_units, parse_url)
from ..common.random import get_unique_s
from ..drafts.attri import status
from .md import check_text, parse_md
from .parse import parse_art_query, parse_arts_query
from .slugs import check_max, make, parse_match


async def select_l_carts(
        request, conn, label, target, page, per_page, last):
    query = await conn.fetch(
        '''SELECT a.id, a.title, a.slug, a.suffix, a.summary, a.published,
                  a.edited, a.state, a.commented, a.viewed, users.username
             FROM articles AS a, users, labels, als
               WHERE a.id = als.article_id
                 AND a.author_id = users.id
                 AND labels.id = als.label_id
                 AND labels.label = $1
                 AND a.state = $2
             ORDER BY a.published DESC LIMIT $3 OFFSET $4''',
        label, status.cens, per_page, per_page*(page-1))
    if query:
        await parse_arts_query(request, conn, query, target, page, last)


async def check_cart(request, conn, slug, target):
    query = await conn.fetchrow(
        '''SELECT a.id, a.title, a.slug, a.suffix, a.html, a.summary,
                  a.meta, a.published, a.edited, a.state, a.commented,
                  a.viewed, a.author_id, u.username, u.weight
             FROM articles AS a, users AS u
             WHERE a.slug = $1
               AND u.id = a.author_id
               AND a.state = $2''', slug, status.cens)
    if query:
        await parse_art_query(request, conn, query, target)


async def select_carts(request, conn, target, page, per_page, last):
    query = await conn.fetch(
        '''SELECT a.id, a.title, a.slug, a.suffix, a.summary, a.published,
                  a.edited, a.state, a.commented, a.viewed, users.username
             FROM articles AS a, users
             WHERE a.author_id = users.id
               AND a.state = $1
             ORDER BY a.published DESC LIMIT $2 OFFSET $3''',
        status.cens, per_page, per_page*(page-1))
    if query:
        await parse_arts_query(request, conn, query, target, page, last)


async def select_l_followed(
        request, conn, uid, label, target, page, per_page, last):
    query = await conn.fetch(
        '''SELECT a.id, a.title, a.slug, a.suffix, a.summary, a.published,
                  a.edited, a.state, a.commented, a.viewed, u.username
             FROM articles AS a, users AS u, followers AS f, labels, als
             WHERE a.author_id = u.id
               AND a.author_id = f.author_id
               AND f.follower_id = $1
               AND a.id = als.article_id
               AND labels.label = $2
               AND labels.id = als.label_id AND a.state IN ($3, $4, $5)
             ORDER BY a.published ASC LIMIT $6 OFFSET $7''',
        uid, label, status.pub, status.priv, status.ffo,
        per_page, per_page*(page-1))
    if query:
        await parse_arts_query(request, conn, query, target, page, last)


async def select_followed(request, conn, target, uid, page, per_page, last):
    query = await conn.fetch(
        '''SELECT a.id, a.title, a.slug, a.suffix, a.summary, a.published,
                  a.edited, a.state, a.commented, a.viewed, u.username
             FROM articles AS a, users AS u, followers AS f
             WHERE a.author_id = u.id
               AND a.author_id = f.author_id
               AND a.state IN ($1, $2, $3)
               AND f.follower_id = $4
             ORDER BY a.published DESC LIMIT $5 OFFSET $6''',
        status.pub, status.priv, status.ffo, uid, per_page, per_page*(page-1))
    if query:
        await parse_arts_query(request, conn, query, target, page, last)


async def select_l_blog(
        request, conn, target, uid, label, page, per_page, last):
    query = await conn.fetch(
        '''SELECT a.id, a.title, a.slug, a.suffix, a.summary, a.published,
                  a.edited, a.state, a.commented, a.viewed, users.username
             FROM articles AS a, users, labels, als
             WHERE a.author_id = users.id
               AND a.author_id = $1
               AND a.id = als.article_id
               AND labels.label = $2
               AND labels.id = als.label_id
               AND a.state IN ($3, $4, $5)
             ORDER BY a.published ASC LIMIT $6 OFFSET $7''',
        uid, label, status.pub, status.priv, status.ffo,
        per_page, per_page*(page-1))
    if query:
        await parse_arts_query(request, conn, query, target, page, last)


async def select_authored(request, conn, target, uid, page, per_page, last):
    query = await conn.fetch(
        '''SELECT a.id, a.title, a.slug, a.suffix, a.summary, a.published,
                  a.edited, a.state, a.commented, a.viewed, users.username
             FROM articles AS a, users
             WHERE a.author_id = users.id
               AND a.author_id = $1
               AND a.state IN ($2, $3, $4)
             ORDER BY a.published DESC LIMIT $5 OFFSET $6''',
        uid, status.pub, status.priv, status.ffo, per_page, per_page*(page-1))
    if query:
        await parse_arts_query(request, conn, query, target, page, last)


async def select_authors(request, conn, target, page, per_page, last):
    query = await conn.fetch(
        '''SELECT id, username, registered, description, last_published
             FROM users WHERE last_published IS NOT null
               AND description IS NOT null
             ORDER BY last_published DESC LIMIT $1 OFFSET $2''',
        per_page, per_page*(page-1))
    if query:
        target['page'] = page
        target['next'] = page + 1 if page + 1 <= last else None
        target['prev'] = page - 1 or None
        target['pages'] = await iter_pages(page, last)
        target['blogs'] = [
            {'id': record.get('id'),
             'username': record.get('username'),
             'registered': f'{record.get("registered").isoformat()}Z',
             'description': record.get('description'),
             'last_published':
             f'{record.get("last_published").isoformat()}Z',
             'ava': request.url_for(
                 'ava', username=record.get('username'), size=98)._url}
             for record in query]


async def select_labeled_arts(
        request, conn, label, target, page, per_page, last):
    query = await conn.fetch(
        '''SELECT a.id, a.title, a.slug, a.suffix, a.summary, a.published,
                  a.edited, a.state, a.commented, a.viewed,
                  users.username
             FROM articles AS a, users, labels, als
               WHERE a.id = als.article_id
               AND a.author_id = users.id
               AND labels.id = als.label_id
               AND labels.label = $1
               AND a.state IN ($2, $3)
             ORDER BY a.published DESC LIMIT $4 OFFSET $5''',
        label, status.pub, status.priv, per_page, per_page*(page-1))
    if query:
        await parse_arts_query(request, conn, query, target, page, last)


async def select_arts(request, conn, target, page, per_page, last):
    query = await conn.fetch(
        '''SELECT a.id, a.title, a.slug, a.suffix, a.summary, a.published,
                  a.edited, a.state, a.commented, a.viewed, users.username
             FROM articles AS a, users
             WHERE a.author_id = users.id
               AND a.state IN ($1, $2)
             ORDER BY a.published DESC LIMIT $3 OFFSET $4''',
        status.pub, status.priv, per_page, per_page*(page-1))
    if query:
        await parse_arts_query(request, conn, query, target, page, last)


async def select_broadcast(conn, aid):
    res = list()
    adm = await conn.fetchrow(
        '''SELECT a.headline, a.html, a.published
             FROM announces AS a
             WHERE adm = true
               AND pub = true
               AND a.author_id != $1
             ORDER BY random() LIMIT 1''', aid)
    if adm:
        res.append({'headline': adm.get('headline'),
                    'html': adm.get('html'),
                    'published': f'{adm.get("published").isoformat()}Z'})
    auth = await conn.fetchrow(
        '''SELECT a.headline, a.html, a.published
             FROM announces AS a, users AS u
             WHERE a.author_id = $1
               AND u.id = a.author_id
               AND pub = true ORDER BY random() LIMIT 1''', aid)
    if auth:
        res.append({'headline': auth.get('headline'),
                    'html': auth.get('html'),
                    'published': f'{auth.get("published").isoformat()}Z'})
    return res


async def check_ann(conn, suffix, uid, target):
    query = await conn.fetchrow(
        'SELECT * FROM announces WHERE suffix = $1 AND author_id = $2',
        suffix, uid)
    if query:
        target['headline'] = query.get('headline')
        target['body'] = query.get('body')
        target['html'] = query.get('html')
        target['suffix'] = query.get('suffix')
        target['pub'] = query.get('pub')
        target['published'] = f'{query.get("published").isoformat()}Z'


async def select_announces(conn, uid, target, page, per_page, last):
    query = await conn.fetch(
        '''SELECT headline, html, suffix, pub, published, author_id
             FROM announces WHERE author_id = $1
             ORDER BY published DESC LIMIT $2 OFFSET $3''',
        uid, per_page, per_page*(page-1))
    if query:
        target['page'] = page
        target['next'] = page + 1 if page + 1 <= last else None
        target['prev'] = page - 1 or None
        target['pages'] = await iter_pages(page, last)
        target['announces'] = [
                {'headline': record.get('headline'),
                 'html': record.get('html'),
                 'suffix': record.get('suffix'),
                 'pub': record.get('pub'),
                 'published': f'{record.get("published").isoformat()}Z'}
                for record in query]


async def check_article(request, conn, slug, target):
    query = await conn.fetchrow(
        '''SELECT a.id, a.title, a.slug, a.suffix, a.html, a.summary,
                a.meta, a.published, a.edited, a.state, a.commented,
                a.viewed, a.author_id, u.username, u.ugroup, u.weight
             FROM articles AS a, users AS u
             WHERE a.slug = $1
               AND u.id = a.author_id
               AND a.state IN ($2, $3, $4)''',
        slug, status.pub, status.priv, status.ffo)
    if query:
        await parse_art_query(request, conn, query, target)


async def undress_art_links(conn, did):
    pars = await conn.fetch(
        '''SELECT mdtext FROM paragraphs
             WHERE article_id = $1 ORDER BY num ASC''', did)
    loop = asyncio.get_running_loop()
    html = await loop.run_in_executor(
        None, functools.partial(parse_md, pars, sc=True))
    if html:
        await conn.execute(
            'UPDATE articles SET html = $1 WHERE id = $2', html, did)


async def edit_par(conn, did, text, num, code):
    cur = await conn.fetchval(
        'SELECT mdtext FROM paragraphs WHERE num = $1 AND article_id = $2',
        num, did)
    if text == cur:
        return None
    loop = asyncio.get_running_loop()
    text, spec = await loop.run_in_executor(
        None, functools.partial(check_text, text, code))
    if spec and text:
        if await conn.fetchrow(
                '''SELECT num FROM paragraphs
                     WHERE mdtext = $1 AND article_id = $2''', text, did):
            text = None
    if text:
        await conn.execute(
            '''UPDATE paragraphs SET mdtext = $1
                 WHERE num = $2 AND article_id = $3''', text, num, did)
        return await update_art(conn, did, loop)


async def insert_par(conn, did, text, num, code):
    loop = asyncio.get_running_loop()
    text, spec = await loop.run_in_executor(
        None, functools.partial(check_text, text, code))
    if spec and text:
        if await conn.fetchrow(
                '''SELECT num FROM paragraphs
                     WHERE mdtext = $1 AND article_id = $2''', text, did):
            text = None
    if text:
        aft = await conn.fetch(
            '''SELECT num FROM paragraphs WHERE article_id = $1 AND num >= $2
                 ORDER BY num DESC''', did, num)
        for each in aft:
            await conn.execute(
                '''UPDATE paragraphs SET num = num + 1
                     WHERE num = $1 AND article_id = $2''', each.get('num'),
                did)
        await conn.execute(
            '''INSERT INTO paragraphs (num, mdtext, article_id)
                 VALUES ($1, $2, $3)''', num, text, did)
        return await update_art(conn, did, loop, withdate=False)


async def remove_par(conn, did, num):
    aft = await conn.fetch(
        '''SELECT num FROM paragraphs WHERE article_id = $1 AND num > $2
             ORDER BY num ASC''', did, num)
    await conn.execute(
        'DELETE FROM paragraphs WHERE num = $1 AND article_id = $2', num, did)
    if aft:
        for each in aft:
            await conn.execute(
                '''UPDATE paragraphs SET num = num - 1
                     WHERE num = $1 AND article_id = $2''',
                each .get('num'), did)
    pars = await conn.fetch(
        '''SELECT mdtext FROM paragraphs
             WHERE article_id = $1 ORDER BY num ASC''', did)
    if pars:
        loop = asyncio.get_running_loop()
        html = await loop.run_in_executor(
            None, functools.partial(parse_md, pars))
        await conn.execute(
            'UPDATE articles SET html = $1 WHERE id = $2', html, did)
        return html
    else:
        await conn.execute(
            '''UPDATE articles SET html = null, edited = $1,
                                   state = $2, published = null
                 WHERE id = $3''', datetime.utcnow(), status.draft, did)


async def update_art(conn, did, loop, withdate=True):
    pars = await conn.fetch(
        '''SELECT mdtext FROM paragraphs
             WHERE article_id = $1 ORDER BY num ASC''', did)
    html = await loop.run_in_executor(
        None, functools.partial(parse_md, pars))
    if html:
        if withdate:
            await conn.execute(
                'UPDATE articles SET html = $1, edited = $2 WHERE id = $3',
                html, datetime.utcnow(), did)
        else:
            await conn.execute(
                'UPDATE articles SET html = $1 WHERE id = $2', html, did)
    return html


async def save_par(conn, did, text, code):
    loop = asyncio.get_running_loop()
    text, spec = await loop.run_in_executor(
        None, functools.partial(check_text, text, code))
    if spec and text:
        if await conn.fetchrow(
                '''SELECT num FROM paragraphs
                     WHERE mdtext = $1 AND article_id = $2''', text, did):
            text = None
    if text:
        last = await conn.fetchval(
            '''SELECT num FROM paragraphs
                 WHERE article_id = $1 ORDER BY num DESC''', did)
        if last is None:
            last = -1
        await conn.execute(
            '''INSERT INTO paragraphs (num, mdtext, article_id)
                 VALUES ($1, $2, $3)''', last+1, text, did)
        return await update_art(conn, did, loop)


async def change_draft(request, conn, did, field, value):
    q = f'UPDATE articles SET {field} = $1 WHERE id = $2'
    if field == 'meta':
        value = value.strip()[:180]
        await conn.execute(q, value, did)
    elif field == 'state':
        if value in status:
            await conn.execute(q, value, did)
            published = await conn.fetchrow(
                'SELECT published, author_id FROM articles WHERE id = $1', did)
            if published.get('published') is None and \
                    value in (status.pub, status.priv, status.ffo):
                now = datetime.utcnow()
                await conn.execute(
                    '''UPDATE articles SET published = $1, edited = $1
                         WHERE id = $2''', now, did)
                await conn.execute(
                    'UPDATE users SET last_published = $1 WHERE id = $2',
                    now, published.get('author_id'))
    elif field == 'summary':
        value = value.strip()[:512]
        await conn.execute(q, value, did)
    elif field == 'commented':
        value = await conn.fetchval(
            'SELECT commented FROM articles WHERE id = $1', did)
        await conn.execute(q, not value, did)
    elif field == 'title':
        value = value.strip()[:100]
        slug = await check_slug(conn, value)
        await conn.execute(
            'UPDATE articles SET title = $1, slug = $2 WHERE id = $3',
            value, slug, did)
        return slug


async def select_labeled_drafts(
        request, conn, uid, label, target, page, per_page, last):
    query = await conn.fetch(
        '''SELECT a.id, a.title, a.slug, a.suffix, a.summary, a.published,
                  a.edited, a.state, a.commented, a.viewed,
                  users.username
             FROM articles AS a, users, labels, als
             WHERE a.author_id = users.id
               AND a.author_id = $1
               AND a.id = als.article_id
               AND labels.label = $2
               AND labels.id = als.label_id
               AND a.state IN ($3, $4)
            ORDER BY a.edited DESC LIMIT $5 OFFSET $6''',
        uid, label, status.draft, status.cens, per_page, per_page*(page-1))
    if query:
        await parse_arts_query(request, conn, query, target, page, last)


async def check_draft(request, conn, slug, cuid, target):
    query = await conn.fetchrow(
        '''SELECT articles.id, articles.title, articles.slug,
                  articles.suffix, articles.html, articles.summary,
                  articles.meta, articles.published, articles.edited,
                  articles.state, articles.commented, articles.viewed,
                  articles.author_id, users.username
             FROM articles, users
             WHERE articles.slug = $1
               AND articles.author_id = $2
               AND users.id = articles.author_id''',
        slug, cuid)
    if query:
        await parse_art_query(request, conn, query, target)


async def check_slug(conn, title):
    loop = asyncio.get_running_loop()
    slug = await loop.run_in_executor(
        None, functools.partial(make, title))
    match = await conn.fetch(
        'SELECT slug FROM articles WHERE slug LIKE $1', f'{slug}%')
    match = await loop.run_in_executor(
        None, functools.partial(parse_match, match))
    if not match or slug not in match:
        return slug
    maxi = await loop.run_in_executor(
        None, functools.partial(check_max, match, slug))
    return f'{slug}-{maxi+1}'


async def create_d(conn, title, uid):
    suffix = await get_unique_s(conn, 'articles', 8)
    slug = await check_slug(conn, title)
    now = datetime.utcnow()
    empty = await conn.fetchval(
        'SELECT id FROM articles WHERE author_id IS NULL')
    if empty:
        await conn.execute(
            '''UPDATE articles
                 SET title = $1, slug = $2, suffix = $3,
                     edited = $4, state = $5, author_id = $6
                 WHERE id = $7''',
            title, slug, suffix, now, status.draft, uid, empty)
    else:
        await conn.execute(
            '''INSERT INTO articles
               (title, slug, suffix, edited, state, author_id)
               VALUES ($1, $2, $3, $4, $5, $6)''',
            title, slug, suffix, now, status.draft, uid)
    return slug


async def select_drafts(request, conn, uid, target, page, per_page, last):
    query = await conn.fetch(
        '''SELECT a.id, a.title, a.slug, a.suffix, a.summary, a.published,
                  a.edited, a.state, a.commented, a.viewed, users.username
             FROM articles AS a, users
             WHERE a.author_id = users.id
               AND a.author_id = $1
               AND a.state IN ($2, $3)
             ORDER BY a.edited DESC LIMIT $4 OFFSET $5''',
        uid, status.draft, status.cens, per_page, per_page*(page-1))
    if query:
        await parse_arts_query(request, conn, query, target, page, last)


async def get_pic_stat(request, conn, uid, suffix):
    query = await conn.fetchrow(
        '''SELECT pictures.uploaded, pictures.filename, pictures.width,
                  pictures.height, pictures.format, pictures.volume,
                  pictures.suffix, albums.author_id FROM pictures, albums
             WHERE pictures.album_id = albums.id
               AND albums.author_id = $1 AND pictures.suffix = $2''',
        uid, suffix)
    if query:
        return {'uploaded': f'{query.get("uploaded").isoformat()}Z',
                'filename': query.get('filename'),
                'width': query.get('width'),
                'height': query.get('height'),
                'format': query.get('format'),
                'volume': await parse_units(query.get('volume')),
                'suffix': query.get('suffix'),
                'url': request.url_for(
                    'picture', suffix=query.get('suffix'))._url,
                'path': request.app.url_path_for(
                    'picture', suffix=query.get('suffix')),
                'parsed15': await parse_pic_filename(
                    query.get('filename'), 15),
                'parsed25': await parse_pic_filename(
                    query.get('filename'), 20)}


async def select_pictures(conn, aid, page, per_page, last):
    query = await conn.fetch(
        '''SELECT filename, suffix FROM pictures
             WHERE album_id = $1
             ORDER BY uploaded DESC LIMIT $2 OFFSET $3''',
        aid, per_page, per_page*(page-1))
    if query:
        return {'page': page,
                'next': page + 1 if page + 1 <= last else None,
                'prev': page - 1 or None,
                'pages': await iter_pages(page, last),
                'pictures': [{'filename': record.get('filename'),
                              'parsed40': await parse_pic_filename(
                                  record.get('filename'), 30),
                              'suffix': record.get('suffix')}
                             for record in query]}


async def get_user_stat(conn, uid):
    return {'albums': await conn.fetchval(
        'SELECT count(*) FROM albums WHERE author_id = $1', uid),
            'files': await conn.fetchval(
        '''SELECT count(*) FROM albums, pictures
             WHERE author_id = $1
             AND pictures.album_id = albums.id''', uid),
            'volume': await parse_units(await conn.fetchval(
        'SELECT sum(volume) FROM albums WHERE author_id = $1', uid) or 0)}


async def get_album(conn, uid, suffix):
    query = await conn.fetchrow(
        '''SELECT id, title, created, suffix, state, volume FROM albums
             WHERE suffix = $1 AND author_id = $2''',
        suffix, uid)
    if query:
        num = await conn.fetchval(
            'SELECT count(*) FROM pictures WHERE album_id = $1',
            query.get('id'))
        return {'id': query.get('id'),
                'title': query.get('title'),
                'created': f'{query.get("created").isoformat()}Z',
                'suffix': query.get('suffix'),
                'state': query.get('state'),
                'volume_': query.get('volume'),
                'volume': await parse_units(query.get('volume')),
                'files': num,
                'parse_t': len(query.get('title')) > 50,
                'parsed22': await parse_title(query.get('title'), 22),
                'parsed36': await parse_title(query.get('title'), 36),
                'parsed50': await parse_title(query.get('title'), 50)}
    return None


async def create_new_album(conn, uid, title, state):
    now = datetime.utcnow()
    suffix = await get_unique_s(conn, 'albums', 8)
    empty = await conn.fetchval(
        'SELECT id FROM albums WHERE author_id IS NULL')
    if empty:
        await conn.execute(
            '''UPDATE albums SET title = $1,
                                 created = $2,
                                 changed = $2,
                                 suffix = $3,
                                 state = $4,
                                 volume = 0,
                                 author_id = $5 WHERE id = $6''',
            title, now, suffix, state, uid, empty)
    else:
        await conn.execute(
            '''INSERT INTO
                 albums (title, created, changed, suffix, state, author_id)
                 VALUES ($1, $2, $2, $3, $4, $5)''',
            title, now, suffix, state, uid)
    return suffix


async def get_user_stat(conn, uid):
    return {'albums': await conn.fetchval(
        'SELECT count(*) FROM albums WHERE author_id = $1', uid),
            'files': await conn.fetchval(
        '''SELECT count(*) FROM albums, pictures
             WHERE author_id = $1
             AND pictures.album_id = albums.id''', uid),
            'volume': await parse_units(await conn.fetchval(
        'SELECT sum(volume) FROM albums WHERE author_id = $1', uid) or 0)}


async def select_albums(conn, uid, page, per_page, last):
    query = await conn.fetch(
        '''SELECT title, suffix FROM albums
             WHERE author_id = $1
             ORDER BY changed DESC LIMIT $2 OFFSET $3''',
        uid, per_page, per_page*(page-1))
    if query:
        return {'page': page,
                'next': page + 1 if page + 1 <= last else None,
                'prev': page - 1 or None,
                'pages': await iter_pages(page, last),
                'albums': [{'title': record.get('title'),
                            'parsed': await parse_title(
                                record.get('title'), 40),
                            'suffix': record.get('suffix')}
                           for record in query]}
    return None


async def select_aliases(request, conn, uid, target, page, per_page, last):
    query = await conn.fetch(
        '''SELECT url, created, clicked, suffix FROM aliases
             WHERE author_id = $1
             ORDER BY created DESC LIMIT $2 OFFSET $3''',
        uid, per_page, per_page*(page-1))
    if query:
        target['page'] = page
        target['next'] = page + 1 if page + 1 <= last else None
        target['prev'] = page - 1 or None
        target['pages'] = await iter_pages(page, last)
        target['aliases'] = [
            {'url': record.get('url'),
             'parsed': await parse_url(record.get('url')),
             'created': f'{record.get("created").isoformat()}Z',
             'clicked': record.get('clicked'),
             'suffix': record.get('suffix'),
             'alias': request.url_for(
                 'jump', suffix=record.get('suffix'))._url}
             for record in query]


async def select_users(
        request, conn, uid, is_admin, target, page, per_page, last):
    if is_admin:
        query = await conn.fetch(
            '''SELECT username, ugroup, registered, last_visit
                 FROM users WHERE id != $1
                 ORDER BY last_visit DESC LIMIT $2 OFFSET $3''',
            uid, per_page, per_page*(page-1))
    else:
        query = await conn.fetch(
            '''SELECT username, ugroup, registered, last_visit
                 FROM users WHERE id != $1 AND weight > 0
                 ORDER BY last_visit DESC LIMIT $2 OFFSET $3''',
            uid, per_page, per_page*(page-1))
    if query:
        target['page'] = page
        target['next'] = page + 1 if page + 1 <= last else None
        target['prev'] = page - 1 or None
        target['pages'] = await iter_pages(page, last)
        target['users'] = [
            {'username': record.get('username'),
             'group': record.get('ugroup'),
             'last_visit': f'{record.get("last_visit").isoformat()}Z',
             'registered': f'{record.get("registered").isoformat()}Z',
             'ava': request.url_for(
                 'ava', username=record.get('username'), size=98)._url}
            for record in query]


async def check_last(conn, page, per_page, *args):
    num = await conn.fetchval(*args)
    return math.ceil(num / per_page) or 1


async def check_account(config, conn, account, address):
    length = timedelta(
        seconds=round(3600*config.get('TOKEN_LENGTH', cast=float)))
    interval = timedelta(
        seconds=round(3600*config.get('REQUEST_INTERVAL', cast=float)))
    if datetime.utcnow() - account.get('requested') < interval:
        return 'Сервис временно недоступен, попробуйте зайти позже.'
    if account.get('address') == address:
        return 'Задан Ваш текущий адрес, запрос не имеет смысла.'
    if await check_swap(conn, address, length):
        return 'Адрес в свопе, выберите другой или повторите попытку позже.'
    requested = await conn.fetchrow(
        'SELECT requested, user_id FROM accounts WHERE address = $1', address)
    if requested and requested.get('user_id'):
        return 'Этот адрес уже зарегистрирован, запрос отклонён.'
    if requested and datetime.utcnow() - requested.get('requested') < length:
        return 'Адрес регистрируется, выберите другой или попробуйте позже.'
    return None


async def check_rel(conn, uid1, uid2):
    friend = bool(await conn.fetchrow(
        '''SELECT author_id, friend_id FROM friends
             WHERE author_id = $1 AND friend_id = $2''', uid1, uid2))
    follower = bool(await conn.fetchrow(
        '''SELECT author_id, follower_id FROM followers
             WHERE author_id = $1 AND follower_id = $2''', uid1, uid2))
    blocker = bool(await conn.fetchrow(
        '''SELECT target_id, blocker_id FROM blockers
             WHERE target_id = $1 AND blocker_id = $2''', uid2, uid1))
    blocked = bool(await conn.fetchrow(
        '''SELECT target_id, blocker_id FROM blockers
             WHERE target_id = $1 AND blocker_id = $2''', uid1, uid2))
    return {'friend': friend, 'follower': follower,
            'blocker': blocker, 'blocked': blocked}


async def filter_target_user(request, conn, username):
    query = await conn.fetchrow(
        '''SELECT id, username, ugroup, weight, registered,
                  last_visit, description, last_published FROM users
             WHERE username = $1''', username)
    if query:
        return {'uid': query.get('id'),
                'username': query.get('username'),
                'group': query.get('ugroup'),
                'weight': query.get('weight'),
                'registered': f'{query.get("registered").isoformat()}Z',
                'last_visit': f'{query.get("last_visit").isoformat()}Z',
                'description': query.get('description'),
                'last_published': f'{query.get("last_published").isoformat()}Z'
                if query.get('last_published') else None,
                'ava': request.url_for(
                    'ava', username=query.get('username'), size=160)._url}


async def define_acc(conn, account):
    if account and account.get('user_id'):
        username = await conn.fetchval(
            'SELECT username FROM users WHERE id = $1', account.get('user_id'))
        return username, 'Сброс забытого пароля', 'emails/resetpwd.html'
    return 'Гость', 'Регистрация', 'emails/invitation.html'


async def get_acc(conn, account, address):
    now = datetime.utcnow()
    if account:
        address = account.get('address')
        await conn.execute(
            '''UPDATE accounts SET swap = null, requested = $1
                 WHERE address = $2''', now, address)
    else:
        await conn.execute(
            '''INSERT INTO accounts (address, requested)
                 VALUES ($1, $2)''', address, now)
    return await conn.fetchrow(
        'SELECT id, address, user_id FROM accounts WHERE address = $1',
        address)


async def check_swap(conn, address, length):
    swapped = await conn.fetchrow(
        'SELECT id, swap, requested FROM accounts WHERE swap = $1', address)
    if swapped:
        if datetime.utcnow() - swapped.get('requested') > length:
            await conn.execute(
                'UPDATE accounts SET swap = null WHERE id = $1',
                swapped.get('id'))
            return None
        else:
            return True


async def check_address(request, conn, address):
    message = None
    interval = timedelta(
        seconds=round(
            3600*request.app.config.get('REQUEST_INTERVAL', cast=float)))
    length = timedelta(
        seconds=round(
            3600*request.app.config.get('TOKEN_LENGTH', cast=float)))
    acc = await conn.fetchrow(
        'SELECT address, requested, user_id FROM accounts WHERE address = $1',
        address)
    if acc and datetime.utcnow() - acc.get('requested') < interval:
        message = 'Сервис временно недоступен, попробуйте зайти позже.'
    if await check_swap(conn, address, length):
        message = 'Адрес в свопе, выберите другой или повторите попытку позже.'
    return message, acc


async def create_session(config, conn, rme, user, brkey):
    now = datetime.utcnow()
    if rme:
        expire = now + timedelta(
            seconds=config.get('SESSION_LIFETIME', cast=int))
    else:
        expire = now + timedelta(seconds=2*60*60)
    suffix = await get_unique_s(conn, 'sessions', 13)
    await conn.execute(
        '''INSERT INTO sessions (suffix, brkey, logedin, expire, user_id)
             VALUES ($1, $2, $3, $4, $5)''',
        suffix, brkey, now, expire, user.get('id'))
    return suffix, now


async def filter_user(conn, login):
    squery = '''SELECT users.id, users.username,
                       users.password_hash, users.ugroup
                  FROM users, accounts
                    WHERE users.id = accounts.user_id '''
    if validate_email(login):
        squery += ' AND accounts.address = $1'
    else:
        squery += ' AND users.username = $1'
    query = await conn.fetchrow(squery, login)
    if query and query.get('ugroup') != groups.pariah:
        return {'id': query.get('id'),
                'username': query.get('username'),
                'password_hash': query.get('password_hash')}
