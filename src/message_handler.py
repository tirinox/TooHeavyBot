from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from models.profile import Profile
from aioredis import Redis
from msg_io import Input, Output


class MessageHandler:
    def __init__(self, m: Message, r: Redis, handlers: dict):
        self.message = m
        self.redis = r
        self.handlers = handlers

    async def handle_start(self, code):
        if code:
            # надо прервать любой диалог и обрбаотать диалог с кодом
            await self.message.reply(f"Hi!\nYour code is {code}")
        else:
            # сделать стэйт main menu
            await self.message.reply(f'Hi! this is start without params!')

    def get_handler(self, state):
        if state is None or state not in self.handlers:
            state = 'main'
        return self.handlers[state]

    async def handle(self):
        text = str(self.message.text)
        start_prefix = '/start'
        if text.startswith(start_prefix):
            code = text[len(start_prefix):].strip()
            await self.handle_start(code)
            return

        profile = Profile(self.redis, self.message.from_user.id)
        state = await profile.dialog_state()

        handler = self.get_handler(state)

        output = await handler(Input(self.message, profile, text))
        if isinstance(output, tuple):
            output = Output(*output)

        if callable(output.new_state):
            state = output.new_state.__name__

        await profile.set_dialog_state(state)
        if output.reply_text is not None:
            await self.message.reply(output.reply_text, reply=False, reply_markup=output.keyboard)
