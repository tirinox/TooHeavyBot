def say(s, kb=None):
    return 0



def dlg_best_weight_dialog_entry(mgs, context):
    say("Давай расчитаем твой идеальный вес?")
    return dlg_ask_sex


def dlg_ask_sex(context):
    while True:
        say("Ты м или ж?", [
            'М', 'Ж'
        ])

        answer = yield

        if answer in ('М', 'Ж'):
            context.sex = answer
            yield dlg_ask_height
        else:
            say('Неизвестный мне пол!')


def dlg_ask_height(msg, context):
    say("введи свой рост в см")
    return dlg_wait_height


def dlg_wait_height(msg, context):
    try:
        answer = int(msg.text)

    except ValueError:
        say('неправильное число')
        return dlg_ask_height