from chat.msg_io import *
from util.config import Config
from tasks.notify_weight import WeightNotifier
from aiogram.types import Message

START_COMMAND = '/start'
RESET_COMMAND = '/reset'
SERVICE_COMMAND = '/service'


class CommandHandler:
    def __init__(self):
        self.admins = list(map(str, Config().get('admin.list', [])))

    def is_admin(self, message: Message):
        return str(message.from_user.id) in self.admins

    async def _handle_start(self, code: str):
        ...

    async def _handle_service(self, message: Message):
        await WeightNotifier.fix_bad_notifications()
        await message.reply('Service done!')

    async def _handle_reset(self, message: Message, io: DialogIO):
        io.state = {}
        await io.save_dialog_state()
        await message.reply('Reset done!')

    async def check_if_command(self, message: Message, io: DialogIO):
        text = str(message.text)
        if text.startswith(START_COMMAND):
            code = text[len(START_COMMAND):].strip()
            await self._handle_start(code)
        elif text.startswith(RESET_COMMAND):
            io.state = {}
            await message.reply('Reset done!')
        elif text.startswith(SERVICE_COMMAND) and self.is_admin(message):
            await self._handle_service(message)
        else:
            return False
        return True
