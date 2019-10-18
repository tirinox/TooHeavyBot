import aioredis
from util.config import Config


async def get_db_by_url(url):
    return await aioredis.create_redis_pool(url, encoding='utf-8')


async def get_db():
    url = Config().get('db.redis.url')
    return await get_db_by_url(url)


def key(*args):
    return ':'.join(map(str, args))


class ModelBase:
    def __init__(self, r: aioredis.Redis):
        self.r = r

    def key(self, *args):
        return key(self.__class__.__name__, *args)


async def scan(r: aioredis.Redis, match='*'):
    cur = b'0'
    while cur:
        cur, keys = await r.scan(cur, match)
        for k in keys:
            yield k
