from sqlalchemy import select, update, delete, func, and_

from kts_backend.base.base_accessor import BaseAccessor
from kts_backend.quiz.models import (
    Question,
    QuestionModel,
    Player,
    Game,
    GameModel,
    Link,
    PlayerModel, PrizeModel, Prize,
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

    async def get_random_question(self) -> Question:
        async with self.app.database.session() as session:
            query = select(QuestionModel).order_by(func.random())
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

    async def create_game(self, chat_id: int, question_id: int) -> Game:
        async with self.app.database.session() as session:
            game = GameModel(
                chat_id=chat_id, question_id=question_id
            )
            session.add(game)
            await session.commit()
            await session.refresh(game)

            return game.convert_to_dataclass()

    async def get_game_by_id(self, game_id: int) -> Game:
        async with self.app.database.session() as session:
            query = select(GameModel).where(GameModel.id == game_id)
            result = await session.execute(query)
            game = result.scalars().first()
            if game:
                return game.convert_to_dataclass()

    async def get_active_game_by_chat_id(self, chat_id: int) -> Game:
        async with self.app.database.session() as session:
            query = select(GameModel).where(
                and_(GameModel.chat_id == chat_id, GameModel.is_active == True)
            )
            result = await session.execute(query)
            game = result.scalars().first()
            if game:
                return game.convert_to_dataclass()

    async def stop_game(self, game_id: int) -> None:
        async with self.app.database.session() as session:
            query = (
                update(GameModel)
                .where(GameModel.id == game_id)
                .values(is_active=False)
            )
            await session.execute(query)
            await session.commit()

    async def get_game_stats(self) -> list[Game]:
        async with self.app.database.session() as session:
            query = (
                select(GameModel).order_by(GameModel.created_at.desc()).limit(5)
            )
            result = await session.execute(query)
            raw_games = result.scalars().all()
            games = []
            for game in raw_games:
                games.append(game.convert_to_dataclass())
            return games

    async def next_move(self, game_id: int, move: int):
        async with self.app.database.session() as session:
            query = (
                update(GameModel).where(GameModel.id == game_id).values(move=move+1)
            )
            await session.execute(query)
            await session.commit()

    async def is_whole_word_state(self, game_id: int, state: bool):
        async with self.app.database.session() as session:
            query = (
                update(GameModel).where(GameModel.id == game_id).values(is_whole_word=state)
            )
            await session.execute(query)
            await session.commit()

    async def add_player(
        self,
        player_id: int,
        player_username: str,
        player_firstname: str,
        player_secondname: str = None,
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

            return player.convert_to_dataclass()

    async def add_player_game_link(self, game_id: int, player_id: int) -> None:
        async with self.app.database.session() as session:
            link = Link(game_id=game_id, player_id=player_id)
            session.add(link)
            await session.commit()
            await session.refresh(link)

    async def remove_player_game_link(
        self, game_id: int, player_id: int
    ) -> None:
        async with self.app.database.session() as session:
            query = delete(Link).where(
                and_(Link.game_id == game_id, Link.player_id == player_id)
            )
            await session.execute(query)
            await session.commit()

    async def is_player_added(self, game_id: int, player_id: int) -> bool:
        async with self.app.database.session() as session:
            query = select(Link).where(
                and_(Link.player_id == player_id, Link.game_id == game_id)
            )
            result = await session.execute(query)
            link = result.scalars().first()
            return True if link else False

    async def get_player(self, tg_id: int) -> Player:
        async with self.app.database.session() as session:
            query = select(PlayerModel).where(PlayerModel.tg_id == tg_id)
            result = await session.execute(query)
            player = result.scalars().first()
            if player:
                return player.convert_to_dataclass()

    async def get_player_amount(self, game_id: int) -> int:
        async with self.app.database.session() as session:
            query = select(func.count(Link.game_id)).where(
                Link.game_id == game_id
            )
            result = await session.execute(query)
            count = result.scalars().first()
            return count

    async def add_pinned_message_id(self, game_id: int, message_id: int) -> None:
        async with self.app.database.session() as session:
            query = (
                update(GameModel).where(GameModel.id == game_id).values(pinned_message_id=message_id)
            )
            await session.execute(query)
            await session.commit()

    async def add_letter(self, game_id: int, letters_array: list[str]) -> None:
        async with self.app.database.session() as session:
            query = (
                update(GameModel).where(GameModel.id == game_id).values(played_letters=letters_array)
            )
            await session.execute(query)
            await session.commit()

    async def add_winner(self, game_id: int, user_id: int) -> None:
        async with self.app.database.session() as session:
            query = (
                update(GameModel).where(GameModel.id == game_id).values(winner=user_id)
            )
            await session.execute(query)
            await session.commit()

    async def get_random_prize(self) -> Prize:
        async with self.app.database.session() as session:
            query = select(PrizeModel).order_by(func.random())
            result = await session.execute(query)
            prize = result.scalars().first()
            if prize:
                return prize.convert_to_dataclass()