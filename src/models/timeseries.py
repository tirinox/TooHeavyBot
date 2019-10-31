from util.database import DB, ModelBase
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class TimePoint(ModelBase):
    user_id: int = 0
    date: datetime = datetime.now()
    value: dict = None

    @property
    def key(self):
        return super().key(self.user_id, self.date.year, self.date.month, self.date.day)

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

    def __repr__(self):
        return f'{self.__class__.__name__}(user_id={self.user_id}, ' \
               f'year={self.date.year}, month={self.date.month}, day={self.date.day})'

    def get_value_prop(self, prop):
        return None if not isinstance(self.value, dict) else self.value.get(prop, None)

    def set_value_prop(self, prop, value):
        if not isinstance(self.value, dict):
            self.value = {}
        self.value[prop] = value
        return self
