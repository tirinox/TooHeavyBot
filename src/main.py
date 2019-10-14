from aiogram import Bot, Dispatcher, executor, types
from util.config import Config
from util.database import get_db
import logging
from dialogs import *
from message_handler import MessageHandler
import asyncio


if __name__ == '__main__':
    config = Config()
    logging.basicConfig(level=logging.INFO if config.is_debug else logging.ERROR)

    token = config.get('telegram.token')
    bot = Bot(token, parse_mode=types.ParseMode.HTML)
    dispatcher = Dispatcher(bot)

    async def database():
        global redis
        redis = await get_db()
    asyncio.get_event_loop().run_until_complete(database())

    message_handler = MessageHandler(redis, initial_handler=ENTRY_POINT)

    @dispatcher.message_handler()
    async def echo(message: types.Message):
        await message_handler.handle(message)

    executor.start_polling(dispatcher, skip_updates=True)
