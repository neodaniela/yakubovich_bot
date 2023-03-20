import typing


from kts_backend.store.database.database import Database

if typing.TYPE_CHECKING:
    from kts_backend.web.app import Application


class Store:
    def __init__(self, app: "Application", *args, **kwargs):
        from kts_backend.game.accessor import GameAccessor
        from kts_backend.store.bot.manager import BotManager

        self.game = GameAccessor(app)
        self.bot = BotManager(app)


def setup_store(app: "Application"):
    app.database = Database(app)
    app.on_startup.append(app.database.connect)
    app.on_cleanup.append(app.database.disconnect)
    app.store = Store(app)
