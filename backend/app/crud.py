from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models, schemas
from typing import List, Optional

# def get_games(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.BoardGame).offset(skip).limit(limit).all()

def get_games(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    designer: Optional[str] = None,
    mechanic: Optional[str] = None,
    category: Optional[str] = None,
    publisher: Optional[str] = None,
    search: Optional[str] = None,
    players: Optional[int] = None
):
    query = db.query(models.BoardGame)
    
    if search:
        query = query.filter(models.BoardGame.name.ilike(f'%{search}%'))
    if players:
        query = query.filter(
            models.BoardGame.min_players <= players,
            models.BoardGame.max_players >= players
        )
    if designer:
        query = query.join(models.Designer).filter(models.Designer.name == designer)
    if mechanic:
        query = query.join(models.Mechanic).filter(models.Mechanic.name == mechanic)
    if category:
        query = query.join(models.Category).filter(models.Category.name == category)
    if publisher:
        query = query.join(models.Publisher).filter(models.Publisher.name == publisher)
    
    # Order by rank, with NULL ranks appearing last
    query = query.order_by(models.BoardGame.rank.asc().nullslast())
    
    return query.offset(skip).limit(limit).all()

def get_game(db: Session, game_id: int):
    return db.query(models.BoardGame).filter(models.BoardGame.id == game_id).first()

def create_game(db: Session, game: schemas.BoardGameCreate):
    db_game = models.BoardGame(**game.dict(exclude={'mechanics', 'categories', 'designers', 'artists', 'publishers'}))
    db.add(db_game)
    db.commit()
    db.refresh(db_game)
    return db_game

def get_filter_options(db: Session):
    designers = db.query(models.Designer.name).distinct().all()
    mechanics = db.query(models.Mechanic.name).distinct().all()
    categories = db.query(models.Category.name).distinct().all()
    publishers = db.query(models.Publisher.name).distinct().all()
    
    return {
        "designers": [d[0] for d in designers],
        "mechanics": [m[0] for m in mechanics],
        "categories": [c[0] for c in categories],
        "publishers": [p[0] for p in publishers]
    }

def add_mechanic(db: Session, game_id: int, mechanic_name: str):
    mechanic = models.Mechanic(game_id=game_id, name=mechanic_name)
    db.add(mechanic)
    db.commit()
    return mechanic

def add_category(db: Session, game_id: int, category_name: str):
    category = models.Category(game_id=game_id, name=category_name)
    db.add(category)
    db.commit()
    return category

def add_designer(db: Session, game_id: int, designer_name: str):
    designer = models.Designer(game_id=game_id, name=designer_name)
    db.add(designer)
    db.commit()
    return designer

def add_artist(db: Session, game_id: int, artist_name: str):
    artist = models.Artist(game_id=game_id, name=artist_name)
    db.add(artist)
    db.commit()
    return artist

def add_publisher(db: Session, game_id: int, publisher_name: str):
    publisher = models.Publisher(game_id=game_id, name=publisher_name)
    db.add(publisher)
    db.commit()
    return publisher