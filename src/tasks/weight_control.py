from models.timeseries import TimePoint
from models.profile import Profile
from util.date import *
import asyncio
from typing import List
import matplotlib.pyplot as plt
import matplotlib


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


async def get_weight_points_for_profile(p: Profile, n_days=30):
    today = await p.get_their_now()

    tasks = []
    for _ in range(n_days):
        tp = TimePoint(WEIGHT, p.user_id, today)
        tasks.append(tp.load())
        today -= timedelta(days=1)

    tps = await asyncio.gather(*tasks)

    return [tp for tp in tps if tp.value]


def _plot_weight_graph(tps: List[TimePoint]):
    if len(tps) < 2:
        return None

    plt.figure()

    xs, ys = [], []
    for tp in tps:
        w = tp.value.get('weight', None)
        if w:
            xs.append(tp.date)
            ys.append(w)

    plt.xticks(rotation=30)
    plt.plot(xs, ys, marker='*')

    from io import BytesIO
    png_buffer = BytesIO()
    plt.savefig(png_buffer, format='png')
    png_buffer.seek(0)
    return png_buffer


async def plot_weight_graph(tps: List[TimePoint]):
    return await asyncio.get_event_loop().run_in_executor(None, _plot_weight_graph, tps)