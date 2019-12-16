import asyncio
import logging

import tasks.notify_weight
import tasks.weight_control
from chat.message_handler import MessageHandler
from util.config import Config


class TaskManager:
    @staticmethod
    def periodic_task_seconds():
        return Config().get_inteval_seconds('periodic.period', min_interval='1s', max_interval='1d')

    def __init__(self, message_handler: MessageHandler):
        self.message_handler = message_handler

    async def _main_periodic_task(self):
        period = self.periodic_task_seconds()
        while True:
            await asyncio.sleep(period)

            logging.info('Periodic tick!')

            await tasks.notify_weight.WeightNotifier(self.message_handler).notify_all_by_time()

    def run_on_loop(self, loop: asyncio.AbstractEventLoop):
        loop.create_task(self._main_periodic_task())
