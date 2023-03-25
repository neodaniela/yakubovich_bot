from kts_backend.base.base_accessor import BaseAccessor
from sqlalchemy import select, insert
from kts_backend.game.models import (
    GameModel,
    GameScoreModel,
    PlayerModel,
    PlayerDC,
)
from sqlalchemy.orm import joinedload


class GameAccessor(BaseAccessor):
    async def get_last_game(self) -> dict or None:
        async with self.app.database.session() as session:
            query = select(GameModel).order_by(GameModel.created_at.desc())
            game = await session.execute(query)
            game = game.scalars().first()
            if game:
                player_query = select(GameScoreModel).where(
                    GameScoreModel.game_id == game.id
                )
                players = await session.execute(player_query)
                players = (
                    [p.convert_to_dict() for p in players.scalars()]
                    if players
                    else []
                )
                data = game.convert_to_dict()
                data["players"] = players
                return data

    async def get_player_by_tg_id(self, tg_id) -> PlayerModel or None:
        async with self.app.database.session() as session:
            query = select(PlayerModel).where(PlayerModel.tg_id == tg_id)
            player = await session.execute(query)
            player = player.scalars().first()
            return player if player else None

    async def create_game(self, chat_id: int, players: list[PlayerDC]) -> dict:
        game = GameModel(chat_id=chat_id)
        async with self.app.database.session() as session:
            session.add(game)
            await session.commit()
            await session.refresh(game)
        for item in players:
            player = await self.get_player_by_tg_id(item.tg_id)
            if not player:
                player = await self.create_player(item)
            game_score = GameScoreModel(player_id=player.id, game_id=game.id)
            session.add(game_score)
            await session.commit()
        players = await self.get_players_by_game_id(game.id)
        game = game.convert_to_dict()
        game["players"] = players
        return game

    async def get_players_by_game_id(self, game_id: int) -> list:
        async with self.app.database.session() as session:
            query = (
                select(GameScoreModel)
                .where(GameScoreModel.game_id == game_id)
                .options(joinedload(GameScoreModel.player))
            )
            players = await session.execute(query)
        players = (
            [p.convert_to_dict() for p in players.scalars()] if players else []
        )
        return players

    async def create_player(self, data: PlayerDC) -> PlayerModel:
        async with self.app.database.session() as session:
            player = PlayerModel(tg_id=data.tg_id, username=data.username)
            session.add(player)
            await session.commit()
            await session.refresh(player)
        return player
