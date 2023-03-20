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


@dataclass
class PlayerDC:
    tg_id: int
    username: str


@dataclass
class GameScoreDC:
    points: int


class GameModel(db):
    __tablename__ = "games"
    id = Column(Integer, nullable=False, primary_key=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    chat_id = Column(Integer, nullable=False)

    def convert_to_dict(self) -> dict:
        return {
            "id": self.id,
            "created_at": str(self.created_at),
            "chat_id": self.chat_id,
        }

    def convert_to_dataclass(self) -> GameDC:
        return GameDC(
            id=self.id,
            created_at=self.created_at,
            chat_id=self.chat_id,
        )


class PlayerModel(db):
    __tablename__ = "players"
    id = Column(Integer, nullable=False, primary_key=True)
    tg_id = Column(Integer, nullable=False)
    username = Column(VARCHAR, nullable=False)

    def convert_to_dict(self) -> dict:
        return {
            "id": self.id,
            "tg_id": self.tg_id,
            "username": self.username,
        }

    def convert_to_dataclass(self) -> PlayerDC:
        return PlayerDC(
            tg_id=self.tg_id,
            username=self.username,
        )


class GameScoreModel(db):
    __tablename__ = "score"
    id = Column(Integer, nullable=False, primary_key=True)
    points = Column(Integer, nullable=False, default=0)
    game_id = Column(Integer, ForeignKey("games.id", ondelete="CASCADE"))
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"))
    player = relationship(
        "PlayerModel",
        backref="player",
        cascade="all, save-update",
        lazy="selectin",
    )

    def convert_to_dataclass(self) -> GameScoreDC:
        return GameScoreDC(points=self.points)

    def convert_to_dict(self) -> dict:
        return {
            "id": self.id,
            "points": self.points,
            "player": {
                "id": self.player.id,
                "tg_id": self.player.tg_id,
                "username": self.player.username,
            },
        }
