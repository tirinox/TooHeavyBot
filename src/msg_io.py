from dataclasses import dataclass
from models.profile import Profile
from aiogram.types import Message


@dataclass
class Input:
    message: Message
    profile: Profile
    text: str


@dataclass
class Output:
    new_state: object = None
    reply_text: str = None
    keyboard: list = None
