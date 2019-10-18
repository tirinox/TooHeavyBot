from dialogs.best_weight import *
from dialogs.aim_percent import *
from msg_io import *
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
            hh, mm = io.text.strip().split(':')
            hh, mm = int(hh), int(mm)

            assert 0 <= hh < 24
            assert 0 <= mm < 60

            now = datetime.now()
            my_hh, my_mm = now.hour, now.minute

            diff = ((my_hh - hh) * 60 + my_mm - mm) / 30.0
            diff = round(diff) / 2.0

            await io.profile.set_prop('time_zone_offset', diff)

            io.back()
        except (AssertionError, ValueError):
            io.ask('Кажется, вы меня не так поняли! Введите время в формате ЧЧ:ММ - 24 часа.')


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
