from msg_io import *
from util import try_parse_float


def aim_percent_formula(current, ideal, start):
    return (1.0 - (current - ideal) / (start - ideal)) * 100.0


def weight_format(w):
    return f'{w:.1f}'

# --------------------------------------------------------------------------------

@require_answer
async def answer_current_weight(io: DialogIO):
    try:
        weight = float(io.text)
        assert 10 <= weight <= 500
        await io.profile.set_prop('weight_today', weight)

        weight_start = try_parse_float(await io.profile.get_prop('weight_start'))
        weight_aim = try_parse_float(await io.profile.get_prop('weight_aim'))
        if weight_start and weight_aim:
            percent = aim_percent_formula(weight, weight_aim, weight_start)
            io.reply(f'\nВаш прогресс:\n {percent:.2f} %\n')

        io.next(ask_aim_menu)
    except (ValueError, AssertionError):
        io.reply('Должно быть число от 10 до 500!').next(answer_current_weight)


@sentence
async def ask_current_weight(io: DialogIO):
    io.reply('Введите ваш вес сегодня в кг:').next(answer_current_weight)


# --------------------------------------------------------------------------------

@require_answer
async def answer_weight_start(io: DialogIO):
    try:
        weight = float(io.text)
        assert 10 <= weight <= 500
        await io.profile.set_prop('weight_start', weight)
        io.next(ask_aim_menu)
    except (ValueError, AssertionError):
        io.reply('Должно быть число от 10 до 500!').next(ask_weight_aim)


@sentence
async def ask_weight_start(io: DialogIO):
    io.reply('Введите ваш начальный вес в кг. Это будет 0 % цели:').next(answer_weight_start)

# --------------------------------------------------------------------------------

@require_answer
async def answer_weight_aim(io: DialogIO):
    try:
        weight = float(io.text)
        assert 10 <= weight <= 500
        await io.profile.set_prop('weight_aim', weight)
        io.next(ask_aim_menu)
    except (ValueError, AssertionError):
        io.reply('Должно быть число от 10 до 500!').next(ask_weight_aim)


@sentence
async def ask_weight_aim(io: DialogIO):
    io.reply('Введите ваш целевой вес в кг. Это будет 100 % цели:').next(answer_weight_aim)

# --------------------------------------------------------------------------------

@require_answer
async def answer_aim_menu(io: DialogIO):
    value = Menu.value(io)
    if value == 'enter_today_weight':
        io.next(ask_current_weight)
    elif value == 'change_start_weight':
        io.next(ask_weight_start)
    elif value == 'change_aim_weight':
        io.next(ask_weight_aim)
    else:
        io.next(None)


@sentence
async def ask_aim_menu(io: DialogIO):
    weight_start = try_parse_float(await io.profile.get_prop('weight_start'))

    if not weight_start:
        return io.next(ask_weight_start)

    weight_aim = try_parse_float(await io.profile.get_prop('weight_aim'))
    if not weight_aim:
        return io.next(ask_weight_aim)

    Menu.create(io, ask_aim_menu, answer_aim_menu, "Выберите:", variants=[
        [
            ('Внести вес сегодня', 'enter_today_weight'), ('Назад', 'back')
        ],
        [
            (f'Изменить старт ({weight_format(weight_start)} кг)', 'change_start_weight'),
            (f'Внести вес сегодня ({weight_format(weight_aim)} кг)', 'change_aim_weight')
        ],
    ])


aim_percent_entry = ask_aim_menu
