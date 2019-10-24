import aioredis
from util.config import Config
from util.singleton import Singleton


class DB(metaclass=Singleton):
    def __init__(self):
        self._redis = None
        self._redis_url = Config().get('db.redis.url')

    async def connect(self):
        if not self._redis:
            self._redis = await aioredis.create_redis_pool(self._redis_url, encoding='utf-8')

    async def scan(self, match='*'):
        cur = b'0'
        results = []
        while cur:
            cur, keys = await self.redis.scan(cur, match)
            results += keys
        return results

    @property
    def redis(self) -> aioredis.Redis:
        return self._redis

    @staticmethod
    def key(*args):
        return ':'.join(map(str, args))


class ModelBase:
    def key(self, *args):
        return DB.key(self.__class__.__name__, *args)


async def print_database(request=''):
    if not request:
        request = '*'
    print('-' * 100)
    print('request: ', request)
    db = DB()
    keys = await db.scan(request)
    for key in keys:
        t = await db.redis.type(key)
        if t == 'string':
            value = await db.redis.get(key)
        elif t == 'set':
            value = await db.redis.smembers(key)
        else:
            value = '???'

        print(f'{key} => ({t}) {value}')
    print('-' * 100)
