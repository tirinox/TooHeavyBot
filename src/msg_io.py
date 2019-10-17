from dataclasses import dataclass, field
from models.profile import Profile
from aiogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from typing import Union
import logging


NEW_LINE = '\n'

START_COMMAND = '/start'

CURRENT_FUNCTION_KEY = '__func_state'
STATE_STACK_KEY = '__stack'

DIALOG_PREFIX = 'dialogs.'


def fname(f):
    name = f.__module__ + '.' + f.__qualname__ if callable(f) else str(f)
    if name.startswith(DIALOG_PREFIX):
        name = name[len(DIALOG_PREFIX):]
    return name


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
    out_text: str = None

    join_messages: bool = True

    ASKED = '__asked'

    def reply(self, text: str, keyboard=None):
        self.out_text = text
        if keyboard:
            self.out_keyboard = keyboard
        return self

    def set(self, name, value):
        self.state[name] = value
        return self

    def ask(self, text: str, keyboard=None):
        self.set(self.ASKED, True)
        return self.reply(text, keyboard)

    @property
    def asked(self):
        return self.state.get(self.ASKED, False)

    def reset_asked(self):
        self.state.pop(self.ASKED, None)
        return self

    def get(self, name):
        return self.state.get(name, None)

    def next(self, next_func):
        next_func = fname(next_func)
        self.state[CURRENT_FUNCTION_KEY] = next_func
        self.reset_asked()

        logging.info(f'dialog next {next_func}; stack is {self.state[STATE_STACK_KEY]}')

        return self

    def reset(self):
        self.reset_asked()
        self.state[STATE_STACK_KEY] = []
        self.state[CURRENT_FUNCTION_KEY] = "?"
        return self

    def push(self, next_func):
        next_func = fname(next_func)
        stack = self.state.get(STATE_STACK_KEY, [])
        if not isinstance(stack, list):
            stack = []

        self.reset_asked()
        stack.append(self.state[CURRENT_FUNCTION_KEY])
        self.state[STATE_STACK_KEY] = stack
        self.state[CURRENT_FUNCTION_KEY] = next_func

        logging.info(f'dialog push {next_func}; stack is {stack}')

        return self

    def back(self):
        try:
            stack = self.state[STATE_STACK_KEY]
            handler_name = stack.pop()
            logging.info(f'dialog back to {handler_name}; stack is {stack}')
            self.reset_asked()
        except (AttributeError, IndexError):
            logging.error('dialog stack is empty!')
            handler_name = "?"

        self.state[CURRENT_FUNCTION_KEY] = handler_name

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


def create_menu(io: DialogIO, prompt, variants):
    INVALID_MENU_OPTION_MESSAGE = "<pre>Неизвестная опция меню!</pre>"

    variants = normalize_variants(variants)
    keyboard, mapping = make_keyboard_and_mapping(variants, row_width=1)

    if io.asked:
        if io.text in mapping:
            io.reset_asked()
            return mapping[io.text]
        else:
            # invalid answer:
            io.reply(INVALID_MENU_OPTION_MESSAGE, keyboard)
    else:
        # no menu installed
        io.ask(prompt, keyboard)
        return False

def get_message_handlers(my_globals: dict):
    return {fname(func): func for _, func in my_globals.items() if is_sentence(func)}
