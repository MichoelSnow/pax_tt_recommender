from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import List, Optional
import logging
from sqlalchemy.orm import Session
from . import crud, models, schemas
from .database import engine, SessionLocal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Board Game Recommender API",
    description="API for board game recommendations and filtering",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP error: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred"}
    )

@app.get("/")
async def root():
    return {"message": "Board Game Recommender API"}

@app.get("/games/", response_model=schemas.GameListResponse)
async def list_games(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 24,
    sort_by: Optional[str] = "rank",
    search: Optional[str] = None,
    players: Optional[int] = None,
    designer_id: Optional[int] = None,
    artist_id: Optional[int] = None,
    recommendations: Optional[str] = None,
    weight: Optional[str] = None,
    mechanics: Optional[str] = None,
    categories: Optional[str] = None
):
    try:
        games, total = crud.get_games(
            db=db,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            search=search,
            players=players,
            designer_id=designer_id,
            artist_id=artist_id,
            recommendations=recommendations,
            weight=weight,
            mechanics=mechanics,
            categories=categories
        )
        return {"games": games, "total": total}
    except Exception as e:
        logger.error(f"Error fetching games: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error fetching games")

@app.get("/games/{game_id}", response_model=schemas.BoardGameOut)
async def get_game(game_id: int, db: Session = Depends(get_db)):
    try:
        game = crud.get_game(db, game_id)
        if game is None:
            raise HTTPException(status_code=404, detail="Game not found")
        return game
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching game {game_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error fetching game")

@app.get("/recommendations/{game_id}", response_model=List[schemas.BoardGameOut])
async def get_recommendations(game_id: int, limit: int = 10):
    try:
        recommendations = crud.get_recommendations(game_id, limit)
        return recommendations
    except Exception as e:
        logger.error(f"Error getting recommendations for game {game_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error getting recommendations")

@app.get("/filter-options/", response_model=schemas.FilterOptions)
async def get_filter_options():
    try:
        options = crud.get_filter_options()
        return options
    except Exception as e:
        logger.error(f"Error fetching filter options: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error fetching filter options")

@app.get("/mechanics/", response_model=List[schemas.MechanicBase])
async def list_mechanics(db: Session = Depends(get_db)):
    try:
        mechanics = db.query(models.Mechanic.boardgamemechanic_id, models.Mechanic.boardgamemechanic_name).distinct().all()
        return [{"boardgamemechanic_id": m[0], "boardgamemechanic_name": m[1]} for m in mechanics]
    except Exception as e:
        logger.error(f"Error fetching mechanics: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error fetching mechanics")

