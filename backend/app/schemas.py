from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class ArtistBase(BaseModel):
    boardgameartist_id: int
    boardgameartist_name: str

    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    boardgamecategory_id: int
    boardgamecategory_name: str

    class Config:
        from_attributes = True


class CompilationBase(BaseModel):
    boardgamecompilation_id: int
    boardgamecompilation_name: str

    class Config:
        from_attributes = True


class DesignerBase(BaseModel):
    boardgamedesigner_id: int
    boardgamedesigner_name: str

    class Config:
        from_attributes = True


class ExpansionBase(BaseModel):
    boardgameexpansion_id: int
    boardgameexpansion_name: str

    class Config:
        from_attributes = True


class FamilyBase(BaseModel):
    boardgamefamily_id: int
    boardgamefamily_name: str

    class Config:
        from_attributes = True


class ImplementationBase(BaseModel):
    boardgameimplementation_id: int
    boardgameimplementation_name: str

    class Config:
        from_attributes = True


class IntegrationBase(BaseModel):
    boardgameintegration_id: int
    boardgameintegration_name: str

    class Config:
        from_attributes = True


class MechanicBase(BaseModel):
    boardgamemechanic_id: int
    boardgamemechanic_name: str

    class Config:
        from_attributes = True


class PublisherBase(BaseModel):
    boardgamepublisher_id: int
    boardgamepublisher_name: str

    class Config:
        from_attributes = True


class SuggestedPlayerBase(BaseModel):
    player_count: int
    best: int
    recommended: int
    not_recommended: int
    game_total_votes: int
    player_count_total_votes: int  
    recommendation: str

    class Config:
        from_attributes = True


class LanguageDependenceBase(BaseModel):
    level_1: Optional[int]
    level_2: Optional[int]
    level_3: Optional[int]
    level_4: Optional[int]
    level_5: Optional[int]
    total_votes: Optional[int]
    language_dependency: Optional[int]

    class Config:
        from_attributes = True


class VersionBase(BaseModel):
    version_id: int
    width: Optional[float]
    length: Optional[float]
    depth: Optional[float]
    year_published: Optional[int]
    thumbnail: Optional[str]
    image: Optional[str]
    language: Optional[str]
    version_nickname: Optional[str]

    class Config:
        from_attributes = True


class BoardGameBase(BaseModel):
    id: int
    name: str
    thumbnail: Optional[str]
    image: Optional[str]
    min_players: Optional[int]
    max_players: Optional[int]
    playing_time: Optional[int]
    min_playtime: Optional[int]
    max_playtime: Optional[int]
    min_age: Optional[int]
    year_published: Optional[int]

    # Statistics
    average: Optional[float]  # average_rating
    num_ratings: Optional[int]  # num_ratings
    num_comments: Optional[int]  # num_comments
    num_weights: Optional[int]  # num_weights
    average_weight: Optional[float]  # average_weight
    stddev: Optional[float]
    median: Optional[float]
    owned: Optional[int]
    trading: Optional[int]
    wanting: Optional[int]
    wishing: Optional[int]
    bayes_average: Optional[float]  # bayes_average
    users_rated: Optional[int]  # number of users who rated the game
    is_expansion: Optional[bool]

    # Rankings
    rank: Optional[int]
    abstracts_rank: Optional[int]
    cgs_rank: Optional[int]
    childrens_games_rank: Optional[int]
    family_games_rank: Optional[int]
    party_games_rank: Optional[int]
    strategy_games_rank: Optional[int]
    thematic_rank: Optional[int]
    wargames_rank: Optional[int]

    class Config:
        from_attributes = True


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

    class Config:
        from_attributes = True


class FilterOptions(BaseModel):
    designers: List[str]
    mechanics: List[str]
    categories: List[str]
    publishers: List[str]
