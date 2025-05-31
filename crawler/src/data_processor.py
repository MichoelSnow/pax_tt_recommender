"""
Data Processor for Board Game Recommender

This script processes the outputs from the crawler and formats them for import into the backend database.
It combines board game rankings and detailed game data into a format that matches the backend models.
"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Any
import logging
import os
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("data_processor.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Get the project root directory (two levels up from this script)
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent

def process_game_data(game_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a single game's data into the format expected by the backend.
    
    Args:
        game_dict (Dict[str, Any]): Raw game data from crawler
        
    Returns:
        Dict[str, Any]: Processed game data matching backend schema
    """
    try:
        # Handle versions - convert None to empty list
        # versions = game_dict.get("versions")
        # if versions is None:
        #     versions = []
            
        processed = {
            "game_id": game_dict.get("game_id"),
            "name": game_dict.get("name", ""),
            "thumbnail": game_dict.get("thumbnail"),
            "image": game_dict.get("image"),
            "minplayers": int(game_dict.get("minplayers", 0)),
            "maxplayers": int(game_dict.get("maxplayers", 0)),
            "playingtime": int(game_dict.get("playingtime", 0)),
            "minplaytime": int(game_dict.get("minplaytime", 0)),
            "maxplaytime": int(game_dict.get("maxplaytime", 0)),
            "minage": int(game_dict.get("minage", 0)),
            "year_published": int(game_dict.get("yearpublished", 0)),
            "average_rating": float(game_dict.get("average", 0.0)),
            "num_ratings": int(game_dict.get("numratings", 0)),
            "num_comments": int(game_dict.get("numcomments", 0)),
            "num_weights": int(game_dict.get("numweights", 0)),
            "average_weight": float(game_dict.get("averageweight", 0.0)),
            "stddev": float(game_dict.get("stddev", 0.0)),
            "median": float(game_dict.get("median", 0.0)),
            "owned": int(game_dict.get("owned", 0)),
            "trading": int(game_dict.get("trading", 0)),
            "wanting": int(game_dict.get("wanting", 0)),
            "wishing": int(game_dict.get("wishing", 0)),
            "suggested_playerage": game_dict.get("suggested_playerage"),
            "suggested_playerage_quartiles": game_dict.get("suggested_playerage_quartiles"),
            "language_dependence": game_dict.get("language_dependence"),
            "language_dependence_quartiles": game_dict.get("language_dependence_quartiles"),
            "suggested_numplayers": game_dict.get("suggested_numplayers"),
            "player_count_recs": game_dict.get("player_count_recs"),
            "bayes_average": float(game_dict.get("bayesaverage", 0.0)),
            "is_expansion": bool(game_dict.get("is_expansion", False)),
            
            # Ranking fields - allow null values for missing ranks
            "rank": int(game_dict["rank"]),
            "abstracts_rank": int(game_dict["abstracts_rank"]) if game_dict.get("abstracts_rank") is not None and not pd.isna(game_dict["abstracts_rank"]) else None,
            "cgs_rank": int(game_dict["cgs_rank"]) if game_dict.get("cgs_rank") is not None and not pd.isna(game_dict["cgs_rank"]) else None,
            "childrensgames_rank": int(game_dict["childrensgames_rank"]) if game_dict.get("childrensgames_rank") is not None and not pd.isna(game_dict["childrensgames_rank"]) else None,
            "familygames_rank": int(game_dict["familygames_rank"]) if game_dict.get("familygames_rank") is not None and not pd.isna(game_dict["familygames_rank"]) else None,
            "partygames_rank": int(game_dict["partygames_rank"]) if game_dict.get("partygames_rank") is not None and not pd.isna(game_dict["partygames_rank"]) else None,
            "strategygames_rank": int(game_dict["strategygames_rank"]) if game_dict.get("strategygames_rank") is not None and not pd.isna(game_dict["strategygames_rank"]) else None,
            "thematic_rank": int(game_dict["thematic_rank"]) if game_dict.get("thematic_rank") is not None and not pd.isna(game_dict["thematic_rank"]) else None,
            "wargames_rank": int(game_dict["wargames_rank"]) if game_dict.get("wargames_rank") is not None and not pd.isna(game_dict["wargames_rank"]) else None,
            
            # Related entities
            "mechanics": [{"name": m} for m in game_dict.get("boardgamemechanic", [])],
            "categories": [{"name": c} for c in game_dict.get("boardgamecategory", [])],
            "designers": [{"name": d} for d in game_dict.get("boardgamedesigner", [])],
            "artists": [{"name": a} for a in game_dict.get("boardgameartist", [])],
            "publishers": [{"name": p} for p in game_dict.get("boardgamepublisher", [])],
            # "versions": [
            #     {
            #         "version_id": v.get("version_id"),
            #         "name": v.get("version_nickname"),
            #         "year_published": v.get("year_published"),
            #         "language": v.get("language"),
            #         "width": v.get("width"),
            #         "length": v.get("length"),
            #         "depth": v.get("depth"),
            #         "thumbnail": v.get("thumbnail"),
            #         "image": v.get("image")
            #     }
            #     for v in versions
            # ]
        }
        return processed
    except Exception as e:
        # Find which field caused the error
        for field, value in game_dict.items():
            try:
                if isinstance(value, (int, float)) and pd.isna(value):
                    raise ValueError(f"Field '{field}' contains NaN value")
            except Exception:
                pass
        raise ValueError(f"Error processing game {game_dict.get('game_id', 'unknown')}: {str(e)}")

