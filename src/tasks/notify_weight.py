from models.profile import Profile
from models.time_tracker import TimeTracker
from util.date import *
from util.database import DB
import logging
from tzlocal import get_localzone
from datetime import datetime
from chat.bot_telegram import TelegramBot
from tasks.weight_control import WeightProfile
import asyncio


KEY_NOTIFICATION_TIME = 'notification_time'
KEY_WEIGHT_TRACKER = 'weight_tracker'
KEY_LAST_SENT_TS = 'last_sent_ts'

NOTIFICATION_COOLDOWN = parse_timespan_to_seconds('1m')


async def activate_notification(profile: Profile, hh, mm):
    await deactivate_notification(profile)

    await profile.set_prop(KEY_NOTIFICATION_TIME, f'{hh}:{mm}')

    tz = await profile.get_time_zone()
    if tz is None:
        logging.error(f'time zone is not set for user {profile.ident}!')
        return

    local_hh, local_mm = convert_time_hh_mm_to_local(hh, mm, tz)

    tr = TimeTracker(KEY_WEIGHT_TRACKER, local_hh, local_mm)
    await tr.register_user(profile.ident)

    return delta_to_next_hh_mm(local_hh, local_mm)


async def deactivate_notification(profile: Profile):
    tz = await profile.get_time_zone()
    if tz is None:
        logging.error(f'time zone is not set for user {profile.ident}!')
        return

    current_time_str = await profile.get_prop(KEY_NOTIFICATION_TIME)

    try:
        hh, mm = hour_and_min_from_str(current_time_str)

        await profile.del_prop(KEY_NOTIFICATION_TIME)

        local_hh, local_mm = convert_time_hh_mm_to_local(hh, mm, tz)

        tr = TimeTracker(KEY_WEIGHT_TRACKER, local_hh, local_mm)
        await tr.unregister_user(profile.ident)
    except (TypeError, ValueError, AttributeError):
        ...


async def notify_one_user(bot: TelegramBot, user_id, now_ts):
    profile = Profile(user_id)
    wp = WeightProfile(profile)

    today_weight = await wp.get_today_weight()
    if today_weight is not None:
        # he has entered weight for today -> skip
        return

    last_ts = await profile.get_prop(KEY_LAST_SENT_TS)
    last_ts = 0 if last_ts is None else int(last_ts)

    if now_ts > last_ts + NOTIFICATION_COOLDOWN:
        tr = await profile.get_translator()

        await profile.set_prop(KEY_LAST_SENT_TS, now_ts)
        await bot.send_text(user_id, tr.notification_weight)

        # todo: push state with keyboard


async def notify_all_by_time(bot: TelegramBot):
    now = datetime.now(tz=get_localzone())
    now_ts = int(now.timestamp())

    tr = TimeTracker(KEY_WEIGHT_TRACKER, now.hour, now.minute)

    user_ids = await tr.list()
    await asyncio.gather(*(notify_one_user(bot, user_id, now_ts) for user_id in user_ids))


async def fix_bad_notifications():
    db = DB()

    time_prefix = TimeTracker('', 0, 0).key(KEY_WEIGHT_TRACKER)
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
                    their_hh, their_mm = hour_and_min_from_str(await profile.get_prop(KEY_NOTIFICATION_TIME))
                except (TypeError, ValueError, AttributeError):
                    should_delete = True
                else:
                    local_hh, local_mm = convert_time_hh_mm_to_local(their_hh, their_mm, tz)
                    if local_hh != hh or local_mm != mm:
                        should_delete = True

            if should_delete:
                logging.info(f'detected bad notification record: {hh}:{mm} for user {profile.ident}')
                tt = TimeTracker(KEY_WEIGHT_TRACKER, hh, mm)
                await tt.unregister_user(profile.ident)
