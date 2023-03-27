import typing
from kts_backend.base.base_accessor import BaseAccessor
from kts_backend.store.bot.poller import Poller

if typing.TYPE_CHECKING:
    from kts_backend.web.app import Application


class BotManager(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.token = self.app.config.bot.token
        self.poller = Poller(self.token)

    async def start(self):
        await self.poller.start()
        self.logger.info("Bot start")

    async def stop(self):
        await self.poller.stop()

    async def connect(self, app: "Application"):
        await self.start()

    async def disconnect(self, app: "Application"):
        await self.stop()
