def say(s, kb=None):
    return 0



def best_weight_dialog_entry(mgs, context):
    say("Давай расчитаем твой идеальный вес?")
    return ask_sex


def ask_sex(context):
    while True:
        say("Ты м или ж?", [
            'М', 'Ж'
        ])

        answer = yield

        if answer in ('М', 'Ж'):
            context.sex = answer
            yield ask_height
        else:
            say('Неизвестный мне пол!')


def ask_height(msg, context):
    say("введи свой рост в см")
    return wait_height


def wait_height(msg, context):
    try:
        answer = int(msg.text)

    except ValueError:
        say('неправильное число')
        return ask_height