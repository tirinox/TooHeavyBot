from aiogram import Bot, Dispatcher, executor, types
from util.config import Config
from util.database import get_db
import logging
from dialogs import get_handlers
from message_handler import MessageHandler
import asyncio


if __name__ == '__main__':
    config = Config()
    logging.basicConfig(level=logging.INFO if config.is_debug else logging.ERROR)

    token = config.get('telegram.token')
    bot = Bot(token, parse_mode=types.ParseMode.HTML)
    dp = Dispatcher(bot)

    async def database():
        global redis
        redis = await get_db()
    asyncio.get_event_loop().run_until_complete(database())

    handlers = get_handlers()

    @dp.message_handler()
    async def echo(message: types.Message):
        await MessageHandler(message, redis, handlers).handle()

    executor.start_polling(dp, skip_updates=True)
