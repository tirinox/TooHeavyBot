from aiogram.types import Message
from models.profile import Profile
import logging
from msg_io import *


def is_personal_chat(m: Message):
    return m.from_user.id == m.chat.id


class MessageHandler:
    MAX_JUMPS = 50

    def __init__(self, handlers: dict, initial_handler):
        assert handlers
        self.handlers = handlers

        assert initial_handler
        self.initial_handler = initial_handler

    async def handle_start(self, code):
        return None

    async def check_if_start(self, message: Message):
        text = str(message.text)
        if text.startswith(START_COMMAND):
            code = text[len(START_COMMAND):].strip()
            state_name = await self.handle_start(code)
            return state_name

    def find_handler(self, state: dict):
        handler_name = state.get(CURRENT_FUNCTION_KEY, None)

        if not handler_name or handler_name not in self.handlers:
            state[CURRENT_FUNCTION_KEY] = fname(self.initial_handler)
            return self.initial_handler
        return self.handlers[handler_name]

    async def handle(self, message: Message):
        profile = Profile(message.from_user.id)
        dialog_state = await profile.dialog_state()

        handler = self.find_handler(dialog_state)

        io_obj = DialogIO(message, profile, message.text, dialog_state)
        all_reply_texts = []

        jump_no = 0
        while jump_no < self.MAX_JUMPS:
            await handler(io_obj)

            dialog_state = io_obj.state

            if io_obj.out_text:
                all_reply_texts.append(io_obj.out_text)

            handler = self.find_handler(dialog_state)

            if io_obj.asked:
                break

            jump_no += 1
        else:
            logging.error(f'handle recursion detected!')

        await profile.set_dialog_state(dialog_state)

        if all_reply_texts:
            if io_obj.join_messages:
                text_sum = NEW_LINE.join(all_reply_texts)
                await message.reply(text_sum, reply=False, reply_markup=io_obj.out_keyboard)
            else:
                for reply_text in all_reply_texts:
                    await message.reply(reply_text, reply=False, reply_markup=io_obj.out_keyboard)
