from msg_io import Input, sentence, Menu


@sentence
async def yes_no_decide(inp: Input):
    return main_menu, f'you have chosen <b>{inp.param}</b>'

@sentence
async def main_menu(_):
    return Menu('yesno1', 'yes or no?',variants=['yes', 'no', 'hz'], success_state=yes_no_decide)
