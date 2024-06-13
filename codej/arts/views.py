from starlette.responses import PlainTextResponse


async def show_arts(request):
    return PlainTextResponse('Сайт в стадии разработки, зайдите позже.')


async def show_art(request):
    slug = request.path_params.get('slug')
    return PlainTextResponse(f'{slug}')
