import threading
import typing
from unittest.mock import MagicMock

from aiogram.types import Message, base, InlineKeyboardMarkup, ForceReply

from chat.message_handler import MessageHandler
from dialogs import *
from tasks.delete_profile import delete_profile
from tasks.notify_weight import *
from tasks.task_manager import TaskManager
from util.config import Config
from util.database import print_database
from chat.command_handler import CommandHandler

last_keyboard_anwer_map = {}


async def testus():
    ...


class FakeMessage(Message):
    async def reply(self, text, parse_mode=None,
                    disable_web_page_preview=None,
                    disable_notification=None,
                    reply_markup=None, reply=True) -> Message:

        # it know that globals is bad, but for local test it's OK!
        global last_keyboard_anwer_map
        last_keyboard_anwer_map = {}

        print(text)

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

    async def answer_photo(self, photo: typing.Union[base.InputFile, base.String],
                           caption: typing.Union[base.String, None] = None,
                           parse_mode: typing.Union[base.String, None] = None,
                           disable_notification: typing.Union[base.Boolean, None] = None,
                           reply_markup: typing.Union[InlineKeyboardMarkup,
                                                      ReplyKeyboardMarkup,
                                                      ReplyKeyboardRemove,
                                                      ForceReply, None] = None, reply: base.Boolean = False) -> Message:
        print('[Photo]')
        return self


async def async_input(prompt):
    loop = asyncio.get_event_loop()
    fut = loop.create_future()

    def _run():
        line = input(prompt)
        loop.call_soon_threadsafe(fut.set_result, line)

    threading.Thread(target=_run, daemon=True).start()
    return await fut


async def dispatch_message_to_handler(message_handler: MessageHandler, message: FakeMessage, local_uid):
    from_user = MagicMock()
    from_user.id = local_uid
    message.from_user = from_user

    await message_handler.handle(message)


async def my_db(user_id):
    await print_database(f'Profile:{user_id}:*')


async def process_text_message(message_handler: MessageHandler, text_message, local_uid):
    if text_message in ['/quit', '/exit']:
        return False
    elif text_message == '/reset':
        await Profile(local_uid).set_dialog_state(None)
    elif text_message.startswith('/dbs'):
        await print_database(text_message[4:].strip())
    elif text_message.startswith('/kill'):
        user_id = int(text_message[5:].strip())
        await delete_profile(user_id)
    elif text_message == '/me':
        await my_db(local_uid)
    elif text_message.startswith('/loc'):
        _, lat, lon = filter(bool, text_message.split(' '))
        message = FakeMessage()
        message.location = Location(latitude=float(lat),
                                    longitude=float(lon))
        await dispatch_message_to_handler(message_handler, message, local_uid)
    else:
        # translate number to actual item text
        if text_message in last_keyboard_anwer_map:
            text_message = last_keyboard_anwer_map[text_message]
            print(f'({text_message})')

        message = FakeMessage(text=text_message)
        await dispatch_message_to_handler(message_handler, message, local_uid)
    return True


async def repl_loop(message_handler: MessageHandler, local_uid):
    global last_keyboard_anwer_map

    await testus()

    await process_text_message(message_handler, '-----BOOTSTRAP----', local_uid)
    while True:
        text_message = (await async_input('>')).strip()
        if not await process_text_message(message_handler, text_message, local_uid):
            break

    print('Buy!')


class FakeBot(TelegramBot):
    def __init__(self):
        ...

    async def send_text(self, user_id, message):
        return print(f'send to {user_id}: {message}')


def main():
    print('This is a local test suite based in inputs. Works without telegram connection')
    print('  Type /exit or /quit to exit.')
    print('  Type /dbs [key_pattern] to view redis database.')
    print('  Type /kill <user_id> to delete the user.')
    print('  Type /reset to reset the dialog state.')
    print('  Type /loc <latitude> <longitude> to send location.')
    print('\n')

    user_id = input('User ID? (Press enter for default):').strip()
    if not user_id:
        user_id = 102
    else:
        user_id = int(user_id)

    config = Config()
    logging.basicConfig(level=logging.INFO if config.is_debug else logging.ERROR)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(DB().connect())

    task_manager = TaskManager(FakeBot())
    task_manager.run_on_loop(loop)

    handlers = get_message_handlers(globals())
    message_handler = MessageHandler(handlers,
                                     initial_handler=ENTRY_POINT,
                                     command_handler=CommandHandler())

    loop.run_until_complete(repl_loop(message_handler, user_id))


if __name__ == '__main__':
    main()
