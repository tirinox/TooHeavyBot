from chat.msg_io import DialogIO, sentence, create_menu


@sentence
async def my_group_menu(io: DialogIO):
    lang = io.language

    result = create_menu(io, lang.myg_title,
                         variants=[
                             [(lang.back, 'back')]
                         ])
    if result == 'back':
        io.back()
