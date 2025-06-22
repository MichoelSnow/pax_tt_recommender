from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, select
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
    designer_id: Optional[str] = None,
    artist_id: Optional[str] = None,
    recommendations: Optional[str] = None,
    weight: Optional[str] = None,
    mechanics: Optional[str] = None,
    categories: Optional[str] = None
):
    try:
        # Start with a base query - only load main game fields initially
        query = db.query(models.BoardGame)

        # Apply simple filters first
        if search:
            search_term = f"%{search}%"
            query = query.filter(models.BoardGame.name.ilike(search_term))

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

        # Apply relationship filters using efficient subqueries with timeout protection
        if designer_id:
            try:
                designer_ids = [int(d_id) for d_id in designer_id.split(',')]
                subquery = select(models.BoardGame.id).join(
                    models.BoardGame.designers
                ).filter(
                    models.Designer.boardgamedesigner_id.in_(designer_ids)
                ).group_by(
                    models.BoardGame.id
                ).having(
                    func.count(models.Designer.boardgamedesigner_id) == len(designer_ids)
                ).subquery()
                query = query.filter(models.BoardGame.id.in_(subquery))
            except Exception as e:
                logger.warning(f"Error applying designer filter: {str(e)}")
                # Continue without designer filter if it fails

        if artist_id:
            try:
                artist_ids = [int(a_id) for a_id in artist_id.split(',')]
                subquery = select(models.BoardGame.id).join(
                    models.BoardGame.artists
                ).filter(
                    models.Artist.boardgameartist_id.in_(artist_ids)
                ).group_by(
                    models.BoardGame.id
                ).having(
                    func.count(models.Artist.boardgameartist_id) == len(artist_ids)
                ).subquery()
                query = query.filter(models.BoardGame.id.in_(subquery))
            except Exception as e:
                logger.warning(f"Error applying artist filter: {str(e)}")
                # Continue without artist filter if it fails

        if mechanics:
            try:
                mechanic_ids = [int(m_id) for m_id in mechanics.split(',')]
                subquery = select(models.BoardGame.id).join(
                    models.BoardGame.mechanics
                ).filter(
                    models.Mechanic.boardgamemechanic_id.in_(mechanic_ids)
                ).group_by(
                    models.BoardGame.id
                ).having(
                    func.count(models.Mechanic.boardgamemechanic_id) == len(mechanic_ids)
                ).subquery()
                query = query.filter(models.BoardGame.id.in_(subquery))
            except Exception as e:
                logger.warning(f"Error applying mechanics filter: {str(e)}")
                # Continue without mechanics filter if it fails

        if categories:
            try:
                category_ids = [int(c_id) for c_id in categories.split(',')]
                subquery = select(models.BoardGame.id).join(
                    models.BoardGame.categories
                ).filter(
                    models.Category.boardgamecategory_id.in_(category_ids)
                ).group_by(
                    models.BoardGame.id
                ).having(
                    func.count(models.Category.boardgamecategory_id) == len(category_ids)
                ).subquery()
                query = query.filter(models.BoardGame.id.in_(subquery))
            except Exception as e:
                logger.warning(f"Error applying categories filter: {str(e)}")
                # Continue without categories filter if it fails

        if recommendations:
            try:
                rec_list = recommendations.split(',')
                # Need to join with suggested_players table for recommendations filter
                query = query.join(models.BoardGame.suggested_players)
                if players:
                    query = query.filter(models.SuggestedPlayer.player_count == players)
                if 'best' in rec_list:
                    query = query.filter(
                        models.SuggestedPlayer.recommendation_level == 'best'
                    )
                if 'recommended' in rec_list:
                    query = query.filter(
                        models.SuggestedPlayer.recommendation_level == 'recommended'
                    )
            except Exception as e:
                logger.warning(f"Error applying recommendations filter: {str(e)}")
                # Continue without recommendations filter if it fails
        elif players:
            try:
                # Use min_players and max_players from games table instead of suggested_players
                query = query.filter(
                    and_(
                        models.BoardGame.min_players <= players,
                        models.BoardGame.max_players >= players
                    )
                )
            except Exception as e:
                logger.warning(f"Error applying players filter: {str(e)}")
                # Continue without players filter if it fails

        # Get total count before pagination with timeout protection
        try:
            total = query.count()
        except Exception as e:
            logger.error(f"Error getting total count: {str(e)}")
            total = 0

        # Verify that the sort_by field exists in the model
        if not hasattr(models.BoardGame, sort_by):
            raise ValueError(f"Invalid sort field: {sort_by}")

        # Order by the selected rank field, with NULL ranks appearing last
        rank_field = getattr(models.BoardGame, sort_by)
        query = query.order_by(rank_field.asc().nullslast())

        # Apply pagination with timeout protection
        try:
            games = query.offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error fetching games: {str(e)}")
            games = []
        
        # Only load relationships for the returned games to avoid N+1
        if games:
            try:
                game_ids = [game.id for game in games]
                
                # Load mechanics for returned games
                mechanics_data = db.query(models.Mechanic).filter(
                    models.Mechanic.game_id.in_(game_ids)
                ).all()
                
                # Load categories for returned games
                categories_data = db.query(models.Category).filter(
                    models.Category.game_id.in_(game_ids)
                ).all()
                
                # Load suggested players for returned games
                suggested_players_data = db.query(models.SuggestedPlayer).filter(
                    models.SuggestedPlayer.game_id.in_(game_ids)
                ).all()
                
                # Group by game_id for efficient access
                mechanics_by_game = {}
                for m in mechanics_data:
                    if m.game_id not in mechanics_by_game:
                        mechanics_by_game[m.game_id] = []
                    mechanics_by_game[m.game_id].append(m)
                
                categories_by_game = {}
                for c in categories_data:
                    if c.game_id not in categories_by_game:
                        categories_by_game[c.game_id] = []
                    categories_by_game[c.game_id].append(c)
                
                suggested_players_by_game = {}
                for sp in suggested_players_data:
                    if sp.game_id not in suggested_players_by_game:
                        suggested_players_by_game[sp.game_id] = []
                    suggested_players_by_game[sp.game_id].append(sp)
                
                # Attach relationships to games
                for game in games:
                    game.mechanics = mechanics_by_game.get(game.id, [])
                    game.categories = categories_by_game.get(game.id, [])
                    game.suggested_players = suggested_players_by_game.get(game.id, [])
            except Exception as e:
                logger.error(f"Error loading relationships: {str(e)}")
                # Continue without relationships if loading fails
        
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

