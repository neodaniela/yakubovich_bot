import typing


if typing.TYPE_CHECKING:
    from kts_backend.web.app import Application


def setup_routes(app: "Application"):
    from kts_backend.quiz.views import QuestionAddView
    from kts_backend.quiz.views import QuestionListView
    from kts_backend.quiz.views import GameAddView
    from kts_backend.quiz.views import GameGetView
    from kts_backend.quiz.views import PlayerAddView

    app.router.add_view("/questions.add", QuestionAddView)
    app.router.add_view("/questions.list", QuestionListView)
    app.router.add_view("/game.add", GameAddView)
    app.router.add_view("/game.get", GameGetView)
    app.router.add_view("/player.add", PlayerAddView)
