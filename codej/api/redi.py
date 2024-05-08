from ..common.random import randomize
from ..common.redi import get_rc


async def get_unique(conn, prefix, num):
    while True:
        res = prefix + await randomize(num)
        if await conn.exists(res):
            continue
        return res


async def assign_cache(request, prefix, suffix, val, expiration):
    rc = await get_rc(request)
    cache = await get_unique(rc, prefix, 6)
    await rc.hmset(cache, {'suffix': suffix, 'val': val})
    await rc.expire(cache, expiration)
    await rc.close()
    return cache
