import asyncio

from kts_backend.store.bot.poller import Poller
from kts_backend.store.bot.worker import Worker


class Bot:
    def __init__(self, token: str, concurrent_workers: int):
        self.queue = asyncio.Queue()
        self.poller = Poller(token, self.queue)
        self.worker = Worker(token, self.queue, concurrent_workers)

    async def start(self):
        await self.poller.start()
        await self.worker.start()

    async def stop(self):
        await self.poller.stop()
        await self.worker.stop()
