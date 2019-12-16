from chat.bot_telegram import TelegramBot
from chat.command_handler import CommandHandler
from chat.message_handler import MessageHandler
from dialogs.all import *
from tasks.task_manager import TaskManager
from util.config import Config
from util.database import DB

if __name__ == '__main__':
    config = Config()
    logging.basicConfig(level=logging.INFO if config.is_debug else logging.ERROR)

    loop = asyncio.get_event_loop()

    loop.run_until_complete(DB().connect())

    handlers = get_message_handlers(globals())

    message_handler = MessageHandler(handlers,
                                     initial_handler=ENTRY_POINT,
                                     command_handler=CommandHandler())
    bot = TelegramBot(message_handler)

    task_manager = TaskManager(bot)
    task_manager.run_on_loop(loop)

    bot.serve()
