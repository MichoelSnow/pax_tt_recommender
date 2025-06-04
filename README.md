# Board Game Recommender

A full-stack application for discovering and recommending board games, built with FastAPI and React.

## Project Structure

```
pax_tt_recommender/
├── backend/               # FastAPI backend
│   └── app/              # Backend application code
├── crawler/              # Data collection and processing
│   └── src/             # Crawler source code
├── frontend/            # React frontend
│   ├── src/            # Frontend source code
│   └── package.json    # Node.js dependencies
├── data/               # Data storage
│   └── crawler/        # Crawled and processed data
└── pyproject.toml      # Poetry dependencies for backend and crawler
```

## Prerequisites

- Python 3.10+
- Node.js 16+
- PostgreSQL
- Chrome/Chromium (for web scraping)
- Poetry (Python package manager)

## Setup

### 1. Python Environment Setup

```bash
# Install Poetry if you haven't already
curl -sSL https://install.python-poetry.org | python3 -

# Setup Python environment
poetry install
poetry shell  # Activates the virtual environment
```

### 2. Frontend Setup

```bash
cd frontend
npm install
```

## Data Collection and Processing

The crawler collects data from BoardGameGeek.com in three main steps. Make sure you're in the Poetry shell first:

```bash
poetry shell
```

### 1. Collect Board Game Rankings

```bash
python crawler/src/get_ranks.py
```

This will:
- Authenticate with BoardGameGeek
- Download current board game rankings
- Save to `data/crawler/boardgame_ranks_YYYYMMDD.csv`

### 2. Collect Detailed Game Data

```bash
python crawler/src/get_game_data.py
```

This will:
- Process games in batches of 20 (BGG API limit)
- Collect detailed information for each game
- Save to `data/crawler/boardgame_data_TIMESTAMP.parquet`

### 3. Collect User Ratings

```bash
python crawler/src/get_ratings.py
```

This will:
- Process games in batches
- Collect user ratings for each game
- Save to `data/crawler/boardgame_ratings_TIMESTAMP.parquet`

The `get_game_data` and `get_ratings` scripts support the `--continue-from-last` flag to resume from the most recent output file if the process was interrupted:

```bash
python crawler/src/get_game_data.py --continue-from-last
python crawler/src/get_ratings.py --continue-from-last
```

### 4. Process the Data

```bash
python crawler/src/data_processor.py
```

This will:
- Combine rankings and detailed game data
- Process relationships (mechanics, categories, etc.)
- Generate multiple CSV files in `data/processed/`:
  - `processed_games_data_TIMESTAMP.csv` - Basic game info
  - `processed_games_boardgamecategory_TIMESTAMP.csv` - Categories
  - `processed_games_boardgamemechanic_TIMESTAMP.csv` - Mechanics
  - `processed_games_boardgamedesigner_TIMESTAMP.csv` - Designers
  - `processed_games_boardgameartist_TIMESTAMP.csv` - Artists
  - `processed_games_boardgamepublisher_TIMESTAMP.csv` - Publishers
  - `processed_games_boardgamefamily_TIMESTAMP.csv` - Game families
  - `processed_games_boardgameexpansion_TIMESTAMP.csv` - Expansions
  - `processed_games_boardgamecompilation_TIMESTAMP.csv` - Compilations
  - `processed_games_boardgameimplementation_TIMESTAMP.csv` - Implementations
  - `processed_games_boardgameintegration_TIMESTAMP.csv` - Integrations
  - `processed_games_suggested_num_players_TIMESTAMP.csv` - Player recommendations
  - `processed_games_language_dependence_TIMESTAMP.csv` - Language dependence
  - `processed_games_versions_TIMESTAMP.csv` - Game versions

## Importing Data to Backend

Make sure you're in the Poetry shell first:

```bash
poetry shell
```

Then run the import script:

```bash
python backend/app/import_data.py
```

This will:
- Find the most recent processed games files
- Import all games and related entities into the database
- Process data in batches of 200 games
- Log progress to `import_data.log`

You can also delete the existing database before import:

```bash
python backend/app/import_data.py --delete-existing
```

## Running the Development Servers

### Backend Server

Make sure you're in the Poetry shell first:

```bash
poetry shell
```

Then start the server:

```bash
uvicorn backend.app.main:app --reload
```

The API will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

### Frontend Server

```bash
cd frontend
npm start
```

The frontend will be available at `http://localhost:3000`

## Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/boardgames
SECRET_KEY=your-secret-key
```

## API Endpoints

- `GET /games` - List all games with optional filters
- `GET /games/{game_id}` - Get detailed game information
- `GET /games/{game_id}/recommendations` - Get game recommendations
- `GET /mechanics` - List all game mechanics
- `GET /categories` - List all game categories
- `GET /designers` - List all game designers
- `GET /artists` - List all game artists
- `GET /publishers` - List all game publishers

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
