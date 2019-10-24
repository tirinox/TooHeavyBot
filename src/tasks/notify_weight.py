from models.profile import Profile
from models.timeseries import TimePoint
from models.time_tracker import TimeTracker
from util.date import hour_and_min_from_str, possible_timezones
import logging
import pytz
from tzlocal import get_localzone
from datetime import datetime
from chat.bot_telegram import TelegramBot


KEY_NOTIFICATION_TIME = 'notification_time'
KEY_WEIGHT_TRACKER = 'weight_tracker'

NOTIFICATION_TEXT = 'Пора бы внести вес, еще не внесни еще сегодня!'


async def activate_notification(user_id, hh, mm):
    user = Profile(user_id)
    minutes_shift = await user.get_time_shift()
    if minutes_shift is None:
        logging.error(f'time shift is not set for user {user_id}!')
        return

    tz_list = possible_timezones(minutes_shift)
    if not tz_list:
        logging.error(f'impossible time shift for user {user_id}!')
        return

    their_tz = pytz.timezone(tz_list[0])

    their_dt = datetime(2019, 8, 26, hour=hh, minute=mm, tzinfo=their_tz)
    out_dt = their_dt.astimezone(get_localzone())
    local_hh = out_dt.hour
    local_mm = out_dt.minute

    await user.set_prop(KEY_NOTIFICATION_TIME, f'{local_hh}:{local_mm}')
    tr = TimeTracker(KEY_WEIGHT_TRACKER, local_hh, local_mm)
    await tr.register_user(user_id)


async def deactivate_notification(user_id):
    user = Profile(user_id)

    current_time_str = await user.get_prop(KEY_NOTIFICATION_TIME)

    try:
        hh, mm = hour_and_min_from_str(current_time_str)

        tr = TimeTracker(KEY_WEIGHT_TRACKER, hh, mm)
        await tr.unregister_user(user_id)
    except (TypeError, ValueError):
        ...


async def notify_all_by_time(bot: TelegramBot):
    now = datetime.now(tz=get_localzone())
    tr = TimeTracker(KEY_WEIGHT_TRACKER, now.hour, now.minute)
    for user_id in await tr.list():
        await bot.send_text(user_id, NOTIFICATION_TEXT)
