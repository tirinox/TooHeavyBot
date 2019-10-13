from msg_io import Input, Output, uses_answer, KB, B

YES_NO_KB = KB([
    [B('yes'), B('no'), B('hz')]
], one_time_keyboard=True, row_width=1)


@uses_answer
async def dlg_asked_q(input: Input):
    if input.text == 'yes':
        return dlg_main_menu, 'you said yes!'
    elif input.text == 'no':
        return dlg_main_menu, 'you said no!'
    else:
        return dlg_asked_q, '<b>stupid!</b> yes or no!!!', YES_NO_KB


async def dlg_main_menu(_):
    return dlg_asked_q, f'yes or no?', YES_NO_KB
