from util.database import ModelBase, DB


class TimeTracker(ModelBase):
    def __init__(self, hour, minute):
        self.hour = hour
        self.minute = minute
        self.redis = DB().redis
        self._key = self.key(self.hour, self.minute)

    async def users_for_time(self):
        return await self.redis.smembers(self._key)

    async def register_user(self, user_id):
        return await self.redis.sadd(self._key, str(user_id))

    async def unregister_user(self, user_id):
        return await self.redis.srem(self._key, str(user_id))
