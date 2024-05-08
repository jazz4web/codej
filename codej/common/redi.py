import redis.asyncio as redis


async def get_rc(request, future=False):
    if future:
        return redis.from_url(
            request.app.config.get('REDI'), decode_responses=True)
    return redis.Redis.from_pool(request.app.rp)
