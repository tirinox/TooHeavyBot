from chat.msg_io import *
from util.date import *
import pytz
from tasks.notify_weight import activate_notification, deactivate_notification
from tasks.change_timezone import change_timezone
from timezonefinder import TimezoneFinder

tz_finder = TimezoneFinder(in_memory=True)


@sentence
async def ask_time_zone(io: DialogIO):
    prompt = (f'Чтобы вовремя отправлять вам уведомления, нам нужно узнать ваш часовой пояс.\n\n'
              'Вы может отправить геолокацию, чтобы мы определели часовой пояс. Не обязательно '
              'отправлять ваш точный адрес. Вы можете отправить любую локацию из вашего часового пояса.')
              # 'Или вы можете написать название вашего города, чтобы мы поискали в своей базе:')

    back_text = 'Назад'

    if not io.asked:
        io.ask(prompt, [
            [KeyboardButton('📍 Отправить локацию', request_location=True)],
            [KeyboardButton(back_text)]
        ])
    else:
        if io.text == back_text:
            io.back()
        elif io.location:
            tz_name = tz_finder.timezone_at(lng=io.location.longitude, lat=io.location.latitude)
            try:
                pytz.timezone(tz_name)
            except pytz.UnknownTimeZoneError:
                io.ask('Мы не смогли найти подходящий часовой пояс для вашей локации. '
                       'Введите название города вручную:')
            else:
                await change_timezone(io.profile, tz_name)
                io.reply(f'Мы установили, что ваш часовой пояс: <b>{tz_name}</b>. Верно?\n').back()
        else:
            io.ask('Не знаю такого города...')


@sentence
async def ask_notification_time(io: DialogIO):
    not_notify_text = 'Не уведомлять'
    back_text = 'Назад'
    hint_time = 'Введите время в формате ЧЧ:ММ или ЧЧ ММ - 24 часа. Например: "8:00" или "12 05".'

    if not io.asked:
        io.ask(f'Давайте настроим напонимание о том, что вам пора внести вес. {hint_time}',
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
                delta = await activate_notification(io.profile, hh, mm)
                d_hh, d_mm = hh_mm_from_timedelta(delta)
                io.back(f'Напонимание установлено! Оно прозвучит через {d_hh} ч. {d_mm} мин.')
            except (AssertionError, ValueError):
                io.ask(f'Кажется, вы меня не так поняли! {hint_time}')


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
