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
import csv

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
            # "id": game_dict.get("id"),
            # "name": game_dict.get("name", ""),
            # "thumbnail": game_dict.get("thumbnail"),
            # "image": game_dict.get("image"),
            # "minplayers": game_dict.get("minplayers"),
            # "maxplayers": game_dict.get("maxplayers"),
            # "playingtime": game_dict.get("playingtime"),
            # "minplaytime": game_dict.get("minplaytime"),
            # "maxplaytime": game_dict.get("maxplaytime"),
            # "minage": game_dict.get("minage"),
            # "year_published": game_dict.get("yearpublished"),
            # "average_rating": game_dict.get("average"),
            # "num_ratings": game_dict.get("numratings"),
            # "num_comments": game_dict.get("numcomments"),
            # "num_weights": game_dict.get("numweights"),
            # "average_weight": game_dict.get("averageweight"),
            # "stddev": game_dict.get("stddev"),
            # "median": game_dict.get("median"),
            # "owned": game_dict.get("owned"),
            # "trading": game_dict.get("trading"),
            # "wanting": game_dict.get("wanting"),
            # "wishing": game_dict.get("wishing"),
            # "bayes_average": game_dict.get("bayesaverage"),
            # "is_expansion": bool(game_dict.get("is_expansion", False)),
            # # Ranking fields - allow null values for missing ranks
            # "rank": game_dict.get("rank"),
            # "abstracts_rank": game_dict.get("abstracts_rank"),
            # "cgs_rank": game_dict.get("cgs_rank"),
            # "childrensgames_rank": game_dict.get("childrensgames_rank"),
            # "familygames_rank": game_dict.get("familygames_rank"),
            # "partygames_rank": game_dict.get("partygames_rank"),
            # "strategygames_rank": game_dict.get("strategygames_rank"),
            # "thematic_rank": game_dict.get("thematic_rank"),
            # "wargames_rank": game_dict.get("wargames_rank"),
            # Related entities
            # "mechanics": [{"name": m} for m in game_dict.get("boardgamemechanic", [])],
            # "categories": [{"name": c} for c in game_dict.get("boardgamecategory", [])],
            # "designers": [{"name": d} for d in game_dict.get("boardgamedesigner", [])],
            # "artists": [{"name": a} for a in game_dict.get("boardgameartist", [])],
            # "publishers": [
            #     {"name": p} for p in game_dict.get("boardgamepublisher", [])
            # ],
            "suggested_playerage": game_dict.get("suggested_playerage"),
            "suggested_playerage_quartiles": game_dict.get(
                "suggested_playerage_quartiles"
            ),
            "language_dependence": game_dict.get("language_dependence"),
            "language_dependence_quartiles": game_dict.get(
                "language_dependence_quartiles"
            ),
            # "suggested_numplayers": game_dict.get("suggested_numplayers"),
            # "player_count_recs": game_dict.get("player_count_recs"),
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
        raise ValueError(
            f"Error processing game {game_dict.get('game_id', 'unknown')}: {str(e)}"
        )


def extract_suggested_num_players(df_merged: pd.DataFrame) -> pd.DataFrame:
    """
    Extract player count recs from the dataframe.
    """
    df_sugg_num_players = df_merged.loc[
        ~(df_merged["suggested_numplayers"] == {}), ["id", "suggested_numplayers"]
    ]
    df_sugg_num_players["game_total_votes"] = df_sugg_num_players[
        "suggested_numplayers"
    ].apply(lambda x: x["total_votes"])
    df_sugg_num_players = df_sugg_num_players.loc[
        df_sugg_num_players["game_total_votes"] > 10
    ]
    col = "suggested_numplayers"
    df_exploded = pd.DataFrame(
        [
            {"id": row_id, col: k, "votes": v}
            for row_id, d in zip(df_sugg_num_players["id"], df_sugg_num_players[col])
            if isinstance(d, dict)  # ensure it's a dict
            for k, v in d.items()
        ]
    )
    df_exploded = pd.concat(
        [df_exploded.drop(columns="votes"), pd.json_normalize(df_exploded["votes"])],
        axis=1,
    )
    df_exploded = df_exploded.loc[
        (df_exploded[col] != "total_votes")
        & ~(df_exploded[col].str.contains("+", regex=False))
    ]
    df_exploded = df_exploded.merge(
        df_sugg_num_players[["id", "game_total_votes"]], on="id", how="left"
    )
    df_exploded.columns = [x.lower().replace(" ", "_") for x in df_exploded.columns]
    for col in df_exploded.columns:
        df_exploded[col] = df_exploded[col].astype(pd.Int64Dtype())
    df_exploded["recommendation"] = df_exploded[
        ["best", "recommended", "not_recommended"]
    ].idxmax(axis=1)
    df_exploded = df_exploded.rename(
        columns={"suggested_numplayers": "player_count", "id": "game_id"}
    )
    return df_exploded


