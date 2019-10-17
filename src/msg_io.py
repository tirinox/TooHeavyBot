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


"""

        if transition == transition.GOTO:
            logging.info(f'dialog go to {handler_name}; stack is {state[stack_key]}')
        elif transition == transition.BACK:
            try:
                handler_name = state[stack_key].pop()
            except (AttributeError, IndexError):
                logging.error('dialog stack is empty!')
                handler_name = None
            logging.info(f'dialog back to {handler_name}; stack is {state[stack_key]}')
        elif transition == transition.PUSH:
            if stack_key not in state or not isinstance(state[stack_key], list):
                state[stack_key] = [handler_name]
            else:
                state[stack_key].append(handler_name)
            logging.info(f'dialog push {handler_name}; stack is {state[stack_key]}')
        elif transition == transition.IGNORE:
            ...
"""


@dataclass
class DialogIO:
    message: Message
    profile: Profile
    text: str
    state: dict = field(default_factory={})

    out_keyboard: Union[ReplyKeyboardMarkup, ReplyKeyboardRemove, None] = ReplyKeyboardRemove()
    out_text: str = None

    join_messages: bool = True

    def reply(self, text: str, keyboard=None):
        self.out_text = text
        if keyboard:
            self.out_keyboard = keyboard
        return self

    def set(self, name, value):
        self.state[name] = value
        return self

    def next(self, next_func):
        next_func = fname(next_func)
        self.state[CURRENT_FUNCTION_KEY] = next_func

        logging.info(f'dialog next {next_func}; stack is {self.state[STATE_STACK_KEY]}')

        return self

    def reset(self):
        self.state[STATE_STACK_KEY] = []
        self.state[CURRENT_FUNCTION_KEY] = "?"
        return self

    def push(self, next_func):
        next_func = fname(next_func)
        stack = self.state.get(STATE_STACK_KEY, [])
        if not isinstance(stack, list):
            stack = []

        stack.append(self.state[CURRENT_FUNCTION_KEY])
        self.state[STATE_STACK_KEY] = stack
        self.state[CURRENT_FUNCTION_KEY] = next_func

        logging.info(f'dialog push {next_func}; stack is {stack}')

        return self

    def back(self):
        try:
            stack = self.state[STATE_STACK_KEY]
            handler_name = stack.pop()
        except (AttributeError, IndexError):
            logging.error('dialog stack is empty!')
            handler_name = "?"

        self.state[CURRENT_FUNCTION_KEY] = handler_name

        logging.info(f'dialog back to {handler_name}; stack is {stack}')

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
        return dlgio.push(answer_func).reply(prompt, keyboard)

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
    return {fname(func): func for _, func in my_globals.items() if is_sentence(func)}
