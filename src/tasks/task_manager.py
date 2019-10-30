import asyncio
from util.config import Config
import logging
import tasks.notify_weight
import tasks.weight_control


def periodic_task_seconds():
    return Config().get_inteval_seconds('periodic.period', min_interval='1s', max_interval='1d')


async def main_periodic_task(bot):
    period = periodic_task_seconds()
    while True:
        await asyncio.sleep(period)

        logging.info('Periodic tick!')

        await tasks.notify_weight.notify_all_by_time(bot)


def run_on_loop(loop: asyncio.AbstractEventLoop, bot):
    loop.create_task(main_periodic_task(bot))
