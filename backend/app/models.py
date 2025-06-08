from sqlalchemy import Column, Integer, String, Float, Table, ForeignKey, JSON, DateTime, Boolean
from sqlalchemy.orm import relationship
from .database import Base

class BoardGame(Base):
    __tablename__ = 'games'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    thumbnail = Column(String)
    image = Column(String)
    min_players = Column(Integer)
    max_players = Column(Integer)
    playing_time = Column(Integer)
    min_playtime = Column(Integer)
    max_playtime = Column(Integer)
    min_age = Column(Integer)
    year_published = Column(Integer)
    
    # Statistics
    average = Column(Float)  # average_rating
    num_ratings = Column(Integer)  # num_ratings
    num_comments = Column(Integer)  # num_comments
    num_weights = Column(Integer)  # num_weights
    average_weight = Column(Float)  # average_weight
    stddev = Column(Float)
    median = Column(Float)
    owned = Column(Integer)
    trading = Column(Integer)
    wanting = Column(Integer)
    wishing = Column(Integer)
    bayes_average = Column(Float)  # bayes_average
    users_rated = Column(Integer)  # number of users who rated the game
    is_expansion = Column(Boolean)
    
    # Rankings
    rank = Column(Integer)
    abstracts_rank = Column(Integer)
    cgs_rank = Column(Integer)
    childrens_games_rank = Column(Integer)
    family_games_rank = Column(Integer)
    party_games_rank = Column(Integer)
    strategy_games_rank = Column(Integer)
    thematic_rank = Column(Integer)
    wargames_rank = Column(Integer)
    
    # Relationships - all lazy loaded by default
    mechanics = relationship("Mechanic", back_populates="game", lazy="select")
    categories = relationship("Category", back_populates="game", lazy="select")
    designers = relationship("Designer", back_populates="game", lazy="select")
    artists = relationship("Artist", back_populates="game", lazy="select")
    publishers = relationship("Publisher", back_populates="game", lazy="select")
    suggested_players = relationship("SuggestedPlayer", back_populates="game", lazy="select")
    language_dependence = relationship("LanguageDependence", back_populates="game", uselist=False, lazy="select")
    integrations = relationship("Integration", back_populates="game", lazy="select")
    implementations = relationship("Implementation", back_populates="game", lazy="select")
    compilations = relationship("Compilation", back_populates="game", lazy="select")
    expansions = relationship("Expansion", back_populates="game", lazy="select")
    families = relationship("Family", back_populates="game", lazy="select")
    versions = relationship("Version", back_populates="game", lazy="select")

class Mechanic(Base):
    __tablename__ = 'mechanics'
    
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('games.id'))
    boardgamemechanic_id = Column(Integer)
    boardgamemechanic_name = Column(String)
    game = relationship("BoardGame", back_populates="mechanics")

class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('games.id'))
    boardgamecategory_id = Column(Integer)
    boardgamecategory_name = Column(String)
    game = relationship("BoardGame", back_populates="categories")

class Designer(Base):
    __tablename__ = 'designers'
    
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('games.id'))
    boardgamedesigner_id = Column(Integer)
    boardgamedesigner_name = Column(String)
    game = relationship("BoardGame", back_populates="designers")

class Artist(Base):
    __tablename__ = 'artists'
    
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('games.id'))
    boardgameartist_id = Column(Integer)
    boardgameartist_name = Column(String)
    game = relationship("BoardGame", back_populates="artists")

class Publisher(Base):
    __tablename__ = 'publishers'
    
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('games.id'))
    boardgamepublisher_id = Column(Integer)
    boardgamepublisher_name = Column(String)
    game = relationship("BoardGame", back_populates="publishers")

class SuggestedPlayer(Base):
    __tablename__ = 'suggested_players'
    
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('games.id'))
    player_count = Column(Integer)
    best = Column(Integer)
    recommended = Column(Integer)
    not_recommended = Column(Integer)
    game_total_votes = Column(Integer)
    player_count_total_votes = Column(Integer)  # total votes for this player count
    recommendation = Column(String)  # 'best', 'recommended', or 'not_recommended'
    game = relationship("BoardGame", back_populates="suggested_players")

class LanguageDependence(Base):
    __tablename__ = 'language_dependence'
    
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('games.id'))
    level_1 = Column(Integer)
    level_2 = Column(Integer)
    level_3 = Column(Integer)
    level_4 = Column(Integer)
    level_5 = Column(Integer)
    total_votes = Column(Integer)
    language_dependency = Column(Integer)  # 1-5 scale
    game = relationship("BoardGame", back_populates="language_dependence")

class Integration(Base):
    __tablename__ = 'integrations'
    
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('games.id'))
    boardgameintegration_id = Column(Integer)
    boardgameintegration_name = Column(String)
    game = relationship("BoardGame", back_populates="integrations")

class Implementation(Base):
    __tablename__ = 'implementations'
    
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('games.id'))
    boardgameimplementation_id = Column(Integer)
    boardgameimplementation_name = Column(String)
    game = relationship("BoardGame", back_populates="implementations")

class Compilation(Base):
    __tablename__ = 'compilations'
    
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('games.id'))
    boardgamecompilation_id = Column(Integer)
    boardgamecompilation_name = Column(String)
    game = relationship("BoardGame", back_populates="compilations")

class Expansion(Base):
    __tablename__ = 'expansions'
    
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('games.id'))
    boardgameexpansion_id = Column(Integer)
    boardgameexpansion_name = Column(String)
    game = relationship("BoardGame", back_populates="expansions")

class Family(Base):
    __tablename__ = 'families'
    
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('games.id'))
    boardgamefamily_id = Column(Integer)
    boardgamefamily_name = Column(String)
    game = relationship("BoardGame", back_populates="families")

class Version(Base):
    __tablename__ = 'versions'
    
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('games.id'))
    version_id = Column(Integer)
    width = Column(Float)
    length = Column(Float)
    depth = Column(Float)
    year_published = Column(Integer)
    thumbnail = Column(String)
    image = Column(String)
    language = Column(String)
    version_nickname = Column(String)
    game = relationship("BoardGame", back_populates="versions")