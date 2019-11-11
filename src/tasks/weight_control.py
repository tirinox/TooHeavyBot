from models.timeseries import TimePoint
from models.profile import Profile
from util.date import *
import asyncio
from typing import List
import matplotlib.pyplot as plt
from util import try_parse_float


class WeightPoint(TimePoint):
    def set_values(self, weight, percent, ts):
        self.value = {
            'weight': weight,
            'percent': percent,
            'ts': int(ts)
        }

    def __init__(self, user_id, dt, weight=None, percent=None, ts=None):
        super().__init__(user_id, dt)
        if weight or percent or ts:
            self.set_values(weight, percent, ts)

    @property
    def weight(self):
        return self.get_value_prop('weight')

    @property
    def percent(self):
        return self.get_value_prop('percent')

    @property
    def ts(self):
        return self.get_value_prop('ts')

    async def get_earliest(self) -> 'WeightPoint':
        keys = await self.all_dates_for_user()
        if not keys:
            return None
        early_date_tuple = min(keys)
        wp = WeightPoint(self.user_id, datetime(*early_date_tuple))
        await wp.load()
        return wp


class WeightProfile:
    def __init__(self, p: Profile, weight: float = 0.0):
        self.p = p
        self.weight = weight
        self.aim_percent = 0.0
        self.tps = []

    async def get_weight_start(self):
        return try_parse_float(await self.p.get_prop('weight_start'))

    async def set_weight_start(self, v):
        await self.p.set_prop('weight_start', try_parse_float(v))

    async def get_weight_aim(self):
        return try_parse_float(await self.p.get_prop('weight_aim'))

    async def set_weight_aim(self, v):
        await self.p.set_prop('weight_aim', try_parse_float(v))

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

    async def report_weight(self):
        their_now = await self.p.get_their_now()
        tp = WeightPoint(self.p.ident, their_now,
                         self.weight, self.aim_percent,
                         their_now.timestamp())
        await tp.save()

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
        return await WeightPoint(self.p.ident).get_earliest()

    def __len__(self):
        return len(self.tps)

    @staticmethod
    def _plot_weight_graph(tps: List[WeightPoint], start_weight, aim_weight, is_percent, y_label):
        if len(tps) < 2:
            return None

        plt.figure()

        xs, ys = [], []
        for tp in tps:
            w = tp.percent if is_percent else tp.weight
            if w:
                xs.append(tp.date)
                ys.append(w)

        plt.xticks(rotation=30)
        plt.plot(xs, ys, marker='*')

        plt.ylabel(y_label)

        if start_weight:
            plt.axhline(y=start_weight, color='r', linestyle='--')

        if aim_weight:
            plt.axhline(y=aim_weight, color='g', linestyle='--')

        from io import BytesIO
        png_buffer = BytesIO()
        plt.savefig(png_buffer, format='png')
        png_buffer.seek(0)
        return png_buffer

    async def plot_weight_graph(self, n_days=30):
        start_weight = await self.get_weight_start()
        aim_weight = await self.get_weight_aim()

        tr = await self.p.get_translator()
        y_label = tr.ap_weight_label

        tps = await self.get_weight_points_for_profile(n_days)
        return await asyncio.get_event_loop().run_in_executor(
            None, self._plot_weight_graph, tps, start_weight, aim_weight, False, y_label)

    async def plot_percent_graph(self, n_days=30):
        tr = await self.p.get_translator()
        y_label = tr.ap_percent_label

        tps = await self.get_weight_points_for_profile(n_days)
        return await asyncio.get_event_loop().run_in_executor(
            None, self._plot_weight_graph, tps, 0, 100, True, y_label)
