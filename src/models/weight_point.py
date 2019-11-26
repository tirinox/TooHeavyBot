from models.timeseries import TimePoint
from datetime import datetime


class WeightPoint(TimePoint):
    def set_values(self, weight, percent, ts):
        self.value = {
            'weight': weight,
            'percent': percent,
            'ts': int(ts)
        }

    def __init__(self, user_id, dt: datetime, weight=None, percent=None):
        super().__init__(user_id, dt)
        ts = dt.timestamp() if dt is not None else None
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

