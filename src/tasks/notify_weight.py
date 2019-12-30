import asyncio
import logging

from chat.message_handler import MessageHandler
from chat.msg_io import DialogIO
from dialogs.aim_percent import ask_current_weight
from models.profile import Profile
from models.time_tracker import TimeTracker
from tasks.weight_control import WeightProfile
from util.database import DB
from util.date import *


class WeightNotifier:
    KEY_NOTIFICATION_TIME = 'notification_time'
    KEY_WEIGHT_TRACKER = 'weight_tracker'
    KEY_LAST_SENT_TS = 'last_sent_ts'

    NOTIFICATION_COOLDOWN = parse_timespan_to_seconds('1m')

    def __init__(self, handler: MessageHandler):
        self.handler = handler

    @classmethod
    async def activate_notification(cls, profile: Profile, hh, mm):
        """
        Activate weight notification for the user
        :param profile: Profile for notification
        :param hh: hour (his)
        :param mm: minutes (his)
        :return: seconds to next notification
        """
        await cls.deactivate_notification(profile)

        await profile.set_prop(cls.KEY_NOTIFICATION_TIME, f'{hh}:{mm}')

        tz = await profile.get_time_zone()
        if tz is None:
            logging.error(f'time zone is not set for user {profile.ident}!')
            return

        local_hh, local_mm = convert_time_hh_mm_to_local(hh, mm, tz)

        tr = TimeTracker(cls.KEY_WEIGHT_TRACKER, local_hh, local_mm)
        await tr.register_user(profile.ident)

        return delta_to_next_hh_mm(local_hh, local_mm)

    @classmethod
    async def deactivate_notification(cls, profile: Profile):
        tz = await profile.get_time_zone()
        if tz is None:
            logging.error(f'time zone is not set for user {profile.ident}!')
            return

        current_time_str = await profile.get_prop(cls.KEY_NOTIFICATION_TIME)

        try:
            hh, mm = hour_and_min_from_str(current_time_str)

            await profile.del_prop(cls.KEY_NOTIFICATION_TIME)

            local_hh, local_mm = convert_time_hh_mm_to_local(hh, mm, tz)

            tr = TimeTracker(cls.KEY_WEIGHT_TRACKER, local_hh, local_mm)
            await tr.unregister_user(profile.ident)
        except (TypeError, ValueError, AttributeError):
            ...

    async def _send_notification(self, profile: Profile):
        tr = await profile.get_translator()
        io = await DialogIO.load(profile, '')
        # "'Пора бы внести вес, еще не внесли еще сегодня!'"
        io.add(tr.notification_weight).push(ask_current_weight)
        await self.handler.revolve_io(io)

    async def _notify_one_user(self, user_id, now_ts):
        profile = Profile(user_id)
        wp = WeightProfile(profile)

        today_weight = await wp.get_today_weight()
        if today_weight is not None:
            # he has entered weight for today -> skip
            return

        last_ts = await profile.get_prop(self.KEY_LAST_SENT_TS)
        last_ts = 0 if last_ts is None else int(last_ts)

        if now_ts > last_ts + self.NOTIFICATION_COOLDOWN:
            await profile.set_prop(self.KEY_LAST_SENT_TS, now_ts)
            await self._send_notification(profile)

    async def notify_all_by_time(self):
        now = datetime.now(tz=get_localzone())
        now_ts = int(now.timestamp())

        tr = TimeTracker(self.KEY_WEIGHT_TRACKER, now.hour, now.minute)

        user_ids = await tr.list()
        await asyncio.gather(*(self._notify_one_user(user_id, now_ts) for user_id in user_ids))

    @classmethod
    async def fix_bad_notifications(cls):
        db = DB()

        time_prefix = TimeTracker('', 0, 0).key(cls.KEY_WEIGHT_TRACKER)
        time_keys = await db.scan(time_prefix + '*')

        for time_key in time_keys:
            hh, mm = tuple(map(int, time_key.split(':')[2:4]))
            all_users_for_this_time = (await db.redis.smembers(time_key)) or []
            for user_id in all_users_for_this_time:
                profile = Profile(user_id)

                should_delete = False

                tz = await profile.get_time_zone()
                if tz is None:
                    logging.warning(f'time zone is not set for user {profile.ident}!')
                    should_delete = True
                else:
                    try:
                        their_hh, their_mm = hour_and_min_from_str(await profile.get_prop(cls.KEY_NOTIFICATION_TIME))
                    except (TypeError, ValueError, AttributeError):
                        should_delete = True
                    else:
                        local_hh, local_mm = convert_time_hh_mm_to_local(their_hh, their_mm, tz)
                        if local_hh != hh or local_mm != mm:
                            should_delete = True

                if should_delete:
                    logging.info(f'detected bad notification record: {hh}:{mm} for user {profile.ident}')
                    tt = TimeTracker(cls.KEY_WEIGHT_TRACKER, hh, mm)
                    await tt.unregister_user(profile.ident)
