import csv
import logging
from app import models
from app.database import SessionLocal, engine

logging.basicConfig(
    filename='import.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

models.Base.metadata.create_all(bind=engine)
db = SessionLocal()

def import_games(db):
    with open("boardgames.csv", newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            game = models.BoardGame(
                name=row["name"],
                designer=row["designer"],
                player_count=row["player_count"],
                play_time=row["play_time"],
                image_url=row["image_url"]
            )
            db.add(game)
            db.commit()
            db.refresh(game)

            mechanics = [m.strip() for m in row.get("mechanics", "").split(";") if m.strip()]
            genres = [g.strip() for g in row.get("genres", "").split(";") if g.strip()]

            for m in mechanics:
                db.add(models.Mechanic(game_id=game.id, name=m))
            for g in genres:
                db.add(models.Genre(game_id=game.id, name=g))

            db.commit()
            logging.info(f"Imported game: {game.name}")

def import_ratings(db):
    with open("ratings.csv", newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            game_id = int(row["game_id"])
            game_exists = db.query(models.BoardGame).filter(models.BoardGame.id == game_id).first()
            if not game_exists:
                logging.warning(f"Skipping rating: game_id {game_id} does not exist")
                continue

            rating = models.UserRating(
                user_id=int(row["user_id"]),
                game_id=game_id,
                rating=float(row["rating"])
            )
            db.add(rating)
            logging.info(f"Imported rating for game_id {game_id} by user {rating.user_id}")
        db.commit()

def run_import_csv(import_games=True, import_ratings=True):
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    if import_games:
        import_games(db)
    if import_ratings:
        import_ratings(db)
    db.close()
