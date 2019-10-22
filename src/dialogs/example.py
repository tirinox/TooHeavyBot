from chat.msg_io import DialogIO, sentence, require_answer, Menu


@require_answer
async def yes_no_decide(io: DialogIO):
    result = Menu.value(io)
    if result:
        return io.next(main_menu).reply(f"<b>OK: {result}</b>")


@sentence
async def main_menu(io: DialogIO):
    return Menu.create(io, yes_no_decide, prompt="Yes or no?", variants=[('yes', 1), ('no', 0), ('hz', 'ne znayou')])
