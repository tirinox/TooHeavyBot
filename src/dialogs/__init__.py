from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup


class MessageHandler:
    def __init__(self, m: Message):
        self.message = m

    async def handle_start(self, code):
        if code:
            # надо прервать любой диалог и обрбаотать диалог с кодом
            await self.message.reply(f"Hi!\nYour code is {code}")
        else:
            # сделать стэйт main menu
            await self.message.reply(f'Hi! this is start without params!')

    async def handle(self):
        text = str(self.message.text)

        start_prefix = '/start'
        if text.startswith(start_prefix):
            code = text[len(start_prefix):].strip()
            await self.handle_start(code)
        else:
            await self.message.reply(text, reply=False, reply_markup=ReplyKeyboardMarkup([
                [KeyboardButton('Yes'), KeyboardButton('No')]
            ]))
