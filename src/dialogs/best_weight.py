from msg_io import *


def best_weight_formula(height, sex):
    if sex == 'male':
        return round((height - 100) * 1.15)
    elif sex == 'female':
        return round((height - 110) * 1.15)


@sentence
async def ask_height(io: DialogIO):
    height = ask_for_number(io, 'Ваш рост в сантиметрах?', 50, 300,
                      error_msg='Должно быть число от 50 до 300!')

    if height:
        sex = io.state['sex']
        result = best_weight_formula(height, sex)
        io.reply(f'Ваш идеальный вес: {result} кг').back()


@sentence
async def ask_sex(io: DialogIO):
    result = create_menu(io, "Какой ваш пол?", variants=[
        ('Мужской', 'male'), ('Женский', 'female')
    ])
    if result:
        io.set('sex', result).next(ask_height)


best_weight_entry = ask_sex