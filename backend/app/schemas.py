from pydantic import BaseModel
from typing import List

class Mechanic(BaseModel):
    name: str
    class Config:
        orm_mode = True

class Genre(BaseModel):
    name: str
    class Config:
        orm_mode = True

class BoardGameOut(BaseModel):
    id: int
    name: str
    designer: str
    player_count: str
    play_time: str
    image_url: str
    mechanics: List[Mechanic]
    genres: List[Genre]
    class Config:
        orm_mode = True

class FilterOptions(BaseModel):
    designers: List[str]
    mechanics: List[str]
    genres: List[str]