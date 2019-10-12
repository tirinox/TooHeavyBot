from dataclasses import dataclass
from aioredis import Redis


def make_key(entity_name, ident):
    return ':'.join(map(str, (entity_name, ident)))


@dataclass
class Base:
    ident: int = 0

    @classmethod
    async def load(cls, r: Redis, ident):
        o = cls(ident=ident)
        data = await r.hgetall(make_key(cls.__name__, ident))
        for k, v in data.items():
            setattr(o, k, v)
        return o

    @property
    def key(self):
        return make_key(self.__class__.__name__, self.ident)

    async def save(self, r: Redis):
        key = self.key
        for k, v in self.__dict__.items():
            if not k.startswith('_'):
                await r.hset(key, k, v)



