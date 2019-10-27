from util.database import DB, ModelBase
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class TimePoint(ModelBase):
    series_name: str = ""
    user_id: int = 0
    date: datetime = datetime.now()
    value: dict = None

    @property
    def key(self):
        return super().key(self.series_name, self.user_id, self.date.year, self.date.month, self.date.day)

    async def load(self):
        data = await DB().redis.get(self.key)
        try:
            self.value = json.loads(data)
        except (json.JSONDecodeError, TypeError):
            self.value = {}
        return self

    async def save(self):
        await DB().redis.set(self.key, json.dumps(self.value))
        return self
