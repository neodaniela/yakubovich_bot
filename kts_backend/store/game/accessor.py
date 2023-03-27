from sqlalchemy import select

from kts_backend.base.base_accessor import BaseAccessor
from kts_backend.quiz.models import (
    Question,
    QuestionModel,
    Player,
    Game,
    GameModel,
    Link,
    PlayerModel,
)


class QuizAccessor(BaseAccessor):
    async def list_questions(self) -> list[Question]:
        async with self.app.database.session() as session:
            query = select(QuestionModel)
            result = await session.execute(query)
            raw_questions = result.scalars().all()
            questions = []
            for theme in raw_questions:
                questions.append(theme.convert_to_dataclass())
            return questions

    async def get_question_by_id(self, question_id: int) -> Question:
        async with self.app.database.session() as session:
            query = select(QuestionModel).where(QuestionModel.id == question_id)
            result = await session.execute(query)
            question = result.scalars().first()
            if question:
                return question.convert_to_dataclass()

    async def create_question(self, title: str, answer: str) -> Question:
        async with self.app.database.session() as session:
            question = QuestionModel(title=title, answer=answer)
            session.add(question)
            await session.commit()
            await session.refresh(question)

            return question.convert_to_dataclass()

    async def create_game(
        self, chat_id: int, question_id: int, creator_id: int
    ) -> Game:
        async with self.app.database.session() as session:
            question = await self.get_question_by_id(question_id)
            answer = question.answer
            mask = "*" * len(answer)
            game = GameModel(
                chat_id=chat_id, question_id=question_id, mask=mask
            )
            session.add(game)
            await session.commit()
            await session.refresh(game)
            link = Link(game_id=game.id, player_id=creator_id)
            session.add(link)
            await session.commit()
            await session.refresh(link)

            return game.convert_to_dataclass()

    async def get_game_by_id(self, game_id: int) -> Question:
        async with self.app.database.session() as session:
            query = select(GameModel).where(GameModel.id == game_id)
            result = await session.execute(query)
            game = result.scalars().first()
            if game:
                return game.convert_to_dataclass()

    async def add_player(
        self,
        game_id: int,
        player_id: int,
        player_username: str,
        player_firstname: str,
        player_secondname: str or None,
    ) -> Player:
        async with self.app.database.session() as session:
            player = PlayerModel(
                tg_id=player_id,
                username=player_username,
                first_name=player_firstname,
                second_name=player_secondname,
            )
            session.add(player)
            await session.commit()
            await session.refresh(player)
            link = Link(game_id=game_id, player_id=player_id)
            session.add(link)
            await session.commit()
            await session.refresh(link)

            return player.convert_to_dataclass()
