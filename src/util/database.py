import aioredis
from util.config import Config
from util.singleton import Singleton
import json


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

    def __init__(self, ident):
        self.redis = DB().redis
        self._cache = {}
        self.ident = ident

    def key_for_prop(self, prop):
        return self.key(self.ident, prop)

    async def get_prop(self, prop, as_json=False, cached=True):
        if cached:
            if prop in self._cache:
                # print(f'{self.__class__.__name__}: cache get {self.ident} for prop {prop} = {self._cache[prop]}')
                return self._cache[prop]

        result = await self.redis.get(self.key_for_prop(prop))
        if as_json:
            try:
                result = self._cache[prop] = json.loads(result)
                # print(f'{self.__class__.__name__}: cache set {self.ident} for prop {prop} = {result}')
                return result
            except (json.JSONDecodeError, TypeError):
                return {}
        else:
            self._cache[prop] = result
            # print(f'{self.__class__.__name__}: cache set {self.ident} for prop {prop} = {result}')
            return result

    async def set_prop(self, prop, value, expire=0):
        if isinstance(value, list) or isinstance(value, dict) or isinstance(value, tuple):
            value = json.dumps(value)
        self._cache[prop] = value
        return await self.redis.set(self.key_for_prop(prop), value, expire=expire)

    async def del_prop(self, prop):
        await self.redis.delete(self.key_for_prop(prop))

    async def delete(self):
        for key in await DB().scan(self.key_for_prop('*')):
            await self.redis.delete(key)


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
