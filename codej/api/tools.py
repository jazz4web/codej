async def check_profile_permissions(request, cu, user, rel, data):
    data['rel'] = rel
    data['owner'] = cu.get('id') == user.get('uid')
    data['address'] = cu.get('id') == user.get('uid') or \
            (cu.get('weight') >= 200 and user.get('weight') < 250) or \
            cu.get('weight') >= 250


async def fix_bad_token(config):
    length = config.get('TOKEN_LENGTH')
    return f'Данные устарели, срок действия брелка {length} часов.'


async def define_target_url(request, account, token):
    if account.get('user_id'):
        return f'{request.url_for("index")}?realm=rpasswd&key={token}'
    return f'{request.url_for("index")}?realm=gpasswd&key={token}'
