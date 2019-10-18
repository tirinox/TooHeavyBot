import typing

from util.config import Config
from util.database import DB
import logging
from unittest.mock import MagicMock
from dialogs import *
from msg_io import get_message_handlers
from message_handler import MessageHandler
import asyncio
from aiogram.types import Message, base, InlineKeyboardMarkup, ForceReply


last_keyboard_anwer_map = {}


class FakeMessage(Message):
    async def reply(self, text: base.String, parse_mode: typing.Union[base.String, None] = None,
                    disable_web_page_preview: typing.Union[base.Boolean, None] = None,
                    disable_notification: typing.Union[base.Boolean, None] = None,
                    reply_markup: typing.Union[InlineKeyboardMarkup,
                                               ReplyKeyboardMarkup,
                                               ReplyKeyboardRemove,
                                               ForceReply, None] = None, reply: base.Boolean = True) -> Message:

        # it know that globals is bad, but for local test it's OK!
        global last_keyboard_anwer_map
        last_keyboard_anwer_map = {}

        print('<', text)
        if isinstance(reply_markup, ReplyKeyboardRemove):
            print('[keyboard removed]')
        elif isinstance(reply_markup, ReplyKeyboardMarkup):
            i = 1
            for row in reply_markup.keyboard:
                for button in row:
                    print(f'{i}. {button.text}')
                    last_keyboard_anwer_map[str(i)] = button.text
                    i += 1
        return self


async def repl_loop(message_handler: MessageHandler):
    USER_ID = 101

    global last_keyboard_anwer_map

    while True:
        # i know that input() is sync, but for local testing it is totally OK!
        text_message = input('> ').strip()
        if text_message in ['/quit', '/exit']:
            break

        if text_message == '/reset':
            await Profile(USER_ID).set_dialog_state(None)
            continue

        # translate number to actual item text
        if text_message in last_keyboard_anwer_map:
            text_message = last_keyboard_anwer_map[text_message]
            print(f'({text_message})')

        message = FakeMessage(text=text_message)
        from_user = MagicMock()
        from_user.id = USER_ID
        message.from_user = from_user

        await message_handler.handle(message)

    print('Buy!')


if __name__ == '__main__':
    print('This is a local test suite based in inputs. Works without telegram connection')

    config = Config()
    logging.basicConfig(level=logging.INFO if config.is_debug else logging.ERROR)


    loop = asyncio.get_event_loop()
    loop.run_until_complete(DB().connect())

    handlers = get_message_handlers(globals())
    message_handler = MessageHandler(handlers, initial_handler=ENTRY_POINT)

    loop.run_until_complete(repl_loop(message_handler))
