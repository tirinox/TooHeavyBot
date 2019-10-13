from msg_io import Input, Output, uses_answer
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

YES_NO_KB = ReplyKeyboardMarkup([
    [KeyboardButton('yes'), KeyboardButton('no'), KeyboardButton('hz')]
], one_time_keyboard=True)


@uses_answer
async def dlg_asked_q(input: Input):
    if input.text == 'yes':
        return dlg_main_menu, 'you said yes!'
    elif input.text == 'no':
        return dlg_main_menu, 'you said no!'
    else:
        return dlg_asked_q, 'stupid! yes or no!!!', YES_NO_KB


async def dlg_main_menu(_):
    return dlg_asked_q, f'yes or no?', YES_NO_KB
