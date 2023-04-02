import asyncio
import typing
from asyncio import Task
from typing import Optional
from kts_backend.store.telegram_api.api import TgClient

if typing.TYPE_CHECKING:
    from kts_backend.web.app import Application


class Poller:
    def __init__(self, token: str, app: "Application"):
        self.tg_client = TgClient(token)
        self._task: Optional[Task] = None
        self.app = app

    async def _worker(self):
        offset = 0
        while True:
            res = await self.tg_client.get_updates_in_objects(
                offset=offset, timeout=30
            )
            for u in res.result:
                offset = u.update_id + 1
                await self.app.store.bot.handle_update(u)

    async def start(self):
        self._task = asyncio.create_task(self._worker())

    async def stop(self):
        self._task.cancel()
