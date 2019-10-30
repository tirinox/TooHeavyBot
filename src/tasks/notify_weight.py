from models.profile import Profile
from models.time_tracker import TimeTracker
from util.date import hour_and_min_from_str, convert_time_hh_mm_to_local, parse_timespan_to_seconds, delta_to_next_hh_mm
import logging
from tzlocal import get_localzone
from datetime import datetime
from chat.bot_telegram import TelegramBot
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
        logging.error(f'time zone is not set for user {profile.user_id}!')
        return

    local_hh, local_mm = convert_time_hh_mm_to_local(hh, mm, tz)

    tr = TimeTracker(KEY_WEIGHT_TRACKER, local_hh, local_mm)
    await tr.register_user(profile.user_id)

    return delta_to_next_hh_mm(local_hh, local_mm)


async def deactivate_notification(profile: Profile):
    tz = await profile.get_time_zone()
    if tz is None:
        logging.error(f'time zone is not set for user {profile.user_id}!')
        return

    current_time_str = await profile.get_prop(KEY_NOTIFICATION_TIME)

    try:
        hh, mm = hour_and_min_from_str(current_time_str)

        await profile.del_prop(KEY_NOTIFICATION_TIME)

        local_hh, local_mm = convert_time_hh_mm_to_local(hh, mm, tz)

        tr = TimeTracker(KEY_WEIGHT_TRACKER, local_hh, local_mm)
        await tr.unregister_user(profile.user_id)
    except (TypeError, ValueError, AttributeError):
        ...


async def notify_one_user(bot: TelegramBot, user_id, now_ts):
    profile = Profile(user_id)
    last_ts = await profile.get_prop(KEY_LAST_SENT_TS)
    last_ts = 0 if last_ts is None else int(last_ts)

    if now_ts > last_ts + NOTIFICATION_COOLDOWN:
        tr = await profile.get_translator()

        await profile.set_prop(KEY_LAST_SENT_TS, now_ts)
        await bot.send_text(user_id, tr.notification_weight)


async def notify_all_by_time(bot: TelegramBot):
    now = datetime.now(tz=get_localzone())
    now_ts = int(now.timestamp())

    tr = TimeTracker(KEY_WEIGHT_TRACKER, now.hour, now.minute)

    user_ids = await tr.list()
    await asyncio.gather(*(notify_one_user(bot, user_id, now_ts) for user_id in user_ids))
