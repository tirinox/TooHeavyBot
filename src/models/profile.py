from util.database import ModelBase, DB
from util.date import now_tsi, now_local_dt
import json
import pytz
from datetime import datetime


class Profile(ModelBase):
    DIALOG_STATE_KEY = 'state'
    NOTIFICATION_TIME_KEY = 'notif_time'
    TIME_ZONE_KEY = 'tz_name'
    LAST_ACTIVITY_KEY = 'last_activity'

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

    async def del_prop(self, prop):
        await self.redis.delete(self.key_for_prop(prop))

    async def delete(self):
        for key in await DB().scan(self.key_for_prop('*')):
            await self.redis.delete(key)

    # ----

    async def dialog_state(self):
        return await self.get_prop(self.DIALOG_STATE_KEY, as_json=True)

    async def set_dialog_state(self, state):
        if state is None:
            return await self.redis.delete(key=self.key_for_prop(self.DIALOG_STATE_KEY))
        else:
            return await self.set_prop(self.DIALOG_STATE_KEY, state)

    async def set_time_zone(self, tz_name):
        return await self.set_prop(self.TIME_ZONE_KEY, tz_name)

    async def get_time_zone(self):
        return await self.get_prop(self.TIME_ZONE_KEY)

    async def get_their_time(self, dt: datetime):
        try:
            tz = pytz.timezone(await self.get_time_zone())
        except pytz.UnknownTimeZoneError:
            tz = pytz.UTC

        return dt.astimezone(tz)

    async def get_their_now(self):
        return await self.get_their_time(now_local_dt())

    async def activity(self):
        return await self.set_prop(self.LAST_ACTIVITY_KEY, now_tsi())

    async def get_last_activity_ts(self):
        r = await self.get_prop(self.LAST_ACTIVITY_KEY)
        return 0 if r is None else int(r)
