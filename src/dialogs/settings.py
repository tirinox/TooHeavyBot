from chat.msg_io import *
from util.date import *
from util import chunks
import pytz
from tasks.notify_weight import activate_notification, deactivate_notification
from tasks.change_timezone import change_timezone


@sentence
async def ask_time_zone(io: DialogIO):
    now_dt = now_local_dt()

    now_text = now_dt.strftime('%H:%M')
    prompt = (f'У нас сейчас {now_text}.\n'
              'Сколько у вас сейчас времени?\n'
              'Выберите вариант, варианты можно прокручивать:')

    if not io.asked:
        io.state['now'] = now_dt.isoformat()
    else:
        now_dt = datetime.fromisoformat(io.state['now'])

    def format_date(name):
        their_now = now_dt.astimezone(pytz.timezone(name))
        return format_date_for_tz_selector(their_now)

    variants = [(format_date(tz_name), tz_name) for tz_name in DIFFERENT_TIMEZONE_NAMES]
    variants_columned = list(chunks(variants, n=3))
    result = create_menu(io, prompt, variants_columned)

    if result is not None:
        print('tz name =', result)
        await change_timezone(io.profile, result)
        io.back(f'Часовой пояс установлен.').clear('now')


@sentence
async def ask_notification_time(io: DialogIO):
    not_notify_text = 'Не уведомлять'
    back_text = 'Назад'

    if not io.asked:
        io.ask(f'Давайте настроим напонимание о том, что вам пора внести вес. Введите время в формате ЧЧ:ММ - 24 часа.',
               keyboard=[[not_notify_text], [back_text]])
    else:
        if io.text == not_notify_text:
            await deactivate_notification(io.profile)
            io.back('Напонимание выключено!')
        elif io.text == back_text:
            io.back()
        else:
            try:
                hh, mm = hour_and_min_from_str(io.text)
                await activate_notification(io.profile, hh, mm)
                io.back(f'Напонимание установлено!')
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
