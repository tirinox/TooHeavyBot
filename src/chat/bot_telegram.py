from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ContentTypes
from util.config import Config


class TelegramBot:
    @staticmethod
    def is_personal_chat(m: types.Message):
        return m.from_user.id == m.chat.id

    def __init__(self, handler_func):
        token = Config().get('telegram.token')
        self.bot = Bot(token, parse_mode=types.ParseMode.HTML)
        self.dispatcher = Dispatcher(self.bot)

        @self.dispatcher.message_handler(content_types=ContentTypes.ANY)
        async def echo(message: types.Message):
            # only personal chats
            if not TelegramBot.is_personal_chat(message):
                return

            await handler_func(message)

    def serve(self):
        executor.start_polling(self.dispatcher, skip_updates=True)

    async def send_text(self, user_id, message):
        return await self.bot.send_message(user_id, message)
