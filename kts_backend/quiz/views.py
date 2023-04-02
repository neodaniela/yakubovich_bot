from kts_backend.quiz.schemes import (
    QuestionSchema,
    QuestionListSchema,
    GameSchema,
    GameGetSchema,
    PlayerAddSchema,
    PlayerSchema,
)
from kts_backend.web.app import View
from aiohttp_apispec import (
    docs,
    request_schema,
    response_schema,
    querystring_schema,
)

from kts_backend.web.mixins import AuthRequiredMixin
from kts_backend.web.utils import json_response


class QuestionAddView(AuthRequiredMixin, View):
    @docs(
        tags=["quiz"], summary="Create question", description="Create question"
    )
    @request_schema(QuestionSchema)
    @response_schema(QuestionSchema)
    async def post(self):
        title = self.data["title"]
        answer = self.data["answer"]
        question = await self.store.quizzes.create_question(title, answer)
        return json_response(data=QuestionSchema().dump(question))


class QuestionListView(AuthRequiredMixin, View):
    @docs(
        tags=["quiz"], summary="Question List", description="Get Question list"
    )
    @response_schema(QuestionListSchema)
    async def get(self):
        questions = await self.store.quizzes.list_questions()
        raw_questions = [
            QuestionSchema().dump(question) for question in questions
        ]
        return json_response(data={"questions": raw_questions})


class GameAddView(View):
    @docs(tags=["quiz"], summary="Add game", description="Add game")
    @request_schema(GameSchema)
    @response_schema(GameSchema)
    async def post(self):
        chat_id = self.data["chat_id"]
        question_id = self.data["question_id"]
        creator_id = self.data["creator_id"]
        game = await self.store.quizzes.create_game(
            chat_id, question_id, creator_id
        )
        return json_response(data={"game": GameSchema().dump(game)})


class GameGetView(View):
    @docs(tags=["quiz"], summary="Get game", description="Get game by id")
    @querystring_schema(GameGetSchema)
    @response_schema(GameSchema)
    async def get(self):
        game_id = int(self.request.query.get("game_id"))
        game = await self.store.quizzes.get_game_by_id(game_id)
        return json_response(data={"game": GameSchema().dump(game)})


class PlayerAddView(View):
    @docs(tags=["quiz"], summary="Add player", description="Add player")
    @request_schema(PlayerAddSchema)
    @response_schema(PlayerSchema)
    async def post(self):
        game_id = self.data["game_id"]
        player_id = self.data["player_id"]
        player_username = self.data["player_username"]
        player_firstname = self.data["player_firstname"]
        player_secondname = self.data["player_secondname"]
        player = await self.store.quizzes.add_player(
            game_id,
            player_id,
            player_username,
            player_firstname,
            player_secondname,
        )
        return json_response(data={"player": PlayerSchema().dump(player)})
