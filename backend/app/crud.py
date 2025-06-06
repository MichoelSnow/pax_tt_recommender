from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.sql import or_, and_
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
    mechanics: Optional[str] = None,
    category: Optional[str] = None,
    publisher: Optional[str] = None,
    search: Optional[str] = None,
    players: Optional[int] = None,
    recommendations: Optional[str] = None,
    weight: Optional[str] = None,
    sort_by: Optional[str] = "rank"
):
    try:
        query = db.query(models.BoardGame)

        if search:
            search_term = f"%{search}%"
            query = query.filter(models.BoardGame.name.ilike(search_term))

        if designer:
            query = query.join(models.BoardGame.designers).filter(models.Designer.name == designer)

        if mechanic:
            query = query.join(models.BoardGame.mechanics).filter(models.Mechanic.name == mechanic)

        if mechanics:
            mechanic_list = mechanics.split(',')
            for m in mechanic_list:
                query = query.join(models.BoardGame.mechanics).filter(models.Mechanic.name == m)

        if category:
            query = query.join(models.BoardGame.categories).filter(models.Category.name == category)

        if publisher:
            query = query.join(models.BoardGame.publishers).filter(models.Publisher.name == publisher)

        if players:
            query = query.join(models.BoardGame.suggested_players).filter(
                and_(
                    models.SuggestedPlayer.min_players <= players,
                    models.SuggestedPlayer.max_players >= players
                )
            )

        if recommendations:
            rec_list = recommendations.split(',')
            if 'best' in rec_list:
                query = query.join(models.BoardGame.suggested_players).filter(
                    and_(
                        models.SuggestedPlayer.min_players <= players,
                        models.SuggestedPlayer.max_players >= players,
                        models.SuggestedPlayer.best == True
                    )
                )
            if 'recommended' in rec_list:
                query = query.join(models.BoardGame.suggested_players).filter(
                    and_(
                        models.SuggestedPlayer.min_players <= players,
                        models.SuggestedPlayer.max_players >= players,
                        models.SuggestedPlayer.recommended == True
                    )
                )

        if weight:
            weight_list = weight.split(',')
            weight_conditions = []
            if 'beginner' in weight_list:
                weight_conditions.append(models.BoardGame.average_weight <= 2.0)
            if 'midweight' in weight_list:
                weight_conditions.append(and_(
                    models.BoardGame.average_weight > 2.0,
                    models.BoardGame.average_weight < 4.0
                ))
            if 'heavy' in weight_list:
                weight_conditions.append(models.BoardGame.average_weight >= 4.0)
            
            if weight_conditions:
                query = query.filter(or_(*weight_conditions))

        # Verify that the sort_by field exists in the model
        if not hasattr(models.BoardGame, sort_by):
            raise ValueError(f"Invalid sort field: {sort_by}")

        # Order by the selected rank field, with NULL ranks appearing last
        rank_field = getattr(models.BoardGame, sort_by)
        query = query.order_by(rank_field.asc().nullslast())

        return query.offset(skip).limit(limit).all()
    except Exception as e:
        print(f"Error in get_games: {str(e)}")  # Add server-side logging
        raise

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

def get_mechanics_by_frequency(db: Session):
    return db.query(
        models.Mechanic.boardgamemechanic_name.label('name'),
        func.count(models.Mechanic.boardgamemechanic_name).label('count')
    ).group_by(models.Mechanic.boardgamemechanic_name).order_by(func.count(models.Mechanic.boardgamemechanic_name).desc()).all()