def combine_crawler_data(
    ranks_file: str,
    data_file: str,
    output_file: str
) -> None:
    """
    Combine board game rankings and detailed data into a format for backend import.
    
    Args:
        ranks_file (str): Path to the board game rankings CSV file
        data_file (str): Path to the board game data parquet file
        output_file (str): Path to save the combined data
    """
    logger.info("Starting data combination process")
    
    # Read the data files
    try:
        df_ranks = pd.read_csv(ranks_file, sep="|", escapechar="\\")
        df_data = pd.read_parquet(data_file)
        logger.info(f"Successfully loaded {len(df_ranks)} rankings and {len(df_data)} detailed records")
    except Exception as e:
        logger.error(f"Error reading input files: {str(e)}")
        raise
    
    # Convert game_id to int for merging
    df_data['game_id'] = df_data['game_id'].astype(int)
    
    # Drop columns from ranks that we don't want to merge
    df_ranks = df_ranks.drop(columns=['yearpublished', 'queried_at_utc'])
    
    # Merge rankings data with game data
    df_merged = pd.merge(
        df_data,
        df_ranks,
        left_on='game_id',
        right_on='id',
        how='inner'
    )
    
    # Convert data to dictionaries
    games_data = df_merged.to_dict(orient="records")
    
    # Process each game's data
    processed_games = []
    for game in games_data:
        try:
            processed = process_game_data(game)
            processed_games.append(processed)
        except Exception as e:
            logger.error(str(e))
            raise  # Stop processing on first error
    
    # Save the processed data
    try:
        with open(output_file, 'w') as f:
            json.dump(processed_games, f, indent=2)
        logger.info(f"Successfully saved {len(processed_games)} processed games to {output_file}")
    except Exception as e:
        logger.error(f"Error saving output file: {str(e)}")
        raise

def main():
    """Main function to process the most recent crawler outputs."""
    # Get the data directory using the project root
    data_dir = PROJECT_ROOT / "data" / "crawler"
    
    # Find the most recent ranks file
    ranks_files = list(data_dir.glob("boardgame_ranks_*.csv"))
    if not ranks_files:
        raise FileNotFoundError(f"No board game ranks files found in {data_dir}")
    latest_ranks = max(ranks_files, key=lambda x: x.stat().st_mtime)
    
    # Find the most recent data file
    data_files = list(data_dir.glob("boardgame_data_*.parquet"))
    if not data_files:
        raise FileNotFoundError(f"No board game data files found in {data_dir}")
    latest_data = max(data_files, key=lambda x: x.stat().st_mtime)
    
    # Set output file path with Unix timestamp
    timestamp = int(time.time())
    output_file = data_dir / f"processed_games_{timestamp}.json"
    
    # Process the data
    combine_crawler_data(
        ranks_file=str(latest_ranks),
        data_file=str(latest_data),
        output_file=str(output_file)
    )

if __name__ == "__main__":
    main() 