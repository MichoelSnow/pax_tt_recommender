from . import models
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)
db = SessionLocal()

# Sample board games
games = [
    models.BoardGame(
        name="Catan",
        designer="Klaus Teuber",
        player_count="3-4",
        play_time="60-120",
        image_url="https://example.com/catan.jpg"
    ),
    models.BoardGame(
        name="Ticket to Ride",
        designer="Alan R. Moon",
        player_count="2-5",
        play_time="45-60",
        image_url="https://example.com/ttr.jpg"
    ),
    models.BoardGame(
        name="Carcassonne",
        designer="Klaus-Jürgen Wrede",
        player_count="2-5",
        play_time="30-45",
        image_url="https://example.com/carcassonne.jpg"
    )
]
db.add_all(games)
db.commit()

games = db.query(models.BoardGame).all()

# Add mechanics and genres
for game in games:
    if game.name == "Catan":
        db.add_all([
            models.Mechanic(game_id=game.id, name="Trading"),
            models.Mechanic(game_id=game.id, name="Dice Rolling"),
            models.Genre(game_id=game.id, name="Strategy")
        ])
    elif game.name == "Ticket to Ride":
        db.add_all([
            models.Mechanic(game_id=game.id, name="Set Collection"),
            models.Genre(game_id=game.id, name="Family")
        ])
    elif game.name == "Carcassonne":
        db.add_all([
            models.Mechanic(game_id=game.id, name="Tile Placement"),
            models.Genre(game_id=game.id, name="Strategy")
        ])
db.commit()

# Sample ratings
ratings = [
    models.UserRating(user_id=1, game_id=games[0].id, rating=8.0),
    models.UserRating(user_id=1, game_id=games[1].id, rating=7.0),
    models.UserRating(user_id=2, game_id=games[0].id, rating=9.0),
    models.UserRating(user_id=2, game_id=games[2].id, rating=8.5),
    models.UserRating(user_id=3, game_id=games[1].id, rating=6.0),
    models.UserRating(user_id=3, game_id=games[2].id, rating=7.5),
]
db.add_all(ratings)
db.commit()

db.close()