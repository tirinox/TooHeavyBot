from models.profile import Profile
from models.time_tracker import TimeTracker
from util.date import hour_and_min_from_str, convert_time_hh_mm_to_local
import logging
import pytz
from tzlocal import get_localzone
from datetime import datetime
from chat.bot_telegram import TelegramBot


KEY_NOTIFICATION_TIME = 'notification_time'
KEY_WEIGHT_TRACKER = 'weight_tracker'

NOTIFICATION_TEXT = 'Пора бы внести вес, еще не внесни еще сегодня!'


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


async def notify_all_by_time(bot: TelegramBot):
    now = datetime.now(tz=get_localzone())
    tr = TimeTracker(KEY_WEIGHT_TRACKER, now.hour, now.minute)
    for user_id in await tr.list():
        await bot.send_text(user_id, NOTIFICATION_TEXT)
