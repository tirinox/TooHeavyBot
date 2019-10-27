from models.timeseries import TimePoint
from models.profile import Profile
from util.date import *


WEIGHT = 'weight'


async def report_weight(profile: Profile, weight, percent):
    their_now = await profile.get_their_now()

    tp = TimePoint(WEIGHT, profile.user_id, their_now)
    tp.value = {
        'weight': weight,
        'percent': percent,
        'ts': int(their_now.timestamp())
    }
    await tp.save()


async def get_yesterday_weight(profile: Profile):
    their_now = await profile.get_their_now()

    their_yesterday = their_now - timedelta(days=1)
    tp = TimePoint(WEIGHT, profile.user_id, their_yesterday)
    await tp.load()
    return tp.value.get('weight', None)
