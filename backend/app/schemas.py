from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any


class ArtistBase(BaseModel):
    boardgameartist_id: int
    boardgameartist_name: str

    model_config = ConfigDict(from_attributes=True)


class CategoryBase(BaseModel):
    boardgamecategory_id: int
    boardgamecategory_name: str

    model_config = ConfigDict(from_attributes=True)


class CompilationBase(BaseModel):
    boardgamecompilation_id: int
    boardgamecompilation_name: str

    model_config = ConfigDict(from_attributes=True)


class DesignerBase(BaseModel):
    boardgamedesigner_id: int
    boardgamedesigner_name: str

    model_config = ConfigDict(from_attributes=True)


class ExpansionBase(BaseModel):
    boardgameexpansion_id: int
    boardgameexpansion_name: str

    model_config = ConfigDict(from_attributes=True)


class FamilyBase(BaseModel):
    boardgamefamily_id: int
    boardgamefamily_name: str

    model_config = ConfigDict(from_attributes=True)


class ImplementationBase(BaseModel):
    boardgameimplementation_id: int
    boardgameimplementation_name: str

    model_config = ConfigDict(from_attributes=True)


class IntegrationBase(BaseModel):
    boardgameintegration_id: int
    boardgameintegration_name: str

    model_config = ConfigDict(from_attributes=True)


class MechanicBase(BaseModel):
    boardgamemechanic_id: int
    boardgamemechanic_name: str

    model_config = ConfigDict(from_attributes=True)


class PublisherBase(BaseModel):
    boardgamepublisher_id: int
    boardgamepublisher_name: str

    model_config = ConfigDict(from_attributes=True)


class SuggestedPlayerBase(BaseModel):
    player_count: int
    recommendation: str

    model_config = ConfigDict(from_attributes=True)


class LanguageDependenceBase(BaseModel):
    level: Optional[str] = None
    votes: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class VersionBase(BaseModel):
    version_id: int
    width: Optional[float] = None
    length: Optional[float] = None
    depth: Optional[float] = None
    year_published: Optional[int] = None
    thumbnail: Optional[str] = None
    image: Optional[str] = None
    language: Optional[str] = None
    version_nickname: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class BoardGameBase(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    thumbnail: Optional[str] = None
    image: Optional[str] = None
    min_players: Optional[int] = None
    max_players: Optional[int] = None
    playing_time: Optional[int] = None
    min_playtime: Optional[int] = None
    max_playtime: Optional[int] = None
    min_age: Optional[int] = None
    year_published: Optional[int] = None
    average: Optional[float] = None
    num_ratings: Optional[int] = None
    num_comments: Optional[int] = None
    num_weights: Optional[int] = None
    average_weight: Optional[float] = None
    stddev: Optional[float] = None
    median: Optional[float] = None
    owned: Optional[int] = None
    trading: Optional[int] = None
    wanting: Optional[int] = None
    wishing: Optional[int] = None
    bayes_average: Optional[float] = None
    users_rated: Optional[int] = None
    is_expansion: Optional[bool] = None
    rank: Optional[int] = None
    abstracts_rank: Optional[int] = None
    cgs_rank: Optional[int] = None
    childrens_games_rank: Optional[int] = None
    family_games_rank: Optional[int] = None
    party_games_rank: Optional[int] = None
    strategy_games_rank: Optional[int] = None
    thematic_rank: Optional[int] = None
    wargames_rank: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class BoardGameCreate(BoardGameBase):
    pass


class BoardGameOut(BoardGameBase):
    mechanics: Optional[List[MechanicBase]]
    categories: Optional[List[CategoryBase]]
    designers: Optional[List[DesignerBase]]
    artists: Optional[List[ArtistBase]]
    publishers: Optional[List[PublisherBase]]
    suggested_players: Optional[List[SuggestedPlayerBase]]
    language_dependence: Optional[LanguageDependenceBase]
    integrations: Optional[List[IntegrationBase]]
    implementations: Optional[List[ImplementationBase]]
    compilations: Optional[List[CompilationBase]]
    expansions: Optional[List[ExpansionBase]]
    families: Optional[List[FamilyBase]]
    versions: Optional[List[VersionBase]]

    model_config = ConfigDict(from_attributes=True)


class FilterOptions(BaseModel):
    designers: List[str]
    mechanics: List[str]
    categories: List[str]
    publishers: List[str]

    model_config = ConfigDict(from_attributes=True)


class MechanicFrequency(BaseModel):
    name: str
    count: int

    model_config = ConfigDict(from_attributes=True)


class Mechanic(MechanicBase):
    game_id: int

    model_config = ConfigDict(from_attributes=True)


class BoardGameList(BoardGameBase):
    mechanics: List[MechanicBase] = []
    suggested_players: List[SuggestedPlayerBase] = []

    model_config = ConfigDict(from_attributes=True)


class GameListResponse(BaseModel):
    games: List[BoardGameList]
    total: int

    model_config = ConfigDict(from_attributes=True)
