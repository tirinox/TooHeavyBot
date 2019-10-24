from chat.msg_io import *
from util.date import *
from util import chunks
from datetime import datetime
from tasks.notify_weight import activate_notification, deactivate_notification


@sentence
async def ask_time_zone(io: DialogIO):
    now_time = datetime.now().strftime('%H:%M')
    prompt = (f'У нас сейчас {now_time}.\n'
              'Сколько у вас сейчас времени?\n'
              'Выберите вариант, варианты можно прокручивать:')

    now = datetime.now()

    def shift_to_time(s):
        their_now = date_shift(now, s)
        return format_date_for_tz_selector(their_now)

    variants = [(shift_to_time(s), s) for s in POSSIBLE_TIMEZONE_SHIFTS]
    variants_columned = list(chunks(variants, n=3))
    result = create_menu(io, prompt, variants_columned)

    if result is not None:
        await io.profile.set_time_shift(result)
        tz_names = ', '.join(possible_timezones(result))
        io.back(f'Часовой пояс установлен: ({tz_names})')


@sentence
async def ask_notification_time(io: DialogIO):
    not_notify_text = 'Не уведомлять'
    back_text = 'Назад'

    if not io.asked:
        io.ask(f'Давайте настроим напонимание о том, что вам пора внести вес. Введите время в формате ЧЧ:ММ - 24 часа.',
               keyboard=[[not_notify_text], [back_text]])
    else:
        user_id = io.profile.user_id
        if io.text == not_notify_text:
            await deactivate_notification(user_id)
            io.back('Напонимание выключено!')
        elif io.text == back_text:
            io.back()
        else:
            try:
                hh, mm = hour_and_min_from_str(io.text)
                await activate_notification(user_id, hh, mm)
                io.reply(f'Напонимание установлено!').back()
            except (AssertionError, ValueError):
                io.ask('Кажется, вы меня не так поняли! Введите время в формате ЧЧ:ММ - 24 часа.')


@sentence
async def settings_menu(io: DialogIO):
    result = create_menu(io, 'Настройки бота:',
                         variants=[
                             [('Часовой пояс', 1)],
                             [('Напоминание', 2)],
                             [('Назад', 'back')]
                         ])
    if result == 1:
        return io.push(ask_time_zone)
    elif result == 2:
        return io.push(ask_notification_time)
    elif result == 'back':
        return io.back()
