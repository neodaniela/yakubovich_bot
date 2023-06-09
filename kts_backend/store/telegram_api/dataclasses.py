from dataclasses import field
from typing import ClassVar, Type, List, Optional

from marshmallow_dataclass import dataclass
from marshmallow import Schema, EXCLUDE


@dataclass
class MessageFrom:
    id: int
    is_bot: bool
    first_name: str
    last_name: Optional[str]
    username: Optional[str]

    class Meta:
        unknown = EXCLUDE


@dataclass
class Chat:
    id: int
    type: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    title: Optional[str] = None

    class Meta:
        unknown = EXCLUDE

@dataclass
class LeftChatMember:
    id: int
    username: str

    class Meta:
        unknown = EXCLUDE


@dataclass
class Message:
    message_id: int
    from_: MessageFrom = field(metadata={"data_key": "from"})
    chat: Chat
    text: Optional[str] = None
    left_chat_member: Optional["LeftChatMember"] = None

    class Meta:
        unknown = EXCLUDE


@dataclass
class Callback:
    id: int
    from_: MessageFrom = field(metadata={"data_key": "from"})
    message: Message
    data: str

    class Meta:
        unknown = EXCLUDE


@dataclass
class NewChatMember:
    user: MessageFrom
    status: str

    class Meta:
        unknown = EXCLUDE


@dataclass
class MyChatMember:
    chat: Chat
    from_: MessageFrom = field(metadata={"data_key": "from"})
    new_chat_member: NewChatMember

    class Meta:
        unknown = EXCLUDE


@dataclass
class UpdateObj:
    update_id: int
    message: Optional[Message] = None
    callback_query: Optional[Callback] = None
    my_chat_member: Optional[MyChatMember] = None

    class Meta:
        unknown = EXCLUDE


@dataclass
class GetUpdatesResponse:
    ok: bool
    result: List[UpdateObj]

    Schema: ClassVar[Type[Schema]] = Schema

    class Meta:
        unknown = EXCLUDE


@dataclass
class SendMessageResponse:
    ok: bool
    result: Message
    Schema: ClassVar[Type[Schema]] = Schema

    class Meta:
        unknown = EXCLUDE
