from dataclasses import dataclass
from models.profile import Profile
from aiogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from typing import Union


NEW_LINE = '\n'

START_COMMAND = '/start'


def fname(f):
    return f.__name__


def require_answer(f):
    f = sentence(f)
    f.this_requires_answer = True
    return f


def sentence(f):
    f.this_is_dialog_sentence = True
    return f


def does_require_answer(o):
    return hasattr(o, 'this_requires_answer')


def is_sentence(o):
    return hasattr(o, 'this_is_dialog_sentence')


def register_global(name, value):
    globals()[name] = value


@dataclass
class Input:
    message: Message
    profile: Profile
    text: str
    param: object = None


@dataclass
class Output:
    new_state: object = None
    reply_text: str = None
    keyboard: Union[ReplyKeyboardMarkup, ReplyKeyboardRemove, None] = ReplyKeyboardRemove()
    join_messages: bool = True
    param: object = None


B = KeyboardButton
KB = ReplyKeyboardMarkup
KBRemove = ReplyKeyboardRemove


def make_keyboard_and_mapping(variants: list, **kwargs):
    if not variants:
        return ReplyKeyboardRemove(), {}
    else:
        is_list = lambda it: isinstance(it, list)
        two_level = all(map(is_list, variants))
        if not two_level:
            variants = [variants]

        keyboard = []
        mapping = {}
        for row in variants:
            kb_row = []
            for elem in row:
                if isinstance(elem, tuple):
                    caption, value = elem
                else:
                    caption = value = elem
                mapping[caption] = value
                kb_row.append(KeyboardButton(caption))
            keyboard.append(kb_row)

        return ReplyKeyboardMarkup(keyboard=keyboard, **kwargs), mapping


class Menu(Output):
    INVALID_ANSWER_MESSAGE = "<pre>wrong answer!</pre>"

    def __init__(self, unique_name, prompt, variants, success_state, **kwargs):
        self.prompt = prompt
        self.keyboard, self.mapper = make_keyboard_and_mapping(variants, **kwargs)
        self.success_state = success_state

        @sentence
        async def asker(_):
            return Output(answerer, prompt, self.keyboard, **kwargs)

        asker.__name__ = unique_name + '_in'

        @require_answer
        async def answerer(input: Input):
            text = input.text
            if text in self.mapper:
                return Output(success_state, param=self.mapper[text])
            else:
                return Output(asker, self.INVALID_ANSWER_MESSAGE)

        answerer.__name__ = unique_name + '_out'
        self.new_state = asker

