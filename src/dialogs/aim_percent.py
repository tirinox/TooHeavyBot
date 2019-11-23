from chat.msg_io import *
from tasks.weight_control import *


MIN_WEIGHT = 40
MAX_WEIGHT = 500
GRAPH_DAYS = 30


@sentence
async def ask_current_weight(io: DialogIO):
    lang = io.language
    weight = ask_for_number(io, lang.ap_prompt_today_weight,
                            MIN_WEIGHT, MAX_WEIGHT, lang.ap_prompt_weight_err)
    if weight == CANCELLED:
        io.back()
    elif weight is not None:
        wp = WeightProfile(io.profile, weight)

        reported = await wp.report_aim_percent()
        if reported:

            # f'\nВаш прогресс:\n<b>{percent:.2f} %</b>'
            io.reply(lang.ap_progress(wp.aim_percent)).nl()

            y_weight = await wp.get_yesterday_weight()
            if y_weight:
                delta = abs(y_weight - weight)
                if y_weight > weight:
                    # f'Вы похудели на {delta:0.2f} кг со вчера.'
                    io.add(lang.ap_drop_weight(delta))
                elif y_weight < weight:
                    # f'Вы поправились на {delta:0.2f} кг со вчера.'
                    io.add(lang.ap_gain_weight(delta))
                else:
                    # 'Ваш вес не изменился со вчера.'
                    io.add(lang.ap_same_weight)
            else:
                # "Кажется, вы не вносили вчера вес."
                io.add(lang.ap_you_forgot)

            start_weight_pt = await wp.get_initial_weight_point()
            if start_weight_pt is not None:
                io.nl()
                start_weight = start_weight_pt.weight
                delta = abs(start_weight - weight)
                if start_weight > weight:
                    # f'Вы похудели на {delta:0.2f} кг с самого начала.'
                    io.add(lang.ap_drop_weight_total(delta))
                elif start_weight < weight:
                    # f'Вы набрали {delta:0.2f} кг с самого начала.'
                    io.add(lang.ap_gain_weight_total(delta))
                else:
                    # "Ваш вес не изменился с начала программы."
                    io.add(lang.ap_same_weight_total)

            # graph
            points = await wp.get_weight_points_for_profile(GRAPH_DAYS)
            if len(points) >= 2:

                target_ts = await wp.timestamp_of_target_weight(points)
                if target_ts is not None:
                    now = now_tsi()

                    io.nl()

                    if target_ts < now:
                        # 'Вы движитесь не в том направлении!'
                        io.add(lang.ap_wrong_way)
                    else:
                        days_to_go = int(round((target_ts - now) / DAY))
                        # (f'Вы достигнете цели через {days_to_go} дн.')
                        io.add(lang.ap_days_to_go_l(days_to_go))

                png = await wp.plot_weight_graph(points)
                io.send_image(png, lang.ap_chart_name)

        io.back()


@sentence
async def ask_weight_start(io: DialogIO):
    weight = ask_for_number(io, io.language.ap_prompt_start_weight,
                            MIN_WEIGHT, MAX_WEIGHT, io.language.ap_prompt_weight_err)
    if weight is not None:
        await WeightProfile(io.profile).set_weight_start(weight)
        io.back()


@sentence
async def ask_weight_aim(io: DialogIO):
    weight = ask_for_number(io, io.language.ap_prompt_aim_weight,
                            MIN_WEIGHT, MAX_WEIGHT, io.language.ap_prompt_weight_err)
    if weight is not None:
        weight_start = await WeightProfile(io.profile).get_weight_start()

        if weight_start == weight:
            io.reply(io.language.ap_aim_eq_start_err)
        else:
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
