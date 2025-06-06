from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models

def get_recommendations(game_id: int, db: Session, limit: int = 5):
    target_ratings = db.query(models.UserRating).filter(models.UserRating.game_id == game_id).all()
    user_ids = {r.user_id for r in target_ratings}

    candidate_ratings = db.query(models.UserRating).filter(models.UserRating.user_id.in_(user_ids)).all()
    
    scores = {}
    for r in candidate_ratings:
        if r.game_id == game_id:
            continue
        scores.setdefault(r.game_id, []).append(r.rating)

    average_scores = [
        (gid, sum(ratings) / len(ratings)) for gid, ratings in scores.items()
    ]
    average_scores.sort(key=lambda x: x[1], reverse=True)

    game_ids = [gid for gid, _ in average_scores[:limit]]
    return db.query(models.BoardGame).filter(models.BoardGame.id.in_(game_ids)).all()
