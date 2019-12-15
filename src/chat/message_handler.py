from chat.msg_io import *
from util.config import Config
import tasks.notify_weight
from aiogram.types import Message

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

    def is_admin(self, message: Message):
        return str(message.from_user.id) in self.admins

    async def _handle_start(self, io: DialogIO, code: str):
        ...

    async def _handle_service(self, message: Message):
        await tasks.notify_weight.WeightNotifier.fix_bad_notifications()
        await message.reply('Service done!')

    async def _check_if_command(self, message: Message, io: DialogIO):
        text = str(message.text)
        if text.startswith(START_COMMAND):
            code = text[len(START_COMMAND):].strip()
            await self._handle_start(io, code)
        elif text.startswith(RESET_COMMAND):
            io.state = {}
            await message.reply('Reset done!')
        elif text.startswith(SERVICE_COMMAND) and self.is_admin(message):
            await self._handle_service(message)
        else:
            return False
        return True

    def _find_handler(self, state: dict):
        handler_name = state.get(CURRENT_FUNCTION_KEY, None)

        if not handler_name or handler_name not in self.handlers:
            state[CURRENT_FUNCTION_KEY] = fname(self.initial_handler)
            return self.initial_handler
        return self.handlers[handler_name]

    async def _send_texts(self, io: DialogIO, original_message: Message, texts: list):
        if texts:
            text_sum = NEW_LINE.join(texts)
            await original_message.reply(text_sum,
                                         reply=False,
                                         reply_markup=io.out_keyboard,
                                         disable_notification=True)

    async def handle_io(self, io_obj: DialogIO, input_message: Message):
        all_reply_texts = []

        handler = self._find_handler(io_obj.state)

        jump_no = 0
        while jump_no < self.MAX_JUMPS:
            await handler(io_obj)

            if io_obj.out_text:
                all_reply_texts.append(io_obj.out_text)

            if io_obj.out_image or io_obj.new_message:
                await self._send_texts(io_obj, input_message, all_reply_texts)
                if io_obj.out_image:
                    await input_message.answer_photo(photo=io_obj.out_image, caption=io_obj.out_image_caption)
                    io_obj.out_image = None
                    io_obj.out_image_caption = None
                all_reply_texts = []
                io_obj.new_message = False

            if io_obj.asked:
                break

            handler = self._find_handler(io_obj.state)

            jump_no += 1
        else:
            logging.error(f'handle recursion detected!')

        await io_obj.save_dialog_state()
        await self._send_texts(io_obj, input_message, all_reply_texts)

    async def handle(self, input_message: Message):
        profile = Profile(input_message.from_user.id)
        io_obj = await DialogIO.load(profile, input_message.text, input_message.location)
        io_obj.message = input_message

        await io_obj.profile.activity()

        if await self._check_if_command(input_message, io_obj):
            return

        await self.handle_io(io_obj, input_message)
