from dialogs.mainmenu import *
from dialogs.best_weight import *
from msg_io import is_sentence, MAIN_HANDLER_KEY


def get_message_handlers():
    handlers = {name: obj for name, obj in globals().items() if is_sentence(obj)}
    handlers[MAIN_HANDLER_KEY] = main_menu
    return handlers
