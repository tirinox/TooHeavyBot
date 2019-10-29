from chat.msg_io import *


def best_weight_formula(height, sex):
    if sex == 'male':
        return round((height - 100) * 1.15)
    elif sex == 'female':
        return round((height - 110) * 1.15)


@sentence
async def ask_height(io: DialogIO):
    lang = io.language
    height = ask_for_number(io, lang.bw_prompt_height, 50, 300,
                            error_msg=lang.bw_prompt_height_err)

    if height == CANCELLED:
        io.back()
    elif height:
        sex = io.state['sex']
        result = best_weight_formula(height, sex)
        io.reply(lang.bw_result(result)).back().clear('sex')


@sentence
async def ask_sex(io: DialogIO):
    lang = io.language
    result = create_menu(io, lang.bw_prompt_sex, variants=[
        [
            (lang.bw_male, 'male'),
            (lang.bw_female, 'female')
        ],
        [(lang.skip, CANCELLED)]
    ])
    if result is not None:
        if result == CANCELLED:
            io.back()
        else:
            io.set('sex', result).next(ask_height)


best_weight_entry = ask_sex
