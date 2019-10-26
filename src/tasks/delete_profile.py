from tasks.notify_weight import deactivate_notification
from models.profile import Profile


async def delete_profile(user_id):
    profile = Profile(user_id)

    await deactivate_notification(profile)
    await profile.delete()
