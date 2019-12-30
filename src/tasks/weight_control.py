from models.weight_point import WeightPoint
from models.profile import Profile
from util.date import *
import asyncio
from typing import List
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from util import try_parse_float
import numpy as np


class WeightProfile:
    WEIGHT_START_KEY = 'weight_start'
    WEIGHT_AIM_KEY = 'weight_aim'

    def __init__(self, p: Profile, weight: float = 0.0):
        self.p = p
        self.weight = weight
        self.aim_percent = 0.0
        self.tps = []

    async def get_weight_start(self):
        return try_parse_float(await self.p.get_prop(self.WEIGHT_START_KEY))

    async def set_weight_start(self, v):
        await self.p.set_prop(self.WEIGHT_START_KEY, try_parse_float(v))

    async def get_weight_aim(self):
        return try_parse_float(await self.p.get_prop(self.WEIGHT_AIM_KEY))

    async def set_weight_aim(self, v):
        await self.p.set_prop(self.WEIGHT_AIM_KEY, try_parse_float(v))

    @staticmethod
    def aim_percent_formula(current, aim, start):
        p = (1.0 - (current - aim) / (start - aim)) * 100.0
        return round(p, 2)

    async def calculate_aim_percent(self):
        weight_start = await self.get_weight_start()
        weight_aim = await self.get_weight_aim()
        if weight_start and weight_aim:
            return self.aim_percent_formula(self.weight, weight_aim, weight_start)

    async def report_aim_percent(self):
        self.aim_percent = await self.calculate_aim_percent()
        if self.aim_percent is not None:
            await self.report_weight()
            return True
        return False

    async def get_yesterday_weight(self):
        return await self.get_other_day_weight(-1)

    async def get_today_weight(self):
        return await self.get_other_day_weight(0)

    async def get_other_day_weight(self, shift_days):
        their_now = await self.p.get_their_now()
        their_day = their_now + timedelta(days=shift_days)
        tp = WeightPoint(self.p.ident, their_day)
        await tp.load()
        return tp.weight

    @staticmethod
    async def _report_weight(ident, date, weight, percent):
        return await WeightPoint(ident, date, weight, percent).save()

    async def report_weight(self):
        their_now = await self.p.get_their_now()
        await self._report_weight(self.p.ident, their_now, self.weight, self.aim_percent)

    async def get_weight_points_for_profile(self, n_days=30) -> List[WeightPoint]:
        today = await self.p.get_their_now()

        tasks = []
        for _ in range(n_days):
            tp = WeightPoint(self.p.ident, today)
            tasks.append(tp.load())
            today -= timedelta(days=1)

        self.tps = await asyncio.gather(*tasks)

        return [tp for tp in self.tps if tp.value]

    async def get_initial_weight_point(self):
        return await WeightPoint(self.p.ident, datetime.now()).get_earliest()

    def __len__(self):
        return len(self.tps)

    @staticmethod
    def _plot_weight_graph(tps: List[WeightPoint], start_weight, aim_weight, is_percent, y_label):
        if len(tps) < 2:
            return None

        fig = plt.figure(figsize=(10, 6))
        ax = fig.add_subplot(111)

        xs, ys = [], []
        for tp in tps:
            w = tp.percent if is_percent else tp.weight
            if w:
                xs.append(tp.date)
                ys.append(w)

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))

        ax.plot(xs, ys, marker='*')

        for tick in ax.get_xticklabels():
            tick.set_rotation(30)

        ax.set_ylabel(y_label)

        if start_weight:
            ax.axhline(y=start_weight, color='r', linestyle='--')

        if aim_weight:
            ax.axhline(y=aim_weight, color='g', linestyle='--')

        from io import BytesIO
        png_buffer = BytesIO()
        plt.savefig(png_buffer, format='png')
        png_buffer.seek(0)
        return png_buffer

    async def plot_weight_graph(self, tps: List[WeightPoint]):
        start_weight = await self.get_weight_start()
        aim_weight = await self.get_weight_aim()

        tr = await self.p.get_translator()
        y_label = tr.ap_weight_label

        return await asyncio.get_event_loop().run_in_executor(
            None, self._plot_weight_graph, tps, start_weight, aim_weight, False, y_label)

    async def plot_percent_graph(self, tps: List[WeightPoint]):
        tr = await self.p.get_translator()
        y_label = tr.ap_percent_label

        return await asyncio.get_event_loop().run_in_executor(
            None, self._plot_weight_graph, tps, 0, 100, True, y_label)

    @classmethod
    def estimate_weight_curve(cls, tps: List[WeightPoint]):
        if len(tps) < 5:
            return None, None

        time_stamps = np.array([tp.ts for tp in tps], dtype=np.uint32)
        weights = np.array([tp.weight for tp in tps], dtype=np.float)

        a, b = np.polyfit(time_stamps, weights, 1).tolist()

        if abs(a) < 1e-8:
            return None, None

        return a, b

    async def timestamp_of_target_weight(self, tps: List[WeightPoint]):
        aim_weight = await self.get_weight_aim()

        a, b = self.estimate_weight_curve(tps)
        if a is None:
            return None

        ts = (aim_weight - b) / a
        return ts
