from aiogram.types import Message
from aiogram.types.chat_member_updated import ChatMemberUpdated


def is_group_chat(message: Message) -> bool:
    """
    return true if message was send in group chat
    """
    return message.from_user.id != message.chat.id


def is_private_chat(message: Message) -> bool:
    """
    return true if message was send in private chat
    """
    return not is_group_chat(message)


def is_new_channel_member(member: ChatMemberUpdated) -> bool:
    """
    return true if new person joined to channel
    """
    return (
            member.chat.type == "channel" and
            member.old_chat_member.status in ['left', 'kicked'] and
            member.new_chat_member.status in ['administrator', 'member']
    )
