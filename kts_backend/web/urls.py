from aiohttp.web_app import Application
from aiohttp_cors import CorsConfig

__all__ = ("register_urls",)


def register_urls(application: Application, cors: CorsConfig):
    import kts_backend.game.urls

    kts_backend.users.urls.register_urls(application, cors)
