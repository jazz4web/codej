async def fix_bad_token(config):
    length = config.get('TOKEN_LENGTH')
    return f'Данные устарели, срок действия брелка {length} часов.'


async def define_target_url(request, account, token):
    if account.get('user_id'):
        return f'{request.url_for("index")}?realm=rpasswd&key={token}'
    return f'{request.url_for("index")}?realm=gpasswd&key={token}'
