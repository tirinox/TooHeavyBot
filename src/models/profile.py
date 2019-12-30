from datetime import datetime

import pytz

from localization import get_localization
from util.database import ModelBase
from util.date import now_tsi, now_local_dt


class Profile(ModelBase):
    DIALOG_STATE_KEY = 'state'
    NOTIFICATION_TIME_KEY = 'notif_time'
    TIME_ZONE_KEY = 'tz_name'
    LAST_ACTIVITY_KEY = 'last_activity'
    LANGUAGE_KEY = 'lang'

    async def get_language(self):
        return await self.get_prop(self.LANGUAGE_KEY)

    async def set_language(self, lang):
        self._language = lang
        await self.set_prop(self.LANGUAGE_KEY, lang)

    async def get_translator(self):
        lang_name = await self.get_language()
        return get_localization(lang_name)

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

    async def get_their_time(self, dt: datetime) -> datetime:
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
