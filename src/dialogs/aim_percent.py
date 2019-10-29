from chat.msg_io import *
from util import try_parse_float
from tasks.weight_control import report_weight, get_yesterday_weight


def aim_percent_formula(current, ideal, start):
    p = (1.0 - (current - ideal) / (start - ideal)) * 100.0
    return round(p, 2)


def weight_format(w):
    return f'{w:.1f}'


@sentence
async def ask_current_weight(io: DialogIO):
    lang = io.language
    weight = ask_for_number(io, lang.ap_prompt_today_weight,
                            40, 500, lang.ap_prompt_weight_err)
    if weight == CANCELLED:
        io.back()
    elif weight is not None:
        weight_start = try_parse_float(await io.profile.get_prop('weight_start'))
        weight_aim = try_parse_float(await io.profile.get_prop('weight_aim'))
        if weight_start and weight_aim:
            percent = aim_percent_formula(weight, weight_aim, weight_start)
            io.reply(lang.ap_progress(percent))

            await report_weight(io.profile, weight, percent)

            y_weight = await get_yesterday_weight(io.profile)
            if y_weight is not None:
                delta = abs(y_weight - weight)
                if y_weight > weight:
                    io.add(lang.ap_drop_weight(delta))
                elif y_weight < weight:
                    io.add(lang.ap_gain_weight(delta))
                else:
                    io.add(lang.ap_same_weight)

        io.back()


@sentence
async def ask_weight_start(io: DialogIO):
    weight = ask_for_number(io, io.language.ap_prompt_start_weight,
                            40, 500, io.language.ap_prompt_weight_err)
    if weight is not None:
        await io.profile.set_prop('weight_start', weight)
        io.back()


@sentence
async def ask_weight_aim(io: DialogIO):
    weight = ask_for_number(io, io.language.ap_prompt_aim_weight,
                            40, 500, io.language.ap_prompt_weight_err)
    if weight is not None:
        await io.profile.set_prop('weight_aim', weight)
        io.back()


@sentence
async def ask_aim_menu(io: DialogIO):
    weight_start = try_parse_float(await io.profile.get_prop('weight_start'))

    if not weight_start:
        return io.push(ask_weight_start)

    weight_aim = try_parse_float(await io.profile.get_prop('weight_aim'))
    if not weight_aim:
        return io.push(ask_weight_aim)

    lang = io.language

    print(lang.ap_change_start)

    result = create_menu(io, lang.ap_menu, variants=[
        [(lang.ap_enter_today, 'enter_today_weight')],
        [
            (lang.ap_change_start(weight_start), 'change_start_weight'),
            (lang.ap_change_aim(weight_aim), 'change_aim_weight')
        ],
        [(lang.back, 'back')]
    ])

    if result == 'enter_today_weight':
        io.push(ask_current_weight)
    elif result == 'change_start_weight':
        io.push(ask_weight_start)
    elif result == 'change_aim_weight':
        io.push(ask_weight_aim)
    elif result == 'back':
        io.back()


aim_percent_entry = ask_aim_menu
