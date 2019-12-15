from models.profile import Profile
from tasks.notify_weight import WeightNotifier
from util.date import hour_and_min_from_str


async def change_timezone(profile: Profile, tz_name):
    notif_time = await profile.get_prop(WeightNotifier.KEY_NOTIFICATION_TIME)
    if notif_time:
        await WeightNotifier.deactivate_notification(profile)

    await profile.set_time_zone(tz_name)

    if notif_time:
        hh, mm = hour_and_min_from_str(notif_time)
        await WeightNotifier.activate_notification(profile, hh, mm)
