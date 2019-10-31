from chat.msg_io import *
from tasks.weight_control import *


@sentence
async def ask_current_weight(io: DialogIO):
    lang = io.language
    weight = ask_for_number(io, lang.ap_prompt_today_weight,
                            40, 500, lang.ap_prompt_weight_err)
    if weight == CANCELLED:
        io.back()
    elif weight is not None:
        wp = WeightProfile(io.profile, weight)

        reported = await wp.report_aim_percent()
        if reported:
            io.reply(lang.ap_progress(wp.aim_percent))

            y_weight = await wp.get_yesterday_weight()
            if y_weight is not None:
                delta = abs(y_weight - weight)
                if y_weight > weight:
                    io.add(lang.ap_drop_weight(delta))
                elif y_weight < weight:
                    io.add(lang.ap_gain_weight(delta))
                else:
                    io.add(lang.ap_same_weight)

            # graph
            png = await wp.plot_weight_graph(n_days=30)
            io.send_image(png, lang.ap_chart_name)

        io.back()


@sentence
async def ask_weight_start(io: DialogIO):
    weight = ask_for_number(io, io.language.ap_prompt_start_weight,
                            40, 500, io.language.ap_prompt_weight_err)
    if weight is not None:
        await WeightProfile(io.profile).set_weight_start(weight)
        io.back()


@sentence
async def ask_weight_aim(io: DialogIO):
    weight = ask_for_number(io, io.language.ap_prompt_aim_weight,
                            40, 500, io.language.ap_prompt_weight_err)
    if weight is not None:
        await WeightProfile(io.profile).set_weight_aim(weight)
        io.back()


@sentence
async def ask_aim_menu(io: DialogIO):
    wp = WeightProfile(io.profile)

    weight_start = await wp.get_weight_start()
    if weight_start is None:
        return io.push(ask_weight_start)

    weight_aim = await wp.get_weight_aim()
    if weight_aim is None:
        return io.push(ask_weight_aim)

    lang = io.language

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
