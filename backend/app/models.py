from sqlalchemy import Column, Integer, String, Float, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

game_mechanics = Table(
    'game_mechanics', Base.metadata,
    Column('game_id', Integer, ForeignKey('games.id')),
    Column('mechanic', String)
)

game_genres = Table(
    'game_genres', Base.metadata,
    Column('game_id', Integer, ForeignKey('games.id')),
    Column('genre', String)
)

class BoardGame(Base):
    __tablename__ = 'games'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    designer = Column(String)
    player_count = Column(String)
    play_time = Column(String)
    image_url = Column(String)
    mechanics = relationship("Mechanic", back_populates="game")
    genres = relationship("Genre", back_populates="game")

class Mechanic(Base):
    __tablename__ = 'mechanics'
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('games.id'))
    name = Column(String)
    game = relationship("BoardGame", back_populates="mechanics")

class Genre(Base):
    __tablename__ = 'genres'
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('games.id'))
    name = Column(String)
    game = relationship("BoardGame", back_populates="genres")

class UserRating(Base):
    __tablename__ = 'ratings'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    game_id = Column(Integer, ForeignKey('games.id'))
    rating = Column(Float)