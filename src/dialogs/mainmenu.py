from dialogs.best_weight import *
from dialogs.aim_percent import *
from msg_io import *


@sentence
async def main_menu(io: DialogIO):
    result = create_menu(io, prompt="Привет! "
                                    "Я робот-тренер и помогу тебе достичь идеального веса "
                                    "(похудеть или набрать массу)!",
                         variants=[('Мой идеальный вес', 'ideal_weight'),
                                   ('Процент цели?', 'aim_percent')])
    if result == 'ideal_weight':
        return io.push(best_weight_entry)
    elif result == 'aim_percent':
        # return io.push(aim_percent_entry)
        return io.ask('not implemented!')


