from dataclasses import dataclass
from models.profile import Profile
from aiogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from typing import Union


NEW_LINE = '\n'
MAIN_HANDLER_KEY = 'main'
START_COMMAND = '/start'


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
