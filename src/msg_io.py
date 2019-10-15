from dataclasses import dataclass, field
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


@dataclass
class DialogIO:
    message: Message
    profile: Profile
    text: str
    state: dict = field(default_factory={})

    out_keyboard: Union[ReplyKeyboardMarkup, ReplyKeyboardRemove, None] = ReplyKeyboardRemove()
    out_next_func: object = None
    out_text: str = None
    join_messages: bool = True

    def reply(self, text: str, keyboard=None):
        self.out_text = text
        if keyboard:
            self.out_keyboard = keyboard
        return self

    def next(self, next_func: callable):
        self.out_next_func = next_func
        return self


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


class Menu:
    MENU_MAPPING_KEY = '_menu_map'
    INVALID_ANSWER_MESSAGE = "<pre>wrong answer!</pre>"

    @staticmethod
    def create(input: DialogIO, next_func, prompt, variants):
        keyboard, mapping = make_keyboard_and_mapping(variants)
        input.state[Menu.MENU_MAPPING_KEY] = mapping
        return input.next(next_func).reply(prompt, keyboard)

    @staticmethod
    def value(input: DialogIO):
        key = Menu.MENU_MAPPING_KEY
        if isinstance(input.state, dict) and key in input.state and input.text in input.state[key]:
            value = input.state[key][input.text]
            del input.state[key]
            return value


def get_message_handlers(my_globals: dict):
    return {name: func for name, func in my_globals.items() if is_sentence(func)}