def combine_crawler_data(
    ranks_file: str, data_file: str, output_file_base: str, timestamp: int
) -> None:
    """
    Combine board game rankings and detailed data into a format for backend import.

    Args:
        ranks_file (str): Path to the board game rankings CSV file
        data_file (str): Path to the board game data parquet file
        output_file_base (str): Base path to save the combined data
        timestamp (int): Unix timestamp for the output file
    """
    logger.info("Starting data combination process")

    # Read the data files
    try:
        df_ranks = pd.read_csv(ranks_file, sep="|", escapechar="\\")
        df_data = pd.read_parquet(data_file)
        logger.info(
            f"Successfully loaded {len(df_ranks)} rankings and {len(df_data)} detailed records"
        )
    except Exception as e:
        logger.error(f"Error reading input files: {str(e)}")
        raise

    # Drop columns from ranks that we don't want to merge
    df_ranks = df_ranks.drop(columns=["queried_at_utc"])

    # Merge rankings data with game data
    df_merged = pd.merge(df_data, df_ranks, on="id", how="inner")

    int_cols = [
        "yearpublished",
        "rank",
        "usersrated",
        "is_expansion",
        "abstracts_rank",
        "cgs_rank",
        "childrensgames_rank",
        "familygames_rank",
        "partygames_rank",
        "strategygames_rank",
        "thematic_rank",
        "wargames_rank",
        "minplayers",
        "maxplayers",
        "playingtime",
        "minplaytime",
        "maxplaytime",
        "minage",
        "owned",
        "trading",
        "wanting",
        "wishing",
        "numcomments",
        "numweights",
        "numratings",
    ]

    float_cols = [
        "bayesaverage",
        "average",
        "stddev",
        "median",
        "averageweight",
    ]

    str_cols = [
        "name",
        "thumbnail",
        "image",
    ]

    dict_id_cols = [
        "boardgamecategory",
        "boardgamemechanic",
        "boardgamefamily",
        "boardgameexpansion",
        "boardgameartist",
        "boardgamecompilation",
        "boardgameimplementation",
        "boardgamedesigner",
        "boardgamepublisher",
        "boardgameintegration",
    ]

    # Covert columns to int
    for col in int_cols:
        df_merged[col] = df_merged[col].fillna(value=pd.NA).astype(pd.Int64Dtype())

    # Convert columns to float
    for col in float_cols:
        df_merged[col] = df_merged[col].fillna(value=pd.NA).astype(pd.Float64Dtype())

    # Save the int, float, and str columns to csv
    output_file_data = f"{output_file_base}_data_{timestamp}.csv"
    df_merged[["id"] + int_cols + float_cols + str_cols].to_csv(
        output_file_data,
        index=False,
        sep="|",
        escapechar="\\",
        quoting=csv.QUOTE_NONE,
    )
    logger.info(
        f"Successfully saved basic info for {len(df_merged)} games to {output_file_data}"
    )

    # Save the dict_id_cols to csv
    for col in dict_id_cols:
        df_dict_id = pd.DataFrame(
            [
                {"game_id": row_id, f"{col}_id": k, f"{col}_name": v}
                for row_id, d in zip(df_merged["id"], df_merged[col])
                if isinstance(d, dict)  # ensure it's a dict
                for k, v in d.items()
            ]
        )
        df_dict_id[f"{col}_id"] = df_dict_id[f"{col}_id"].astype(int)
        output_file_dict_id = f"{output_file_base}_{col}_{timestamp}.csv"
        df_dict_id.to_csv(
            output_file_dict_id,
            index=False,
            sep="|",
            escapechar="\\",
            quoting=csv.QUOTE_NONE,
        )
        logger.info(
            f"Successfully saved {col} for {len(df_dict_id)} games to {output_file_dict_id}"
        )

    # Extract player count recs
    df_suggested_num_players = extract_suggested_num_players(df_merged)
    output_file_suggested_num_players = (
        f"{output_file_base}_suggested_num_players_{timestamp}.csv"
    )
    df_suggested_num_players.to_csv(
        output_file_suggested_num_players,
        index=False,
        sep="|",
        escapechar="\\",
        quoting=csv.QUOTE_NONE,
    )
    logger.info(
        f"Successfully saved {len(df_suggested_num_players)} suggested num players to {output_file_suggested_num_players}"
    )
    # # Convert data to dictionaries
    # games_data = df_merged.to_dict(orient="records")

    # # Process each game's data
    # processed_games = []
    # for game in games_data:
    #     processed = process_game_data(game)
    #     processed_games.append(processed)

    # # Save the processed data
    # try:
    #     with open(output_file, "w") as f:
    #         json.dump(processed_games, f, indent=2)
    #     logger.info(
    #         f"Successfully saved {len(processed_games)} processed games to {output_file}"
    #     )
    # except Exception as e:
    #     logger.error(f"Error saving output file: {str(e)}")
    #     raise


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
    output_file_base = data_dir / "processed_games"

    # Process the data
    combine_crawler_data(
        ranks_file=str(latest_ranks),
        data_file=str(latest_data),
        output_file_base=str(output_file_base),
        timestamp=timestamp,
    )


if __name__ == "__main__":
    main()
