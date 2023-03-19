import asyncio
from typing import Optional

from kts_backend.store.tg_api.telegram.api import TelegramClient


class Poller:
    def __init__(self, token: str, queue: asyncio.Queue):
        self.tg_client = TelegramClient(token)
        self.queue = queue
        self._task: Optional[asyncio.Task] = None

    async def _worker(self):
        offset = 0
        while True:
            res = await self.tg_client.get_updates(
                offset=offset, timeout=25
            )
            for u in res["result"]:
                offset = u["update_id"] + 1
                print(u)
                self.queue.put_nowait(u)

    async def start(self):
        self._task = asyncio.create_task(self._worker())

    async def stop(self):
        self._task.cancel()
