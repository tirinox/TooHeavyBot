import logging
from dataclasses import dataclass, field
from io import BytesIO
from typing import Union
from abc import ABC, abstractmethod
from chat.bot_telegram import TelegramBot

from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, Location, Message

from localization import *
from models.profile import Profile


NEW_LINE = '\n'

CURRENT_FUNCTION_KEY = '__func_state'
STATE_STACK_KEY = '__stack'

DIALOG_PREFIX = 'dialogs.'

CANCELLED = 'CANCELLED'


def fname(f):
    name = f.__module__ + '.' + f.__qualname__ if callable(f) else str(f)
    if name.startswith(DIALOG_PREFIX):
        name = name[len(DIALOG_PREFIX):]
    return name


def sentence(f):
    f.this_is_dialog_sentence = True
    return f


def is_sentence(o):
    return hasattr(o, 'this_is_dialog_sentence')


def get_message_handlers(my_globals: dict):
    return {fname(func): func for _, func in my_globals.items() if is_sentence(func)}



class AbstractMessageSender(ABC):
    def __init__(self):
        ...

    @abstractmethod
    async def send_photo(self, to_uid, photo, caption=None, disable_notification=False):
        ...

    @abstractmethod
    async def send_text(self, to_uid, text, reply_markup=None, disable_notification=False):
        ...


@dataclass
class DialogIO:
    profile: Profile
    text: str
    state: dict = field(default_factory={})
    location: Location = None

    out_keyboard: Union[ReplyKeyboardMarkup, ReplyKeyboardRemove, None] = ReplyKeyboardRemove()
    out_text: str = None
    out_image: BytesIO = None
    out_image_caption: str = None
    new_message: bool = True

    username: str = None
    sender: AbstractMessageSender = None

    _lang: Union[languages] = None

    ASKED = '__asked'

    @staticmethod
    async def load(profile: Profile, text='', location=None, sender: AbstractMessageSender=None):
        dialog_state = await profile.dialog_state()
        io_obj = DialogIO(profile, text, dialog_state)
        io_obj.location = location
        io_obj.language = await profile.get_language()
        io_obj.sender = sender
        return io_obj

    @property
    def language(self) -> LangEnglish:
        return self._lang

    @language.setter
    def language(self, lang):
        self._lang = get_localization(lang)

    async def change_language(self, code):
        await self.profile.set_language(code)
        self.language = code

    def reply(self, text: str, keyboard=None):
        self.out_text = text
        if keyboard:
            if type(keyboard) is list:
                variants = normalize_variants(keyboard)
                keyboard, _ = make_keyboard_and_mapping(variants, row_width=1)
            self.out_keyboard = keyboard
        return self

    def send_image(self, img: BytesIO, caption=None):
        self.out_image = img
        self.out_image_caption = caption
        return self

    def add(self, text: str):
        self.out_text = text if self.out_text is None else self.out_text + text
        return self

    def nl(self):
        return self.add('\n')

    def set(self, name, value):
        self.state[name] = value
        return self

    def clear(self, *keys):
        for k in keys:
            self.state.pop(k, None)

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

    def back(self, text=None):
        try:
            if text is not None:
                self.reply(text)

            stack = self.state[STATE_STACK_KEY]
            handler_name = stack.pop()
            logging.info(f'dialog back to {handler_name}; stack is {stack}')
            self.reset_asked()
        except (AttributeError, IndexError):
            logging.error('dialog stack is empty!')
            handler_name = "?"

        self.state[CURRENT_FUNCTION_KEY] = handler_name

        return self

    async def save_dialog_state(self):
        await self.profile.set_dialog_state(self.state)


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
                kb_row.append(caption if isinstance(caption, KeyboardButton) else KeyboardButton(str(caption)))
            keyboard.append(kb_row)

        return ReplyKeyboardMarkup(keyboard=keyboard, **kwargs), mapping


def create_menu(io: DialogIO, prompt, variants, error_msg=None):
    variants = normalize_variants(variants)
    keyboard, mapping = make_keyboard_and_mapping(variants, row_width=1)

    if io.asked:
        if io.text in mapping:
            io.reset_asked()
            return mapping[io.text]
        else:
            # invalid answer:
            io.reply(error_msg or io.language.invalid_menu_option, keyboard)
    else:
        # no menu installed
        io.ask(prompt, keyboard)
        return None


def ask_for_number(io: DialogIO,
                   prompt,
                   min_value=float('-inf'),
                   max_value=float('+inf'),
                   error_msg=None, with_cancel=True):
    if io.asked:
        if with_cancel and io.text == io.language.cancel:
            io.reset_asked()
            return CANCELLED

        try:
            text = io.text.replace(',', '.').replace(' ', '')
            number = float(text)
            assert min_value <= number <= max_value
            io.reset_asked()
            return number
        except (AssertionError, ValueError):
            io.ask(error_msg or io.language.invalid_number)
    else:
        io.ask(prompt, keyboard=[io.language.cancel] if with_cancel else None)


class AbstractCommandHandler(ABC):
    @abstractmethod
    async def __call__(self, message: Message, io: DialogIO):
        ...
