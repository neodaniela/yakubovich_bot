import asyncio
from asyncio import Task
from typing import Optional
from kts_backend.store.telegram_api.api import TgClient


class Poller:
    def __init__(self, token: str):
        self.tg_client = TgClient(token)
        self._task: Optional[Task] = None

    async def _worker(self):
        offset = 0
        while True:
            res = await self.tg_client.get_updates_in_objects(
                offset=offset, timeout=30
            )
            for u in res.result:
                offset = u.update_id + 1
                await self.tg_client.send_message(
                    u.message.chat.id, u.message.text
                )

    async def start(self):
        self._task = asyncio.create_task(self._worker())

    async def stop(self):
        self._task.cancel()
