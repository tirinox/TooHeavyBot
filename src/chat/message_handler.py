from chat.msg_io import *
from util.config import Config
from tasks.notify_weight import fix_bad_notifications


START_COMMAND = '/start'
RESET_COMMAND = '/reset'
SERVICE_COMMAND = '/service'


class MessageHandler:
    MAX_JUMPS = 50

    def __init__(self, handlers: dict, initial_handler):
        assert handlers
        self.handlers = handlers

        assert initial_handler
        self.initial_handler = initial_handler

        self.admins = list(map(str, Config().get('admin.list', [])))

    def is_admin(self, io: DialogIO):
        return str(io.message.from_user.id) in self.admins

    async def handle_start(self, io: DialogIO, code: str):
        ...

    async def handle_service(self, io: DialogIO):
        await fix_bad_notifications()
        await io.message.reply('Service done!')

    async def check_if_command(self, io: DialogIO):
        text = str(io.text)
        if text.startswith(START_COMMAND):
            code = text[len(START_COMMAND):].strip()
            await self.handle_start(io, code)
        elif text.startswith(RESET_COMMAND):
            io.state = {}
            await io.message.reply('RESET DONE!')
        elif text.startswith(SERVICE_COMMAND) and self.is_admin(io):
            await self.handle_service(io)
        else:
            return False
        return True

    def find_handler(self, state: dict):
        handler_name = state.get(CURRENT_FUNCTION_KEY, None)

        if not handler_name or handler_name not in self.handlers:
            state[CURRENT_FUNCTION_KEY] = fname(self.initial_handler)
            return self.initial_handler
        return self.handlers[handler_name]

    async def _send_texts(self, io: DialogIO, texts: list):
        if texts:
            text_sum = NEW_LINE.join(texts)
            await io.message.reply(text_sum,
                                   reply=False,
                                   reply_markup=io.out_keyboard,
                                   disable_notification=True)

    async def handle(self, message: Message):
        profile = Profile(message.from_user.id)
        dialog_state = await profile.dialog_state()

        io_obj = DialogIO(message, profile, message.text, dialog_state)
        io_obj.location = message.location
        io_obj.language = await profile.get_language()

        await profile.activity()

        if await self.check_if_command(io_obj):
            return

        all_reply_texts = []

        handler = self.find_handler(io_obj.state)

        jump_no = 0
        while jump_no < self.MAX_JUMPS:
            await handler(io_obj)

            if io_obj.out_text:
                all_reply_texts.append(io_obj.out_text)

            if io_obj.out_image or io_obj.new_message:
                await self._send_texts(io_obj, all_reply_texts)
                if io_obj.out_image:
                    await message.answer_photo(photo=io_obj.out_image, caption=io_obj.out_image_caption)
                    io_obj.out_image = None
                    io_obj.out_image_caption = None
                all_reply_texts = []
                io_obj.new_message = False

            if io_obj.asked:
                break

            handler = self.find_handler(io_obj.state)

            jump_no += 1
        else:
            logging.error(f'handle recursion detected!')

        await profile.set_dialog_state(io_obj.state)
        await self._send_texts(io_obj, all_reply_texts)
