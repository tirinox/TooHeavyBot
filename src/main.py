import asyncio
from aiogram import Bot, Dispatcher, executor, types
import aioredis
from util.config import Config
import logging
from models.profile import Profile


config = Config()

debug = config.is_debug
level = logging.INFO if debug else logging.ERROR
logging.basicConfig(level=level)



async def get_db(url):
    return await aioredis.create_redis_pool(url, encoding='utf-8')



async def main():
    db_config = config.subtree('db.redis')
    redis_url = db_config.get('url', default='localhost')
    redis = await get_db(redis_url)

    p = Profile(user_name='max')
    p.ident = 10
    await p.save(redis)

    p2 = await Profile.load(redis, 10)
    print(p2)


if __name__ == '__main__':
    asyncio.run(main())
#
# token = Config().get('telegram.token')
# bot = Bot(token)
# dp = Dispatcher(bot)
#
#
# START_PREFIX = '/start '
#
#
# def get_profile_of_message(message: types.Message):
#     user_id = int(message.from_user.id)
#     print(Profile.query.filter(user_id=user_id).all())
#
#
#
# @dp.message_handler(commands=['start'])
# async def send_welcome(message: types.Message):
#     print(message)
#     text = str(message.text)
#     if text.startswith(START_PREFIX):
#         code = text[len(START_PREFIX):]
#         await message.reply(f"Hi!\nYour code is {code}")
#     else:
#         await message.reply(f'Hi! this is start without params!')
#
#
# @dp.message_handler()
# async def echo(message: types.Message):
#     await message.reply(message.text, reply=False)
#
#
# if __name__ == '__main__':
#     executor.start_polling(dp, skip_updates=True)
