from dataclasses import dataclass
from models.profile import Profile
from aiogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
from typing import Union


NEW_LINE = '\n'


def uses_answer(f):
    f.uses_answer = True
    return f


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
