from util.database import ModelBase, DB


class TimeTracker(ModelBase):
    def __init__(self, name, hour, minute):
        super().__init__(0)
        self.hour = hour
        self.minute = minute
        self.name = name
        self._key = self.key(self.name, self.hour, self.minute)

    async def list(self):
        return await self.redis.smembers(self._key)

    async def register_user(self, user_id):
        return await self.redis.sadd(self._key, str(user_id))

    async def unregister_user(self, user_id):
        return await self.redis.srem(self._key, str(user_id))

    async def delete(self):
        return await self.redis.delete(self._key)
