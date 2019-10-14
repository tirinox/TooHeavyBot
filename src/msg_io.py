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


@dataclass
class Output:
    new_state: object = None
    reply_text: str = None
    keyboard: Union[ReplyKeyboardMarkup, ReplyKeyboardRemove, None] = ReplyKeyboardRemove()
    join_messages: bool = True


B = KeyboardButton
KB = ReplyKeyboardMarkup
KBRemove = ReplyKeyboardRemove


@dataclass
class Menu(Output):
    variants: list = None


def get_message_handlers(my_globals: dict):
    return {name: obj for name, obj in my_globals.items() if is_sentence(obj)}


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
                mapping[value] = caption
                kb_row.append(KeyboardButton(caption))
            keyboard.append(kb_row)

        return ReplyKeyboardMarkup(keyboard=keyboard, **kwargs), mapping
