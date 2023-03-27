from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, ForeignKey, Integer, DateTime, VARCHAR, ARRAY
from sqlalchemy.orm import relationship

from kts_backend.store.database.sqlalchemy_base import db


@dataclass
class Game:
    id: int
    created_at: datetime
    chat_id: int
    question_id: int
    players: Optional[list["Player"]] = None
    mask: Optional[str] = None
    winner: Optional[int] = None


@dataclass
class Player:
    tg_id: int
    username: str
    first_name: str
    second_name: Optional[str] = None


@dataclass
class Question:
    id: int
    title: str
    answer: str


class GameModel(db):
    __tablename__ = "games"
    id = Column(Integer, nullable=False, primary_key=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    chat_id = Column(Integer, nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"))
    players = relationship("PlayerModel", secondary="link", lazy="selectin")
    mask = Column(VARCHAR())
    winner = Column(Integer, ForeignKey("players.tg_id"))

    def convert_to_dataclass(self) -> Game:
        return Game(
            id=self.id,
            created_at=self.created_at,
            chat_id=self.chat_id,
            question_id=self.question_id,
            players=[player.convert_to_dataclass() for player in self.players]
            if self.players
            else [],
            mask=self.mask,
            winner=self.winner,
        )


class PlayerModel(db):
    __tablename__ = "players"
    tg_id = Column(Integer, nullable=False, primary_key=True)
    username = Column(VARCHAR, nullable=False)
    first_name = Column(VARCHAR, nullable=False)
    second_name = Column(VARCHAR)
    games = relationship("GameModel", secondary="link")

    def convert_to_dataclass(self) -> Player:
        return Player(
            tg_id=self.tg_id,
            username=self.username,
            first_name=self.first_name,
            second_name=self.second_name,
        )


class QuestionModel(db):
    __tablename__ = "questions"
    id = Column(Integer, nullable=False, primary_key=True)
    title = Column(VARCHAR, nullable=False)
    answer = Column(VARCHAR, nullable=False)

    def convert_to_dataclass(self) -> Question:
        return Question(id=self.id, title=self.title, answer=self.answer)


class Link(db):
    __tablename__ = "link"
    game_id = Column(Integer, ForeignKey("games.id"), primary_key=True)

    player_id = Column(Integer, ForeignKey("players.tg_id"), primary_key=True)
