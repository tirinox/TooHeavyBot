# this is a playground for various tests...
from util.config import Config
from tasks.notify_weight import *
from tasks.weight_control import WeightPoint


async def testus():
    tp = WeightPoint(102)
    keys = await tp.all_dates_for_user()
    print(keys)


if __name__ == '__main__':
    config = Config()
    logging.basicConfig(level=logging.INFO if config.is_debug else logging.ERROR)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(DB().connect())
    loop.run_until_complete(testus())
