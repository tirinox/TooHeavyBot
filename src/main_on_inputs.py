import threading
from unittest.mock import MagicMock

from chat.command_handler import CommandHandler
from dialogs.all import *
from tasks.delete_profile import delete_profile
from tasks.notify_weight import *
from tasks.task_manager import TaskManager
from util.config import Config
from util.database import print_database


class PrintSender(AbstractMessageSender):
    def __init__(self):
        super().__init__()
        self.last_keyboard_anwer_map = {}

    async def send_photo(self, to_uid, photo, caption=None):
        print(f'[Photo] caption = {caption}')
        return self

    async def send_text(self, to_uid, text, keyboard=None, disable_notification=False):
        print(f'[to #{to_uid}]: {text}')

        if isinstance(keyboard, ReplyKeyboardRemove):
            self.last_keyboard_anwer_map = {}
            print('[keyboard removed]')
        elif isinstance(keyboard, ReplyKeyboardMarkup):
            i = 1
            for row in keyboard.keyboard:
                for button in row:
                    print(f'{i}. {button.text}')
                    self.last_keyboard_anwer_map[str(i)] = button.text
                    i += 1
        return self

    def transform_option_to_text(self, input_text: str):
        option = input_text.strip()
        if option in self.last_keyboard_anwer_map:
            option = self.last_keyboard_anwer_map[option]
            print(f'({option})')
        return option


class BotOnInputs:
    def __init__(self, message_handler: MessageHandler, sender: PrintSender, local_uid):
        self.message_handler = message_handler
        self.sender = sender
        self.local_uid = local_uid

    @staticmethod
    async def async_input(prompt):
        loop = asyncio.get_event_loop()
        fut = loop.create_future()

        def _run():
            line = input(prompt)
            loop.call_soon_threadsafe(fut.set_result, line)

        threading.Thread(target=_run, daemon=True).start()
        return await fut

    async def dispatch_message_to_handler(self, message: Message):
        from_user = MagicMock()
        from_user.id = self.local_uid
        from_user.username = f'local_{self.local_uid}'
        message.from_user = from_user
        await self.message_handler.handle(message)

    @staticmethod
    async def my_db(user_id):
        await print_database(f'Profile:{user_id}:*')

    async def process_text_message(self, text_message):
        if text_message in ['/quit', '/exit']:
            return False
        elif text_message == '/reset':
            await Profile(self.local_uid).set_dialog_state(None)
        elif text_message.startswith('/dbs'):
            await print_database(text_message[4:].strip())
        elif text_message.startswith('/kill'):
            user_id = int(text_message[5:].strip())
            await delete_profile(user_id)
        elif text_message == '/me':
            await self.my_db(self.local_uid)
        elif text_message.startswith('/chuser'):
            user_id = int(text_message[7:].strip())
            self.local_uid = user_id
            await self._bootstrap()
        elif text_message.startswith('/loc'):
            _, lat, lon = filter(bool, text_message.split(' '))
            message = Message()
            message.location = Location(latitude=float(lat),
                                        longitude=float(lon))
            await self.dispatch_message_to_handler(message)
        else:
            text_message = self.sender.transform_option_to_text(text_message)
            message = Message(text=text_message)
            await self.dispatch_message_to_handler(message)
        return True

    async def _bootstrap(self):
        # send something meaningless to reveal a message and keyboard
        await self.process_text_message('')  # bootstrap

    async def repl_loop(self):
        await self._bootstrap()
        while True:
            text_message = (await self.async_input('>')).strip()
            if not await self.process_text_message(text_message):
                break
        print('Buy!')


def main():
    print('This is a local test suite based in inputs. Works without telegram connection')
    print('  Type /exit or /quit to exit.')
    print('  Type /dbs [key_pattern] to view redis database.')
    print('  Type /kill <user_id> to delete the user.')
    print('  Type /reset to reset the dialog state.')
    print('  Type /chuser <user_id> to change current user ID')
    print('  Type /loc <latitude> <longitude> to send location.')
    print('\n')

    user_id = input('User ID? (Press enter for default):').strip()
    if not user_id:
        user_id = 102
    else:
        user_id = int(user_id)

    print(f'Your user ID is {user_id}!')

    config = Config()
    logging.basicConfig(level=logging.INFO if config.is_debug else logging.ERROR)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(DB().connect())

    sender = PrintSender()

    handlers = get_message_handlers(globals())
    message_handler = MessageHandler(handlers,
                                     initial_handler=ENTRY_POINT,
                                     command_handler=CommandHandler(),
                                     sender=sender)

    task_manager = TaskManager(message_handler)
    task_manager.run_on_loop(loop)

    inputs_bot = BotOnInputs(message_handler, sender, user_id)
    loop.run_until_complete(inputs_bot.repl_loop())


if __name__ == '__main__':
    main()
