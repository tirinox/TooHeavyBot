from models.profile import Profile
from models.timeseries import TimePoint


KEY_NOTIFICATION_TIME = 'notification_time'


async def activate_notification(user_id):
    user = Profile(user_id)
    notification_time = await user.get_prop(KEY_NOTIFICATION_TIME)
    if notification_time is None:
        await user.set_prop(KEY_NOTIFICATION_TIME, '')