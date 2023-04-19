from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    BigInteger,
    DateTime,
    VARCHAR,
    Boolean,
    ARRAY,
    String
)
from sqlalchemy.orm import relationship

from kts_backend.store.database.sqlalchemy_base import db


@dataclass
class Game:
    id: int
    created_at: datetime
    chat_id: int
    is_active: bool
    question_id: int
    is_whole_word: bool
    pinned_message_id: int
    played_letters: list[str]
    move: Optional[int] = None
    players: Optional[list["Player"]] = None
    winner: Optional[int] = None


@dataclass
class Player:
    tg_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    second_name: Optional[str] = None


@dataclass
class Question:
    id: int
    title: str
    answer: str


@dataclass
class Prize:
    id: int
    title: str
    img: str


class GameModel(db):
    __tablename__ = "games"
    id = Column(Integer, nullable=False, primary_key=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    chat_id = Column(BigInteger, nullable=False)
    is_active = Column(Boolean, default=True)
    question_id = Column(Integer, ForeignKey("questions.id"))
    is_whole_word = Column(Boolean)
    pinned_message_id = Column(Integer)
    played_letters = Column(ARRAY(String), default=[])
    move = Column(Integer, default=0)
    players = relationship("PlayerModel", secondary="link", lazy="selectin")
    winner = Column(BigInteger, ForeignKey("players.tg_id"))

    def convert_to_dataclass(self) -> Game:
        return Game(
            id=self.id,
            created_at=self.created_at,
            chat_id=self.chat_id,
            is_active=self.is_active,
            question_id=self.question_id,
            is_whole_word=self.is_whole_word,
            pinned_message_id=self.pinned_message_id,
            played_letters=self.played_letters,
            move=self.move,
            players=[player.convert_to_dataclass() for player in self.players]
            if self.players
            else [],
            winner=self.winner,
        )


class PlayerModel(db):
    __tablename__ = "players"
    tg_id = Column(BigInteger, nullable=False, primary_key=True)
    username = Column(VARCHAR)
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


class PrizeModel(db):
    __tablename__ = "prizes"
    id = Column(Integer, nullable=False, primary_key=True)
    title = Column(VARCHAR, nullable=False)
    img = Column(VARCHAR, nullable=False)

    def convert_to_dataclass(self) -> Prize:
        return Prize(id=self.id, title=self.title, img=self.img)


class Link(db):
    __tablename__ = "link"
    game_id = Column(Integer, ForeignKey("games.id"), primary_key=True)

    player_id = Column(
        BigInteger, ForeignKey("players.tg_id"), primary_key=True
    )
