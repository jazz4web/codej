async def define_target_url(request, account, token):
    if account.get('user_id'):
        return f'{request.url_for("index")}?realm=rpasswd&key={token}'
    return f'{request.url_for("index")}?realm=gpasswd&key={token}'
