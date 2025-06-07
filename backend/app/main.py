from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import List, Optional
import logging
from . import crud, models, schemas
from .database import engine

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

@app.get("/games/", response_model=List[schemas.BoardGameOut])
async def list_games(
    skip: int = 0,
    limit: int = 50,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = None,
    min_players: Optional[int] = None,
    max_players: Optional[int] = None,
    min_playtime: Optional[int] = None,
    max_playtime: Optional[int] = None,
    min_age: Optional[int] = None,
    year_published: Optional[int] = None,
    mechanics: Optional[List[str]] = None,
    categories: Optional[List[str]] = None,
    designers: Optional[List[str]] = None,
    publishers: Optional[List[str]] = None,
    search: Optional[str] = None
):
    try:
        games = crud.get_games(
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
            min_players=min_players,
            max_players=max_players,
            min_playtime=min_playtime,
            max_playtime=max_playtime,
            min_age=min_age,
            year_published=year_published,
            mechanics=mechanics,
            categories=categories,
            designers=designers,
            publishers=publishers,
            search=search
        )
        return games
    except Exception as e:
        logger.error(f"Error fetching games: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error fetching games")

@app.get("/games/{game_id}", response_model=schemas.BoardGameOut)
async def get_game(game_id: int):
    try:
        game = crud.get_game(game_id)
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

