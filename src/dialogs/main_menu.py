from dialogs.best_weight import *
from dialogs.aim_percent import *
from dialogs.settings import *
from chat.msg_io import *


@sentence
async def main_menu(io: DialogIO):
    prompt = """Привет! Я робот-тренер и помогу тебе достичь идеального веса (похудеть или набрать массу)!"""

    tz_name = await io.profile.get_time_zone()
    if tz_name is None:
        return io.push(ask_time_zone)

    result = create_menu(io, prompt,
                         variants=[
                             [('Мой идеальный вес', 1)],
                             [('Процент цели?', 2)],
                             [('Настройки', 3)]
                         ])
    if result == 1:
        return io.push(best_weight_entry)
    elif result == 2:
        return io.push(aim_percent_entry)
    elif result == 3:
        return io.push(settings_menu)
