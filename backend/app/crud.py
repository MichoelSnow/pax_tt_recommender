from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from sqlalchemy.sql import or_, and_
from . import models, schemas
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

# def get_games(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.BoardGame).offset(skip).limit(limit).all()

def get_games(
    db: Session,
    skip: int = 0,
    limit: int = 24,
    sort_by: Optional[str] = "rank",
    search: Optional[str] = None,
    players: Optional[int] = None,
    designer_id: Optional[int] = None,
    artist_id: Optional[int] = None,
    recommendations: Optional[str] = None,
    weight: Optional[str] = None,
    mechanics: Optional[str] = None
):
    try:
        # Start with a base query that only loads the main game fields
        query = db.query(models.BoardGame).options(
            # Only load the relationships needed for filtering
            joinedload(models.BoardGame.mechanics).load_only(
                models.Mechanic.boardgamemechanic_id,
                models.Mechanic.boardgamemechanic_name
            ),
            joinedload(models.BoardGame.suggested_players).load_only(
                models.SuggestedPlayer.player_count,
                models.SuggestedPlayer.recommendation
            )
        )

        if search:
            search_term = f"%{search}%"
            query = query.filter(models.BoardGame.name.ilike(search_term))

        if designer_id:
            query = query.join(models.BoardGame.designers).filter(models.Designer.boardgamedesigner_id == designer_id)
        
        if artist_id:
            query = query.join(models.BoardGame.artists).filter(models.Artist.boardgameartist_id == artist_id)

        if mechanics:
            mechanic_ids = mechanics.split(',')
            for m_id in mechanic_ids:
                query = query.join(models.BoardGame.mechanics).filter(models.Mechanic.boardgamemechanic_id == int(m_id))

        if players:
            query = query.join(models.BoardGame.suggested_players).filter(
                models.SuggestedPlayer.player_count == players
            )

        if recommendations:
            rec_list = recommendations.split(',')
            if 'best' in rec_list:
                query = query.join(models.BoardGame.suggested_players).filter(
                    and_(
                        models.SuggestedPlayer.player_count == players,
                        models.SuggestedPlayer.recommendation == 'best'
                    )
                )
            if 'recommended' in rec_list:
                query = query.join(models.BoardGame.suggested_players).filter(
                    and_(
                        models.SuggestedPlayer.player_count == players,
                        models.SuggestedPlayer.recommendation == 'recommended'
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

        # Get total count before pagination
        total = query.count()

        # Verify that the sort_by field exists in the model
        if not hasattr(models.BoardGame, sort_by):
            raise ValueError(f"Invalid sort field: {sort_by}")

        # Order by the selected rank field, with NULL ranks appearing last
        rank_field = getattr(models.BoardGame, sort_by)
        query = query.order_by(rank_field.asc().nullslast())

        # Apply pagination
        games = query.offset(skip).limit(limit).all()
        
        return games, total
    except Exception as e:
        logger.error(f"Error in get_games: {str(e)}")
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