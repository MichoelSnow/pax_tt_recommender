from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app import models, schemas, crud, recommender
from app.database import SessionLocal, engine
from app.import_csv import run_import_csv

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS config for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/games", response_model=list[schemas.BoardGameOut])
def list_games(
    skip: int = 0,
    limit: int = 100,
    designer: str | None = None,
    mechanic: str | None = None,
    genre: str | None = None,
    db: Session = Depends(get_db)
):
    return crud.get_games(db, skip, limit, designer, mechanic, genre)

@app.get("/games/{game_id}", response_model=schemas.BoardGameOut)
def game_detail(game_id: int, db: Session = Depends(get_db)):
    game = crud.get_game(db, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game

@app.get("/games/{game_id}/recommendations", response_model=list[schemas.BoardGameOut])
def recommended_games(game_id: int, db: Session = Depends(get_db)):
    return recommender.get_recommendations(game_id, db)

@app.get("/filters", response_model=schemas.FilterOptions)
def get_filter_options(db: Session = Depends(get_db)):
    return crud.get_filter_options(db)

@app.post("/import")
def trigger_csv_import(
    import_games: bool = Body(True),
    import_ratings: bool = Body(True)
):
    run_import_csv(import_games=import_games, import_ratings=import_ratings)
    return {"message": "CSV import completed"}

