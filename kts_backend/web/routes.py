from aiohttp.web_app import Application


def setup_routes(app: Application):
    from kts_backend.game.routes import setup_routes as game_setup_routes

    game_setup_routes(app)