def get_mechanics_cached(db: Session, skip: int = 0, limit: int = 100):
    """Get mechanics with pagination and caching-friendly structure."""
    mechanics = db.query(
        models.Mechanic.boardgamemechanic_id,
        models.Mechanic.boardgamemechanic_name
    ).distinct().order_by(
        models.Mechanic.boardgamemechanic_name
    ).offset(skip).limit(limit).all()
    
    return [{"boardgamemechanic_id": m[0], "boardgamemechanic_name": m[1]} for m in mechanics]

def get_mechanics_count(db: Session):
    """Get total count of unique mechanics for pagination."""
    return db.query(models.Mechanic.boardgamemechanic_id).distinct().count()

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

def get_recommendations(
    game_id: int,
    db: Session,
    limit: int = 10,
    disliked_games: Optional[List[int]] = None,
    anti_weight: float = 1.0
) -> List[models.BoardGame]:
    """
    Get game recommendations using the trained model.
    
    Args:
        game_id: ID of the game to get recommendations for
        db: Database session
        limit: Maximum number of recommendations to return
        disliked_games: Optional list of game IDs to use as anti-recommendations
        anti_weight: Weight to apply to anti-recommendations
        
    Returns:
        List of recommended BoardGame objects
    """
    from .recommender import get_recommendations as get_model_recommendations
    return get_model_recommendations(
        game_id=game_id,
        db=db,
        limit=limit,
        disliked_games=disliked_games,
        anti_weight=anti_weight
    )

# PAX Games CRUD operations
def get_pax_games(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    convention_name: Optional[str] = None,
    convention_year: Optional[int] = None,
    has_bgg_id: Optional[bool] = None
):
    """Get PAX games with optional filtering."""
    query = db.query(models.PAXGame)
    
    if convention_name:
        query = query.filter(models.PAXGame.convention_name == convention_name)
    
    if convention_year:
        query = query.filter(models.PAXGame.convention_year == convention_year)
    
    if has_bgg_id is not None:
        if has_bgg_id:
            query = query.filter(models.PAXGame.bgg_id.isnot(None))
        else:
            query = query.filter(models.PAXGame.bgg_id.is_(None))
    
    # Get total count before pagination
    total = query.count()
    
    # Apply pagination
    pax_games = query.offset(skip).limit(limit).all()
    
    return pax_games, total


def get_pax_game(db: Session, pax_game_id: int):
    """Get a specific PAX game by ID."""
    return db.query(models.PAXGame).filter(models.PAXGame.id == pax_game_id).first()


def get_pax_game_by_bgg_id(db: Session, bgg_id: int):
    """Get PAX game by BGG ID."""
    return db.query(models.PAXGame).filter(models.PAXGame.bgg_id == bgg_id).first()


def create_pax_game(db: Session, pax_game: schemas.PAXGameCreate):
    """Create a new PAX game."""
    db_pax_game = models.PAXGame(**pax_game.model_dump())
    db.add(db_pax_game)
    db.commit()
    db.refresh(db_pax_game)
    return db_pax_game


def get_pax_games_by_convention(db: Session, convention_name: str, convention_year: Optional[int] = None):
    """Get PAX games for a specific convention."""
    query = db.query(models.PAXGame).filter(models.PAXGame.convention_name == convention_name)
    
    if convention_year:
        query = query.filter(models.PAXGame.convention_year == convention_year)
    
    return query.all()


def get_pax_games_with_board_game_links(db: Session, skip: int = 0, limit: int = 100):
    """Get PAX games that have links to BoardGame records."""
    query = db.query(models.PAXGame).filter(models.PAXGame.bgg_id.isnot(None))
    
    # Get total count before pagination
    total = query.count()
    
    # Apply pagination
    pax_games = query.offset(skip).limit(limit).all()
    
    return pax_games, total