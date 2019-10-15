from dialogs.best_weight import *
from dialogs.aim_percent import *
from msg_io import *


@require_answer
async def main_menu_answer(io: DialogIO):
    result = Menu.value(io)
    if result == 'ideal_weight':
        return io.next(best_weight_entry)
    else:
        return io.next(aim_percent_entry)


@sentence
async def main_menu(io: DialogIO):
    return Menu.create(io, main_menu, main_menu_answer,
                       prompt="Привет! "
                              "Я робот-тренер и помогу тебе достичь идеального веса "
                              "(похудеть или набрать массу)!",
                       variants=[('Мой идеальный вес', 'ideal_weight'),
                                 ('Процент цели?', 'aim_percent')])
