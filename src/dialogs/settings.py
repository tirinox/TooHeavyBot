from chat.msg_io import *
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

            io.reply(f'Наша разница во времени: {shift} минут.').back()
        except (AssertionError, ValueError):
            io.ask('Кажется, вы меня не так поняли! Введите время в формате ЧЧ:ММ - 24 часа.')


@sentence
async def ask_notification_time(io: DialogIO):
    if not io.asked:
        io.ask(f'Давайте настроим напонимание о том, что вам пора внести вес. Введите время в формате ЧЧ:ММ - 24 часа.')
    else:
        try:
            hh, mm = hour_and_min_from_str(io.text)

            # todo: set notification time

            io.reply(f'Напонимание установлено!').back()
        except (AssertionError, ValueError):
            io.ask('Кажется, вы меня не так поняли! Введите время в формате ЧЧ:ММ - 24 часа.')


@sentence
async def settings_menu(io: DialogIO):
    result = create_menu(io, 'Настройки бота:',
                         variants=[
                             [('Сверить часы', 1)],
                             [('Напоминание', 2)],
                             [('Назад', 'back')]
                         ])
    if result == 1:
        return io.push(ask_time_zone)
    elif result == 2:
        return io.back().reply('Нет еще!!')
    elif result == 'back':
        return io.back()
