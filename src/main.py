from aiogram import Bot, Dispatcher, executor, types
from util.config import Config
import logging
from dialogs import MessageHandler


if __name__ == '__main__':
    config = Config()
    logging.basicConfig(level=logging.INFO if config.is_debug else logging.ERROR)

    token = config.get('telegram.token')
    bot = Bot(token, parse_mode=types.ParseMode.HTML)
    dp = Dispatcher(bot)

    @dp.message_handler()
    async def echo(message: types.Message):
        await MessageHandler(message).handle()

    executor.start_polling(dp, skip_updates=True)
