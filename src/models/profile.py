from aioredis import Redis
from util.database import key, ModelBase


class Profile(ModelBase):
    def __init__(self, r: Redis, used_id):
        super().__init__(r)
        self.user_id = used_id

    async def dialog_state(self):
        return await self.r.get(self.key(self.user_id, 'state'))

    async def set_dialog_state(self, state):
        return await self.r.set(self.key(self.user_id, 'state'), state)
