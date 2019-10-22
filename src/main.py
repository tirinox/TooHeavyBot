from util.config import Config
from util.database import DB
from dialogs import *
from chat.msg_io import get_message_handlers
from chat.message_handler import MessageHandler
import asyncio
from tasks import task_manager
from chat.bot_telegram import TelegramBot


if __name__ == '__main__':
    config = Config()
    logging.basicConfig(level=logging.INFO if config.is_debug else logging.ERROR)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(DB().connect())
    task_manager.run_on_loop(loop)

    handlers = get_message_handlers(globals())
    message_handler = MessageHandler(handlers, initial_handler=ENTRY_POINT)

    bot = TelegramBot(message_handler.handle)
    bot.serve()
