from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from . import models, schemas, crud, recommender
from .database import SessionLocal, engine
from .import_data import import_all_data
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Board Game Recommender API")

# CORS config for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc.detail)},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc)},
    )

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/games", response_model=List[schemas.BoardGameOut])
@app.get("/games/", response_model=List[schemas.BoardGameOut])
def list_games(
    skip: int = 0,
    limit: int = 100,
    designer: Optional[str] = None,
    designer_id: Optional[int] = None,
    artist_id: Optional[int] = None,
    mechanic: Optional[str] = None,
    mechanics: Optional[str] = None,
    category: Optional[str] = None,
    publisher: Optional[str] = None,
    search: Optional[str] = None,
    players: Optional[int] = None,
    recommendations: Optional[str] = None,
    weight: Optional[str] = None,
    sort_by: Optional[str] = "rank",
    db: Session = Depends(get_db)
):
    try:
        return crud.get_games(db, skip, limit, designer, designer_id, artist_id, mechanic, mechanics, category, publisher, search, players, recommendations, weight, sort_by)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error in list_games endpoint: {str(e)}")  # Add server-side logging
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/games/{game_id}", response_model=schemas.BoardGameOut)
def game_detail(game_id: int, db: Session = Depends(get_db)):
    game = crud.get_game(db, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game

@app.get("/games/{game_id}/recommendations", response_model=List[schemas.BoardGameOut])
def recommended_games(game_id: int, db: Session = Depends(get_db)):
    return recommender.get_recommendations(game_id, db)

@app.get("/filters", response_model=schemas.FilterOptions)
def get_filter_options(db: Session = Depends(get_db)):
    return crud.get_filter_options(db)

@app.post("/import")
def trigger_import(delete_existing: bool = Body(False)):
    import_all_data(delete_existing=delete_existing)
    return {"message": "Data import completed"}

@app.post("/games", response_model=schemas.BoardGameOut)
def create_game(game: schemas.BoardGameCreate, db: Session = Depends(get_db)):
    return crud.create_game(db, game)

@app.post("/games/{game_id}/mechanics", response_model=schemas.MechanicBase)
def add_mechanic(game_id: int, mechanic: schemas.MechanicBase, db: Session = Depends(get_db)):
    return crud.add_mechanic(db, game_id, mechanic)

@app.post("/games/{game_id}/categories", response_model=schemas.CategoryBase)
def add_category(game_id: int, category: schemas.CategoryBase, db: Session = Depends(get_db)):
    return crud.add_category(db, game_id, category)

@app.post("/games/{game_id}/designers", response_model=schemas.DesignerBase)
def add_designer(game_id: int, designer: schemas.DesignerBase, db: Session = Depends(get_db)):
    return crud.add_designer(db, game_id, designer)

@app.post("/games/{game_id}/artists", response_model=schemas.ArtistBase)
def add_artist(game_id: int, artist: schemas.ArtistBase, db: Session = Depends(get_db)):
    return crud.add_artist(db, game_id, artist)

@app.post("/games/{game_id}/publishers", response_model=schemas.PublisherBase)
def add_publisher(game_id: int, publisher: schemas.PublisherBase, db: Session = Depends(get_db)):
    return crud.add_publisher(db, game_id, publisher)

@app.post("/games/{game_id}/versions", response_model=schemas.VersionBase)
def add_version(game_id: int, version: schemas.VersionBase, db: Session = Depends(get_db)):
    return crud.add_version(db, game_id, version)

@app.post("/games/{game_id}/suggested-players", response_model=schemas.SuggestedPlayerBase)
def add_suggested_player(game_id: int, player: schemas.SuggestedPlayerBase, db: Session = Depends(get_db)):
    return crud.add_suggested_player(db, game_id, player)

@app.post("/games/{game_id}/language-dependence", response_model=schemas.LanguageDependenceBase)
def add_language_dependence(game_id: int, lang_dep: schemas.LanguageDependenceBase, db: Session = Depends(get_db)):
    return crud.add_language_dependence(db, game_id, lang_dep)

@app.post("/games/{game_id}/integrations", response_model=schemas.IntegrationBase)
def add_integration(game_id: int, integration: schemas.IntegrationBase, db: Session = Depends(get_db)):
    return crud.add_integration(db, game_id, integration)

@app.post("/games/{game_id}/implementations", response_model=schemas.ImplementationBase)
def add_implementation(game_id: int, implementation: schemas.ImplementationBase, db: Session = Depends(get_db)):
    return crud.add_implementation(db, game_id, implementation)

@app.post("/games/{game_id}/compilations", response_model=schemas.CompilationBase)
def add_compilation(game_id: int, compilation: schemas.CompilationBase, db: Session = Depends(get_db)):
    return crud.add_compilation(db, game_id, compilation)

@app.post("/games/{game_id}/expansions", response_model=schemas.ExpansionBase)
def add_expansion(game_id: int, expansion: schemas.ExpansionBase, db: Session = Depends(get_db)):
    return crud.add_expansion(db, game_id, expansion)

@app.post("/games/{game_id}/families", response_model=schemas.FamilyBase)
def add_family(game_id: int, family: schemas.FamilyBase, db: Session = Depends(get_db)):
    return crud.add_family(db, game_id, family)

@app.get("/mechanics", response_model=List[schemas.MechanicFrequency])
def get_mechanics(db: Session = Depends(get_db)):
    try:
        mechanics = crud.get_mechanics_by_frequency(db)
        return [{"name": m.name, "count": m.count} for m in mechanics]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

