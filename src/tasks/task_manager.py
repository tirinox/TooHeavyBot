import asyncio
from util.config import Config
import logging


def periodic_task_seconds():
    return Config().get_inteval_seconds('periodic.period', min_interval='1s', max_interval='1d')


async def main_periodic_task():
    period = periodic_task_seconds()
    while True:
        logging.info('Periodic tick!')
        await asyncio.sleep(period)


def run_on_loop(loop: asyncio.AbstractEventLoop):
    loop.create_task(main_periodic_task())
