import asyncio
from typing import List

from kts_backend.store.tg_api.telegram.api import TelegramClient


class Worker:
    def __init__(
        self, token: str, queue: asyncio.Queue, concurrent_workers: int
    ):
        self.tg_client = TelegramClient(token)
        self.queue = queue
        self.concurrent_workers = concurrent_workers
        self._tasks: List[asyncio.Task] = []

    async def handle_update(self, upd):
        if "message" in upd and "text" in upd["message"]:
            await self.tg_client.send_message(upd["message"]["chat"]["id"], upd["message"]["text"])

    async def _worker(self):
        while True:
            try:
                upd = await self.queue.get()
                await self.handle_update(upd)
            finally:
                self.queue.task_done()

    async def start(self):
        self._tasks = [
            asyncio.create_task(self._worker())
            for _ in range(self.concurrent_workers)
        ]

    async def stop(self):
        await self.queue.join()
        for t in self._tasks:
            t.cancel()
