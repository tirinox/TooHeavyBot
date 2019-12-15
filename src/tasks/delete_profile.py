from tasks.notify_weight import WeightNotifier
from models.profile import Profile


async def delete_profile(user_id):
    profile = Profile(user_id)

    await WeightNotifier.deactivate_notification(profile)
    await profile.delete_all()
