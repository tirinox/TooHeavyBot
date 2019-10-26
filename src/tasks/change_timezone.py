from models.profile import Profile
from tasks.notify_weight import activate_notification, deactivate_notification, KEY_NOTIFICATION_TIME
from util.date import hour_and_min_from_str


async def change_timezone(profile: Profile, tz_name):
    notif_time = await profile.get_prop(KEY_NOTIFICATION_TIME)
    if notif_time:
        await deactivate_notification(profile)

    await profile.set_time_zone(tz_name)

    if notif_time:
        hh, mm = hour_and_min_from_str(notif_time)
        await activate_notification(profile, hh, mm)
