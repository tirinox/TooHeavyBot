from util import gen_id
from util.database import ModelBase
from util.date import now_tsi


class Group(ModelBase):
    MEMBERS_KEY = 'members'
    CREATED_DATE_KEY = 'created_dt'

    async def get_members(self):
        return set(await self.redis.smembers(self.key(self.MEMBERS_KEY)))

    async def user_join(self, profile_ident):
        return await self.redis.sadd(self.key(self.MEMBERS_KEY), profile_ident)

    async def user_leave(self, profile_ident):
        return await self.redis.srem(self.key(self.MEMBERS_KEY), profile_ident)

    @classmethod
    async def new_group(cls):
        group_ident = gen_id()
        group = Group(group_ident)
        await group.redis.set(group.key(cls.CREATED_DATE_KEY), now_tsi())
        return group

    async def remove(self):
        await self.redis.delete(keys=[
            self.key(self.MEMBERS_KEY),
            self.key(self.CREATED_DATE_KEY)
        ])

