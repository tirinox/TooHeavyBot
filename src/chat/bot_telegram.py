from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ContentTypes

from chat.message_handler import MessageHandler
from chat.msg_io import AbstractMessageSender
from util.config import Config

import asyncio

import logging


class TelegramBot(AbstractMessageSender):
    @staticmethod
    def is_personal_chat(m: types.Message):
        return m.from_user.id == m.chat.id

    def __init__(self, handler: MessageHandler):
        super().__init__()
        self.handler = handler

        token = Config().get('telegram.token')
        self.bot = Bot(token, parse_mode=types.ParseMode.HTML)
        self.dispatcher = Dispatcher(self.bot)

        self.username = None

        @self.dispatcher.message_handler(content_types=ContentTypes.ANY)
        async def echo(message: types.Message):
            # only personal chats
            if not TelegramBot.is_personal_chat(message):
                return

            await self.handler.handle(message)

    async def _me_getter(self):
        me = await self.bot.me
        self.username = me['username']
        logging.info(f'My bot user name is "{self.username}".')

    def serve(self):
        asyncio.get_event_loop().run_until_complete(self._me_getter())
        executor.start_polling(self.dispatcher, skip_updates=True)

    async def send_photo(self, to_uid, photo, caption=None, disable_notification=False):
        return await self.bot.send_photo(to_uid, photo, caption,
                                         disable_notification=disable_notification)

    async def send_text(self, to_uid, text, reply_markup=None, disable_notification=False):
        return await self.bot.send_message(to_uid, text,
                                           disable_notification=disable_notification,
                                           reply_markup=reply_markup)
