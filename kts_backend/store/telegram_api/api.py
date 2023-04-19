import aiohttp
from typing import Optional
from kts_backend.store.telegram_api.dataclasses import (
    GetUpdatesResponse,
    SendMessageResponse,
)


class TgClient:
    def __init__(self, token: str = ""):
        self.token = token

    def get_url(self, method: str):
        return f"https://api.telegram.org/bot{self.token}/{method}"

    async def get_updates(
        self, offset: Optional[int] = None, timeout: int = 0
    ) -> dict:
        url = self.get_url("getUpdates")
        params = {}
        if offset:
            params["offset"] = offset
        if timeout:
            params["timeout"] = timeout
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                a = await resp.json()
                return a

    async def get_updates_in_objects(
        self, offset: Optional[int] = None, timeout: int = 0
    ) -> GetUpdatesResponse:
        res_dict = await self.get_updates(offset=offset, timeout=timeout)
        return GetUpdatesResponse.Schema().load(res_dict)

    async def send_message(
        self, chat_id: int, text: str, reply_markup=None
    ) -> SendMessageResponse:
        url = self.get_url("sendMessage")
        payload = {"chat_id": chat_id, "text": text}
        if reply_markup:
            payload["reply_markup"] = reply_markup.to_json()

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                res_dict = await resp.json()
                return SendMessageResponse.Schema().load(res_dict)

    async def delete_message(
        self, chat_id: int, message_id: int) -> None:
        url = self.get_url("deleteMessage")
        payload = {"chat_id": chat_id, "message_id": message_id}

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                res_dict = await resp.json()

    async def edit_message_text(
        self, chat_id: int, message_id: int, text: str, reply_markup=None
    ) -> SendMessageResponse:
        url = self.get_url("editMessageText")
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup.to_json()

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                res_dict = await resp.json()
                return SendMessageResponse.Schema().load(res_dict)

    async def pin_chat_message(self, chat_id: int, message_id: int) -> None:
        url = self.get_url("pinChatMessage")
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
        }
        async with aiohttp.ClientSession() as session:
            await session.post(url, json=payload)

    async def unpin_all_chat_messages(self, chat_id: int) -> None:
        url = self.get_url("unpinAllChatMessages")
        payload = {
            "chat_id": chat_id,
        }
        async with aiohttp.ClientSession() as session:
            await session.post(url, json=payload)

    async def send_photo(self, chat_id: int, photo: str) -> SendMessageResponse:
        url = self.get_url("sendPhoto")
        payload = {"chat_id": chat_id, "photo": photo}

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                res_dict = await resp.json()
                return SendMessageResponse.Schema().load(res_dict)

    async def send_sticker(
        self, chat_id: int, sticker: str
    ) -> SendMessageResponse:
        url = self.get_url("sendSticker")
        payload = {"chat_id": chat_id, "sticker": sticker}

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                res_dict = await resp.json()
                return SendMessageResponse.Schema().load(res_dict)
