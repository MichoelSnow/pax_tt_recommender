from sqlalchemy.orm import Session
from sqlalchemy import select
from app import models

# def get_games(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.BoardGame).offset(skip).limit(limit).all()

def get_games(db: Session, skip: int, limit: int, designer=None, mechanic=None, genre=None):
    query = db.query(models.BoardGame)

    if designer:
        query = query.filter(models.BoardGame.designer == designer)

    if mechanic:
        query = query.join(models.Mechanic).filter(models.Mechanic.name == mechanic)

    if genre:
        query = query.join(models.Genre).filter(models.Genre.name == genre)

    return query.offset(skip).limit(limit).all()


def get_game(db: Session, game_id: int):
    return db.query(models.BoardGame).filter(models.BoardGame.id == game_id).first()

def get_filter_options(db: Session):
    designers = db.query(models.BoardGame.designer).distinct().all()
    mechanics = db.query(models.Mechanic.name).distinct().all()
    genres = db.query(models.Genre.name).distinct().all()
    return {
        "designers": [d[0] for d in designers],
        "mechanics": [m[0] for m in mechanics],
        "genres": [g[0] for g in genres]
    }