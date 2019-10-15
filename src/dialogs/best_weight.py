from msg_io import *


def best_weight_formula(height, sex):
    if sex == 'male':
        return round((height - 100) * 1.15)
    elif sex == 'female':
        return round((height - 110) * 1.15)


@require_answer
async def answer_height(io: DialogIO):
    try:
        height = int(io.text)
        assert 50 <= height <= 300

        sex = io.state['sex']

        result = best_weight_formula(height, sex)
        io.reply(f'Ваш идеальный вес: {result} кг').next(None)

    except (ValueError, AssertionError):
        io.reply('Должно быть число от 50 до 300!').next(ask_height)


@sentence
async def ask_height(io: DialogIO):
    io.reply('Ваш рост в сантиметрах?').next(answer_height)


@require_answer
async def answer_sex(io: DialogIO):
    sex = Menu.value(io)
    io.set('sex', sex).next(ask_height)


@sentence
async def ask_sex(io: DialogIO):
    Menu.create(io, ask_sex, answer_sex, "Какой ваш пол?", variants=[
        ('Мужской', 'male'), ('Женский', 'female')
    ])


best_weight_entry = ask_sex