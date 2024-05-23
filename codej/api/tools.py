from ..auth.attri import groups, kgroups


async def check_profile_permissions(request, cu, user, rel, data):
    data['rel'] = rel
    data['owner'] = cu.get('id') == user.get('uid')
    data['address'] = cu.get('id') == user.get('uid') or \
            (cu.get('weight') >= 200 and user.get('weight') < 250) or \
            cu.get('weight') >= 250
    data['chgroup'] = cu.get('id') != user.get('uid') and \
            cu.get('weight') == 255 or \
            (cu.get('weight') in (200, 250) and user.get('weight') < 200)
    if cu.get('weight') in (200, 250):
        data['groups'] = kgroups
    if cu.get('weight') == 255:
        data['groups'] = tuple(groups)


async def fix_bad_token(config):
    length = config.get('TOKEN_LENGTH')
    return f'Данные устарели, срок действия брелка {length} часов.'


async def define_target_url(request, account, token):
    if account.get('user_id'):
        return f'{request.url_for("index")}?realm=rpasswd&key={token}'
    return f'{request.url_for("index")}?realm=gpasswd&key={token}'
