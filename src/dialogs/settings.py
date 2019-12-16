from timezonefinder import TimezoneFinder

from dialogs.best_weight import *
from tasks.change_timezone import change_timezone
from util.date import *
from tasks.notify_weight import WeightNotifier

tz_finder = TimezoneFinder(in_memory=True)


@sentence
async def ask_time_zone(io: DialogIO):
    lang = io.language

    prompt = lang.time_zone_prompt

    kbd = [
        [KeyboardButton(lang.send_location, request_location=True)],
        [KeyboardButton(lang.back)]
    ]

    if not io.asked:
        io.ask(prompt, kbd)
    else:
        if io.text == lang.back:
            io.back()
        elif io.location:
            tz_name = tz_finder.timezone_at(lng=io.location.longitude, lat=io.location.latitude)
            try:
                pytz.timezone(tz_name)
            except pytz.UnknownTimeZoneError:
                io.ask(lang.time_zone_err_bad_loc)
            else:
                await change_timezone(io.profile, tz_name)
                io.reply(lang.time_zone_ok(tz_name)).back()
        else:
            io.ask(lang.time_zone_unknown_city, kbd)


@sentence
async def ask_notification_time(io: DialogIO):
    lang = io.language

    if not io.asked:
        io.ask(lang.s_not_ask,
               keyboard=[[lang.s_not_dont], [lang.back]])
    else:
        if io.text == lang.s_not_dont:
            await WeightNotifier.deactivate_notification(io.profile)
            io.back(lang.s_not_off)
        elif io.text == lang.back:
            io.back()
        else:
            try:
                hh, mm = hour_and_min_from_str(io.text)
                delta = await WeightNotifier.activate_notification(io.profile, hh, mm)
                d_hh, d_mm = hh_mm_from_timedelta(delta)
                io.back(lang.s_not_on(d_hh, d_mm))
            except (AssertionError, ValueError):
                io.ask(lang.s_not_err)


@sentence
async def ask_language(io: DialogIO):
    lang = io.language

    result = create_menu(io, io.language.s_lang_hi, variants=[
        (lang.s_english, 'eng'),
        (lang.s_russian, 'rus')
    ])
    if result in ('eng', 'rus'):
        await io.change_language(result)
        io.reply(io.language.s_lang_set).back()


@sentence
async def settings_menu(io: DialogIO):
    lang = io.language

    result = create_menu(io, lang.s_title,
                         variants=[
                             [(lang.s_timezone, 1), (lang.s_notification, 2)],
                             [(lang.s_language, 3), (lang.s_best_weight, 4)],
                             [(lang.back, 'back')]
                         ])
    if result == 1:
        io.push(ask_time_zone)
    elif result == 2:
        io.push(ask_notification_time)
    elif result == 3:
        io.push(ask_language)
    elif result == 4:
        io.push(best_weight_entry)
    elif result == 'back':
        io.back()
