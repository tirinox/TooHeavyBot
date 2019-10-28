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
from models.timeseries import TimePoint
from tasks.weight_control import WEIGHT


USER_ID = 102

last_keyboard_anwer_map = {}


async def testus():
    pass
    # their_now = now_local_dt() - timedelta(days=1)
    # tp = TimePoint(WEIGHT, USER_ID, their_now)
    # tp.value = {
    #     'weight': 102,
    #     'percent': 35,
    #     'ts': int(their_now.timestamp())
    # }
    # await tp.save()


class FakeMessage(Message):
    async def reply(self, text, parse_mode=None,
                    disable_web_page_preview=None,
                    disable_notification=None,
                    reply_markup=None, reply=True) -> Message:

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
    global last_keyboard_anwer_map

    await testus()

    while True:
        # i know that input() is sync, but for local testing it is totally OK!
        text_message = input('> ').strip()
        if text_message in ['/quit', '/exit']:
            break
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
