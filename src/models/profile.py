from util.database import ModelBase, DB
import json


class Profile(ModelBase):
    def __init__(self, user_id):
        self.user_id = user_id
        self.redis = DB().redis

    def key_for_prop(self, prop):
        return self.key(self.user_id, prop)

    async def get_prop(self, prop, as_json=False):
        result = await self.redis.get(self.key_for_prop(prop))
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
        return await self.redis.set(self.key_for_prop(prop), value, expire=expire)

    async def dialog_state(self):
        return await self.get_prop('state', as_json=True)

    async def set_dialog_state(self, state):
        if state is None:
            return await self.redis.delete(key=self.key_for_prop('state'))
        else:
            return await self.set_prop('state', state)

    async def set_time_shift(self, timeshift):
        return await self.set_prop('tz_offset_min', timeshift)

    async def get_time_shift(self):
        r = await self.get_prop('tz_offset_min')
        return r if r is None else int(r)

    async def delete(self):
        for key in await DB().scan(self.key_for_prop('*')):
            await self.redis.delete(key)
