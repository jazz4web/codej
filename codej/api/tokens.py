from datetime import timedelta

from jwt import encode as jwtencode


async def create_login_token(request, rme, cache, now):
    if rme:
        delta = timedelta(
            seconds=request.app.config.get('SESSION_LIFETIME', cast=int))
    else:
        delta = timedelta(seconds=2*60*60)
    d = {'cache': cache, 'exp': now + delta}
    return jwtencode(
        d, request.app.config.get('SECRET_KEY'), algorithm='HS256')
