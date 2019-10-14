from aiogram.types import Message
from models.profile import Profile
from aioredis import Redis
from msg_io import Input, Output, NEW_LINE, START_COMMAND, does_require_answer, fname


def is_personal_chat(m: Message):
    return m.from_user.id == m.chat.id


class MessageHandler:
    def __init__(self, r: Redis, initial_handler):
        self.redis = r
        assert initial_handler
        self.initial_handler = initial_handler
        self.handlers = {fname(initial_handler): initial_handler}

    async def handle_start(self, code):
        return None

    def get_handler(self, state):
        if state is None or state not in self.handlers:
            return self.initial_handler
        return self.handlers[state]

    async def handle(self, message: Message):
        # only personal chats
        if not is_personal_chat(message):
            return

        profile = Profile(self.redis, message.from_user.id)
        state_name = await profile.dialog_state()

        text = str(message.text)
        if text.startswith(START_COMMAND):
            code = text[len(START_COMMAND):].strip()
            state_name = await self.handle_start(code)

        outputs = []

        print(state_name)

        handler = self.get_handler(state_name)

        while True:
            output = await handler(Input(message, profile, text))
            if isinstance(output, tuple):
                output = Output(*output)

            if output.reply_text is not None:
                outputs.append(output)

            new_state = output.new_state
            assert callable(new_state)

            state_name = fname(new_state)
            if state_name not in self.handlers:
                print(self.handlers)
                self.handlers[state_name] = new_state

            handler = self.get_handler(state_name)

            if does_require_answer(handler):
                break

        await profile.set_dialog_state(state_name)

        if outputs:
            reply_messages = (output.reply_text for output in outputs if output.reply_text is not None)

            last_output = outputs[-1]  # type: Output
            if last_output.join_messages:
                all_reply_text = NEW_LINE.join(reply_messages)
                if all_reply_text:
                    await message.reply(all_reply_text, reply=False, reply_markup=last_output.keyboard)
            else:
                for reply_text in reply_messages:
                    await message.reply(reply_text, reply=False, reply_markup=last_output.keyboard)
