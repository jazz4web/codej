import asyncpg


async def get_conn(config):
    if dsn := config.get('DSN'):
        conn = await asyncpg.connect(dsn)
    else:
        conn = await asyncpg.connect(
            user=config.get('USER'), database=config.get('DB'))
    return conn
