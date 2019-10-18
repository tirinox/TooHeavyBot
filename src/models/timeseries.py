from util.database import DB, ModelBase
from dataclasses import dataclass
import json


@dataclass
class TimePoint(ModelBase):
    series_name: str = ""
    user_id: int = 0
    year: int = 2000
    month: int = 1
    day: int = 1
    value: float = 0.0
    real_ts: int = 0

    @property
    def key(self):
        return super().key(self.series_name, self.user_id, self.year, self.month, self.day)

    async def load(self):
        data = await DB().redis.get(self.key)
        j = json.loads(data)
        self.value = j['v']
        self.real_ts = j['ts']
        return self

    async def save(self):
        jv = json.dumps({
            'v': self.value,
            'ts': self.real_ts
        })
        await DB().redis.set(self.key, jv)
        return self
