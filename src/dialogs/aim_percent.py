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
    weight = ask_for_number(io, 'Введите ваш вес сегодня в кг:',
                            40, 500, 'Должно быть число от 40 до 500!')
    if weight is not None:
        weight_start = try_parse_float(await io.profile.get_prop('weight_start'))
        weight_aim = try_parse_float(await io.profile.get_prop('weight_aim'))
        if weight_start and weight_aim:
            percent = aim_percent_formula(weight, weight_aim, weight_start)
            io.reply(f'\nВаш прогресс:\n {percent:.2f} %\n')

            await report_weight(io.profile, weight, percent)

            y_weight = await get_yesterday_weight(io.profile)
            delta = abs(y_weight - weight)
            if y_weight > weight:
                io.add(f'Вы похудели на {delta:0.2f} кг со вчера.\n')
            elif y_weight < weight:
                io.add(f'Вы поправились на {delta:0.2f} кг со вчера.\n')
            else:
                io.add(f'Ваш вес не изменился со вчера.\n')

        io.back()


@sentence
async def ask_weight_start(io: DialogIO):
    weight = ask_for_number(io, 'Введите ваш начальный вес в кг. Это будет 0 % цели:',
                            40, 500, 'Должно быть число от 40 до 500!')
    if weight is not None:
        await io.profile.set_prop('weight_start', weight)
        io.back()


@sentence
async def ask_weight_aim(io: DialogIO):
    weight = ask_for_number(io, 'Введите ваш целевой вес в кг. Это будет 100 % цели:',
                            40, 500, 'Должно быть число от 40 до 500!')
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

    result = create_menu(io, "Мы посчитаем процент вашего прогресса:", variants=[
        [('Внести вес сегодня', 'enter_today_weight')],
        [
            (f'Изменить старт ({weight_format(weight_start)} кг)', 'change_start_weight'),
            (f'Изменить цель ({weight_format(weight_aim)} кг)', 'change_aim_weight')
        ],
        [('Назад', 'back')]
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
