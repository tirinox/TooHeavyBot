from chat.msg_io import *


class MessageHandler:
    MAX_JUMPS = 50

    def __init__(self, handlers: dict, initial_handler):
        assert handlers
        self.handlers = handlers

        assert initial_handler
        self.initial_handler = initial_handler

    async def handle_start(self, io: DialogIO, code: str):
        ...

    async def check_if_command(self, io: DialogIO):
        text = str(io.text)
        if text.startswith(START_COMMAND):
            code = text[len(START_COMMAND):].strip()
            await self.handle_start(io, code)
        elif text.startswith(RESET_COMMAND):
            io.state = {}
            await io.message.reply('RESET DONE!')

    def find_handler(self, state: dict):
        handler_name = state.get(CURRENT_FUNCTION_KEY, None)

        if not handler_name or handler_name not in self.handlers:
            state[CURRENT_FUNCTION_KEY] = fname(self.initial_handler)
            return self.initial_handler
        return self.handlers[handler_name]

    async def handle(self, message: Message):

        profile = Profile(message.from_user.id)
        dialog_state = await profile.dialog_state()

        io_obj = DialogIO(message, profile, message.text, dialog_state)
        io_obj.location = message.location
        io_obj.language = await profile.get_language()

        await self.check_if_command(io_obj)

        all_reply_texts = []

        handler = self.find_handler(io_obj.state)

        jump_no = 0
        while jump_no < self.MAX_JUMPS:
            await handler(io_obj)

            if io_obj.out_text:
                all_reply_texts.append(io_obj.out_text)

            handler = self.find_handler(io_obj.state)

            if io_obj.asked:
                break

            jump_no += 1
        else:
            logging.error(f'handle recursion detected!')

        await profile.set_dialog_state(io_obj.state)
        await profile.activity()

        if all_reply_texts:
            if io_obj.join_messages:
                text_sum = NEW_LINE.join(all_reply_texts)
                await message.reply(text_sum,
                                    reply=False,
                                    reply_markup=io_obj.out_keyboard,
                                    disable_notification=True)
            else:
                for reply_text in all_reply_texts:
                    await message.reply(reply_text, reply=False,
                                        reply_markup=io_obj.out_keyboard,
                                        disable_notification=True)
