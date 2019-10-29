from dialogs.aim_percent import *
from dialogs.settings import *
from chat.msg_io import *


@sentence
async def main_menu(io: DialogIO):
    prompt = io.language.hello

    lang = await io.profile.get_prop(Profile.LANGUAGE_KEY)
    if lang is None:
        return io.push(ask_language)

    tz_name = await io.profile.get_time_zone()
    if tz_name is None:
        return io.push(ask_time_zone)

    result = create_menu(io, prompt,
                         variants=[
                             [(io.language.mm_aim_percent, 1)],
                             [(io.language.mm_settings, 2)]
                         ])
    if result == 1:
        return io.push(aim_percent_entry)
    elif result == 2:
        return io.push(settings_menu)
