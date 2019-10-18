from dialogs.best_weight import *
from dialogs.aim_percent import *
from msg_io import *


@sentence
async def ask_time_zone(io: DialogIO):
    if not io.asked:
        io.ask('Сколько у вас сейчас времени?')
    else:

        io.back()


@sentence
async def main_menu(io: DialogIO):
    prompt = """Привет! Я робот-тренер и помогу тебе достичь идеального веса (похудеть или набрать массу)!"""

    timeoffset = await io.profile.get_prop('time_zone_offset')
    if timeoffset is None:
        return io.push(ask_time_zone)

    result = create_menu(io, prompt,
                         variants=[('Мой идеальный вес', 'ideal_weight'),
                                   ('Процент цели?', 'aim_percent')])
    if result == 'ideal_weight':
        return io.push(best_weight_entry)
    elif result == 'aim_percent':
        return io.push(aim_percent_entry)
