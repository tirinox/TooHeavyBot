from dialogs.best_weight import *
from dialogs.aim_percent import *
from msg_io import *
from util.date import estimate_time_shift_from_server_to_user, hour_and_min_from_str
from datetime import datetime



@sentence
async def ask_time_zone(io: DialogIO):
    if not io.asked:
        now_time = datetime.now().strftime('%H:%M')
        io.ask(f'У нас сейчас {now_time}.\n'
               'Сколько у вас сейчас времени?\n'
               'Введите время в формате ЧЧ:ММ - 24 часа.')
    else:
        try:
            hh, mm = hour_and_min_from_str(io.text)
            shift = estimate_time_shift_from_server_to_user(hh, mm)
            await io.profile.set_time_shift(shift)

            io.back()
        except (AssertionError, ValueError):
            io.ask('Кажется, вы меня не так поняли! Введите время в формате ЧЧ:ММ - 24 часа.')


@sentence
async def main_menu(io: DialogIO):
    prompt = """Привет! Я робот-тренер и помогу тебе достичь идеального веса (похудеть или набрать массу)!"""

    timeoffset = await io.profile.get_time_shift()
    if timeoffset is None:
        return io.push(ask_time_zone)

    result = create_menu(io, prompt,
                         variants=[('Мой идеальный вес', 'ideal_weight'),
                                   ('Процент цели?', 'aim_percent')])
    if result == 'ideal_weight':
        return io.push(best_weight_entry)
    elif result == 'aim_percent':
        return io.push(aim_percent_entry)
