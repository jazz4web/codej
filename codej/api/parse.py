from ..common.aparsers import iter_pages, parse_title

LABELS = '''SELECT labels.label FROM articles, labels, als
              WHERE articles.id = als.article_id
                AND labels.id = als.label_id
                AND articles.id = $1'''


async def parse_art_query(request, conn, query, target):
    target['id'] = query.get('id')
    target['title'] = query.get('title')
    target['title80'] = await parse_title(query.get('title'), 80)
    target['slug'] = query.get('slug')
    target['suffix'] = query.get('suffix')
    if html := query.get('html'):
        target['html'] = html
    else:
        target['html'] = None
    target['summary'] = query.get('summary')
    target['meta'] = query.get('meta')
    target['published'] = f'{query.get("published").isoformat()}Z' \
            if query.get('published') else None
    target['edited'] = f'{query.get("edited").isoformat()}Z'
    target['state'] = query.get('state')
    target['commented'] = query.get('commented')
    target['viewed'] = query.get('viewed')
    target['author'] = query.get('username')
    target['author_perms'] = query.get('permissions')
    target['author_id'] = query.get('author_id')
    target['ava'] = request.url_for(
        'ava', username=query.get('username'), size=98)._url
    target['jump'] = request.url_for('jump', suffix=query.get('suffix'))._url
    target['likes'] = await conn.fetchval(
        'SELECT count(*) FROM likes WHERE article_id = $1', query.get('id'))
    target['dislikes'] = await conn.fetchval(
        'SELECT count(*) FROM dislikes WHERE article_id = $1', query.get('id'))
    target['commentaries'] = await conn.fetchval(
        '''SELECT count(*) FROM commentaries
             WHERE article_id = $1 AND deleted = false''',
        query.get('id'))
    target['labels'] = [label.get('label') for label in await conn.fetch(
        LABELS, query.get('id'))]


async def parse_arts_query(request, conn, query, target, page, last):
    target['page'] = page
    target['next'] = page + 1 if page + 1 <= last else None
    target['prev'] = page - 1 or None
    target['pages'] = await iter_pages(page, last)
    target['articles'] = [
            {'id': record.get('id'),
             'title': record.get('title'),
             'title80': await parse_title(record.get('title'), 80),
             'slug': record.get('slug'),
             'suffix': record.get('suffix'),
             'summary': record.get('summary'),
             'published': f'{record.get("published").isoformat()}Z'
             if record.get('published') else None,
             'edited': f'{record.get("edited").isoformat()}Z',
             'state': record.get('state'),
             'commented': record.get('commented'),
             'viewed': record.get('viewed'),
             'author': record.get('username'),
             'ava': request.url_for(
                 'ava', username=record.get('username'), size=98)._url,
             'likes': await conn.fetchval(
                 'SELECT count(*) FROM likes WHERE article_id = $1',
                 record.get('id')),
             'dislikes': await conn.fetchval(
                 'SELECT count(*) FROM dislikes WHERE article_id = $1',
                 record.get('id')),
             'commentaries': await conn.fetchval(
                 '''SELECT count(*) FROM commentaries
                      WHERE article_id = $1 AND deleted = false''',
                  record.get('id')),
             'labels': [label.get('label') for label in await conn.fetch(
                 LABELS, record.get('id'))]} for record in query]
