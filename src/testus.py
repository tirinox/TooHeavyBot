# this is a playground for various tests...
import asyncio
import logging

from util.config import Config
from util.database import DB
from util.date import *

from datetime import datetime, timedelta
import random

from tasks.weight_control import WeightProfile, WeightPoint
from models.profile import Profile

import matplotlib.pyplot as plt
import numpy as np


async def test_body():
    p = Profile(102)
    wp = WeightProfile(p)
    target_weight = 88

    points = await wp.get_weight_points_for_profile()

    if not points:
        n_days = 25
        current_date = datetime.now() - timedelta(minutes=30)
        current_weight = 96.7

        d_w = []
        for _ in range(n_days):
            d_w.append([current_date, current_weight])
            current_weight -= random.uniform(-1.5, 0.6)
            current_date -= timedelta(days=1)

        for d, w in d_w:
            print(f'{d} ==> {w:.1f}')
            await WeightProfile._report_weight(p.ident, d, w, 50)

        points = await wp.get_weight_points_for_profile()

    a, b = wp.estimate_weight_curve(points)
    if a is not None:
        def solve_lin(target_y, a, b):
            return (target_y - b) / a

        target_ts = solve_lin(target_weight, a, b)
        print(datetime.fromtimestamp(target_ts))

        time_stamps = np.array([tp.ts for tp in points], dtype=np.uint32)
        weights = np.array([tp.weight for tp in points], dtype=np.float)

        plt.axvline(datetime.fromtimestamp(target_ts))

        dates = [datetime.fromtimestamp(tp.ts) for tp in points]
        plt.plot(dates, weights, 'g^')

        ts_fit = np.linspace(np.min(time_stamps) - 3 * DAY, target_ts + 3 * DAY, 100)
        weights_fit = a * ts_fit + b

        date_fit = [datetime.fromtimestamp(ts) for ts in ts_fit]
        plt.plot(date_fit, weights_fit, 'r')

        plt.show()
    else:
        print('unkown!')




config = Config()
logging.basicConfig(level=logging.INFO if config.is_debug else logging.ERROR)

loop = asyncio.get_event_loop()
loop.run_until_complete(DB().connect())

loop.run_until_complete(test_body())
