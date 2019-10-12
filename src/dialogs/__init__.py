from dialogs.mainmenu import *
from dialogs.best_weight import *


def get_handlers():
    handlers = {name: obj for name, obj in globals().items() if name.startswith('dlg_')}
    handlers['main'] = dlg_main_menu
    return handlers
