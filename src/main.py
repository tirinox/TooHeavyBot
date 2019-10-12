from aiogram import Bot, Dispatcher, executor, types
from util.config import Config
import logging
import rom


config = Config()

debug = config.is_debug
level = logging.INFO if debug else logging.ERROR
logging.basicConfig(level=level)

db_config = config.subtree('db.redis')

print(db_config)

rom.util.set_connection_settings(
    host=db_config.get('host'),
    port=db_config.get('port'),
    db=db_config.get('db_no')
)

token = Config().get('telegram.token')
bot = Bot(token)
dp = Dispatcher(bot)


START_PREFIX = '/start '


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    text = str(message.text)
    if text.startswith(START_PREFIX):
        code = text[len(START_PREFIX):]
        await message.reply(f"Hi!\nYour code is {code}")
    else:
        await message.reply(f'Hi! this is start without params!')


@dp.message_handler()
async def echo(message: types.Message):
    await message.reply(message.text, reply=False)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
