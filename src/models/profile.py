from aioredis import Redis
from util.database import ModelBase
import json


class Profile(ModelBase):
    def __init__(self, r: Redis, used_id):
        super().__init__(r)
        self.user_id = used_id

    def key_for_prop(self, prop):
        return self.key(self.user_id, prop)

    async def get_prop(self, prop, as_json=False):
        result = await self.r.get(self.key_for_prop(prop))
        if as_json:
            try:
                return json.loads(result)
            except (json.JSONDecodeError, TypeError):
                return {}
        else:
            return result

    async def set_prop(self, prop, value, expire=0):
        if isinstance(value, list) or isinstance(value, dict) or isinstance(value, tuple):
            value = json.dumps(value)
        return await self.r.set(self.key_for_prop(prop), value, expire=expire)

    async def dialog_state(self):
        return await self.get_prop('state', as_json=True)

    async def set_dialog_state(self, state):
        return await self.set_prop('state', state)
