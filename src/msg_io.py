from dataclasses import dataclass, field
from models.profile import Profile
from aiogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from typing import Union
import logging


NEW_LINE = '\n'

START_COMMAND = '/start'


def fname(f):
    return f.__name__ if callable(f) else str(f)


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

    def set(self, name, value):
        self.state[name] = value
        return self


def normalize_variants(variants: list):
    is_list = lambda it: isinstance(it, list)
    two_level = all(map(is_list, variants))
    if not two_level:
        variants = [variants]

    variants_with_keys = []
    for row in variants:
        row_with_keys = []
        for col in row:
            if isinstance(col, list) or isinstance(col, tuple):
                row_with_keys.append(col)
            else:
                row_with_keys.append([col, col])
        variants_with_keys.append(row_with_keys)

    return variants_with_keys


def make_keyboard_and_mapping(variants: list, **kwargs):
    if not variants:
        return ReplyKeyboardRemove(), {}
    else:
        keyboard = []
        mapping = {}
        for row in variants:
            kb_row = []
            for elem in row:
                caption, value = elem
                mapping[caption] = value
                kb_row.append(KeyboardButton(caption))
            keyboard.append(kb_row)

        return ReplyKeyboardMarkup(keyboard=keyboard, **kwargs), mapping


class Menu:
    KEY = '_menu'

    INVALID_ANSWER_MESSAGE = "<pre>Неизвестная опция меню!</pre>"

    @staticmethod
    def create(dlgio: DialogIO, question_func, answer_func, prompt, variants):
        variants = normalize_variants(variants)

        dlgio.state[Menu.KEY] = {
            'variants': variants,
            'question_func': fname(question_func),
        }

        keyboard, _ = make_keyboard_and_mapping(variants, row_width=1)
        return dlgio.next(answer_func).reply(prompt, keyboard)

    @staticmethod
    def value(dlgio: DialogIO):
        try:
            menu_state = dlgio.state[Menu.KEY]
            variants = menu_state['variants']
            question_func = menu_state['question_func']

            keyboard, mapping = make_keyboard_and_mapping(variants)

            if dlgio.text in mapping:
                dlgio.menu_result = mapping[dlgio.text]
                del dlgio.state[Menu.KEY]
                return dlgio.menu_result
            else:
                # invalid answer:
                dlgio.next(question_func).reply(Menu.INVALID_ANSWER_MESSAGE, keyboard)

        except (KeyError, ValueError) as e:
            # if any access error -> fall back to intial_State
            logging.error('Menu.value error', e)
            dlgio.next(None)


def get_message_handlers(my_globals: dict):
    return {name: func for name, func in my_globals.items() if is_sentence(func)}
