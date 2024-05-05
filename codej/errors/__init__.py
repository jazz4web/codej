E404 = 'Такой страницы у нас нет.'


async def show_error(request, exc):
    if exc.status_code == 404 and exc.detail != E404:
        exc.detail = E404
    return request.app.jinja.TemplateResponse(
        'errors/error.html',
        {'reason': exc.detail,
         'request': request,
         'error': exc.status_code},
        status_code=exc.status_code)
