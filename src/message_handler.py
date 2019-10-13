from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from models.profile import Profile
from aioredis import Redis
from msg_io import Input, Output, NEW_LINE


class MessageHandler:
    def __init__(self, m: Message, r: Redis, handlers: dict):
        self.message = m
        self.redis = r
        self.handlers = handlers

    async def handle_start(self, code):
        return None
        # if code:
        #     # надо прервать любой диалог и обрбаотать диалог с кодом
        #     await self.message.reply(f"Hi!\nYour code is {code}")
        # else:
        #     # сделать стэйт main menu
        #     await self.message.reply(f'Hi! this is start without params!')

    def get_handler(self, state):
        if state is None or state not in self.handlers:
            state = 'main'
        return self.handlers[state]

    async def handle(self):
        profile = Profile(self.redis, self.message.from_user.id)
        state = await profile.dialog_state()

        text = str(self.message.text)
        start_prefix = '/start'
        if text.startswith(start_prefix):
            code = text[len(start_prefix):].strip()
            state = await self.handle_start(code)

        outputs = []

        handler = self.get_handler(state)

        while True:
            output = await handler(Input(self.message, profile, text))
            if isinstance(output, tuple):
                output = Output(*output)

            if output.reply_text is not None:
                outputs.append(output)

            if callable(output.new_state):
                state = output.new_state.__name__

            handler = self.get_handler(state)

            if hasattr(handler, 'uses_answer'):
                break

        await profile.set_dialog_state(state)

        if outputs:
            messages = (output.reply_text for output in outputs if output.reply_text is not None)

            last_output = outputs[-1]  # type: Output
            if last_output.join_messages:
                message = NEW_LINE.join(messages)
                if message:
                    await self.message.reply(message, reply=False, reply_markup=last_output.keyboard)
            else:
                for message in messages:
                    await self.message.reply(message, reply=False, reply_markup=last_output.keyboard)
