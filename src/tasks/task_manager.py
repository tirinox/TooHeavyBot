import asyncio
import logging

import tasks.notify_weight
import tasks.weight_control
from chat.bot_telegram import TelegramBot
from util.config import Config


class TaskManager:
    @staticmethod
    def periodic_task_seconds():
        return Config().get_inteval_seconds('periodic.period', min_interval='1s', max_interval='1d')

    def __init__(self, bot: TelegramBot):
        self.bot = bot

    async def _main_periodic_task(self):
        period = self.periodic_task_seconds()
        while True:
            await asyncio.sleep(period)

            logging.info('Periodic tick!')

            await tasks.notify_weight.WeightNotifier(self.bot.handler).notify_all_by_time()

    def run_on_loop(self, loop: asyncio.AbstractEventLoop):
        loop.create_task(self._main_periodic_task())
