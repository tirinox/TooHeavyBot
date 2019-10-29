from util.config import Config
from util.database import DB, print_database
from unittest.mock import MagicMock
from dialogs import *
from chat.msg_io import get_message_handlers
from chat.message_handler import MessageHandler
import asyncio
from aiogram.types import Message
from tasks import task_manager
from tasks.delete_profile import delete_profile
import threading

USER_ID = 102

last_keyboard_anwer_map = {}


async def testus():
    pass


class FakeMessage(Message):
    async def reply(self, text, parse_mode=None,
                    disable_web_page_preview=None,
                    disable_notification=None,
                    reply_markup=None, reply=True) -> Message:

        # it know that globals is bad, but for local test it's OK!
        global last_keyboard_anwer_map
        last_keyboard_anwer_map = {}

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


async def async_input(prompt):
    loop = asyncio.get_event_loop()
    fut = loop.create_future()

    def _run():
        line = input(prompt)
        loop.call_soon_threadsafe(fut.set_result, line)

    threading.Thread(target=_run, daemon=True).start()
    return await fut


async def process_text_message(text_message):
    if text_message in ['/quit', '/exit']:
        return False
    elif text_message == '/reset':
        await Profile(USER_ID).set_dialog_state(None)
    elif text_message.startswith('/dbs'):
        await print_database(text_message[4:].strip())
    elif text_message.startswith('/kill'):
        user_id = int(text_message[5:].strip())
        await delete_profile(user_id)
    else:
        # translate number to actual item text
        if text_message in last_keyboard_anwer_map:
            text_message = last_keyboard_anwer_map[text_message]
            print(f'({text_message})')

        message = FakeMessage(text=text_message)
        from_user = MagicMock()
        from_user.id = USER_ID
        message.from_user = from_user

        await message_handler.handle(message)
    return True


async def repl_loop(message_handler: MessageHandler):
    global last_keyboard_anwer_map

    await testus()

    await process_text_message('-----BOOTSTRAP----')
    while True:
        text_message = (await async_input('>')).strip()
        if not await process_text_message(text_message):
            break

    print('Buy!')


class FakeBot:
    async def send_text(self, user_id, message):
        return print(f'send to {user_id}: {message}')


if __name__ == '__main__':
    print('This is a local test suite based in inputs. Works without telegram connection')
    print('  Type /exit or /quit to exit.')
    print('  Type /dbs [key_pattern] to view redis database.')
    print('  Type /kill <user_id> to delete the user.')
    print('  Type /reset to reset the dialog state.')
    print('\n')

    config = Config()
    logging.basicConfig(level=logging.INFO if config.is_debug else logging.ERROR)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(DB().connect())

    task_manager.run_on_loop(loop, FakeBot())

    handlers = get_message_handlers(globals())
    message_handler = MessageHandler(handlers, initial_handler=ENTRY_POINT)

    loop.run_until_complete(repl_loop(message_handler))
