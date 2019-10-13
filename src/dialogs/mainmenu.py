from msg_io import Input, require_answer, KB, B, sentence


YES_NO_KB = KB([
    [B('yes'), B('no'), B('hz')]
], one_time_keyboard=True, row_width=1)


@require_answer
async def asked_q(input: Input):
    if input.text == 'yes':
        return main_menu, 'you said yes!'
    elif input.text == 'no':
        return main_menu, 'you said no!'
    else:
        return asked_q, '<b>stupid!</b> yes or no!!!', YES_NO_KB


@sentence
async def main_menu(_):
    return asked_q, f'yes or no?', YES_NO_KB
