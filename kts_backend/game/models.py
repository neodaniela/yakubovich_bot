from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer, DateTime, VARCHAR
from sqlalchemy.orm import relationship

from kts_backend.store.database.sqlalchemy_base import db


@dataclass
class GameDC:
    id: int
    created_at: datetime
    chat_id: int
    players: list["PlayerDC"]


@dataclass
class PlayerDC:
    tg_id: int
    username: str
    score: "GameScoreDC"


@dataclass
class GameScoreDC:
    points: int


class GameModel(db):
    __tablename__ = "games"
    id = Column(Integer, nullable=False, primary_key=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    chat_id = Column(Integer, nullable=False)
    players = relationship("PlayerModel", backref="players")

    def convert_to_dataclass(self) -> GameDC:
        return GameDC(
            id=self.id,
            created_at=self.created_at,
            chat_id=self.chat_id,
            players=[player.convert_to_dataclass() for player in self.players] if self.players else []
        )


class PlayerModel(db):
    __tablename__ = "players"
    tg_id = Column(Integer, nullable=False, primary_key=True)
    username = Column(VARCHAR, nullable=False)

    score = relationship(
        "GameScoreModel",
        backref="score",
    )

    def convert_to_dataclass(self) -> PlayerDC:
        return PlayerDC(
            tg_id=self.tg_id,
            username=self.username,
            score=self.score
        )


class GameScoreModel(db):
    __tablename__ = "score"
    id = Column(Integer, nullable=False, primary_key=True)
    points = Column(Integer, nullable=False, default=0)
    game_id = Column(Integer, ForeignKey("games.id", ondelete='CASCADE'), nullable=False)
    player_id = Column(Integer, ForeignKey("players.tg_id", ondelete='CASCADE'), nullable=False)

    def convert_to_dataclass(self) -> GameScoreDC:
        return GameScoreDC(
            points=self.points
        )
