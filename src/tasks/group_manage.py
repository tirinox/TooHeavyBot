from models.group import Group
from models.profile import Profile
from chat.bot_telegram import TelegramBot
import asyncio
from chat.msg_io import AbstractMessageSender


PROFILE_GROUP_KEY = 'group_id'


async def get_group_of_profile(p: Profile):
    return await p.get_prop(PROFILE_GROUP_KEY)


async def make_or_ensure_my_group(p: Profile):
    group_id = await get_group_of_profile(p)
    if group_id is None:
        g = Group.new_group()
    else:
        g = Group(group_id)
    await g.user_join(p.ident)


async def get_invite_link(g: Group, b: TelegramBot):
    bot_username = b.username
    return f'https://t.me/{bot_username}?start=g_inv_{g.ident}'


def send_message_to_group_members(members: set, message, sender: AbstractMessageSender):
    async def send_one(ident):
        await sender.send_text(message, ident)

    asyncio.create_task(asyncio.gather(*(send_one(m) for m in members)))


async def leave_group(p: Profile, g: Group, sender: AbstractMessageSender):
    await g.user_leave(p.ident)
    await p.del_prop(PROFILE_GROUP_KEY)

    tr = await p.get_translator()

    members = await g.get_members()
    if members:
        message = ''  # fixme: message
        send_message_to_group_members(members, message, sender)
    else:
        await g.remove()


async def join_group(p: Profile, g: Group, sender: AbstractMessageSender):
    members = await g.get_members()

    await g.user_join(p.ident)
    await p.set_prop(PROFILE_GROUP_KEY, g.ident)

    tr = await p.get_translator()

    message = ''  # fixme: message (notify other members that someone joined)
    send_message_to_group_members(members, message, sender)
