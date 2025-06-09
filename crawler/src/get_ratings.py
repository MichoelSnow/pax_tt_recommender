"""
BoardGameGeek (BGG) Ratings Crawler

This script crawls user ratings from BoardGameGeek.com.
This is the third script in the data collection pipeline and should be run after get_game_data.py.

Execution order:
1. get_ranks.py - Gets the current board game rankings
2. get_game_data.py - Gets detailed game information
3. get_ratings.py - Gets user ratings for each game

Usage:
    python get_ratings.py [--continue-from-last]
"""

from bs4 import BeautifulSoup
import requests
import pandas as pd
import logging
import math
from time import sleep, time
from pathlib import Path
import argparse
import bs4

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("get_ratings.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def get_boardgame_ratings(
    boardgame_data: pd.DataFrame,
    boardgame_ratings: pd.DataFrame = None,
    batch_saves: bool = False,
    batch_size: int = 20,
    log_level: str = "INFO",
    drop_partial_ratings: bool = False,
    update_numratings: bool = False,
):
    """
    Fetch user ratings for each board game from BGG API.
    The BGG API has a limit of 20 IDs per request, so we process in batches.

    Args:
        boardgame_data (pd.DataFrame): DataFrame from get_boardgame_data()
        boardgame_ratings (pd.DataFrame, optional): Existing ratings data to update
        batch_saves (bool): Whether to save data after each batch
        batch_size (int): Number of games to process in each batch. BGG API has a limit of 20 IDs per request.
        log_level (str): Logging level for this function
        drop_partial_ratings (bool): Whether to drop games with partial ratings
        update_numratings (bool): Whether to update number of ratings for games with missing ratings

    Returns:
        pd.DataFrame: DataFrame containing user ratings
    """
    # Set logging level for this function
    current_level = logger.level
    logger.setLevel(getattr(logging, log_level.upper()))

    query_time = int(time())
    data_dir = Path(__file__).parent.parent.parent / "data" / "crawler"
    data_dir.mkdir(parents=True, exist_ok=True)
    save_path = data_dir / f"boardgame_ratings_{query_time}.parquet"

    boardgame_master_dict = {}
    boardgame_data_ratings = boardgame_data.loc[boardgame_data["numratings"] > 100].sort_values(
        by="numratings", ascending=False
    )
    boardgame_ids = boardgame_data_ratings["id"].tolist()
    # Check if there are any ids which have not had all their ratings pulled down yet
    if boardgame_ratings is not None:
        df_ratings_len = boardgame_ratings.copy()
        df_ratings_len = df_ratings_len.drop(columns=["id"])
        df_ratings_len = df_ratings_len.fillna("")
        for col in df_ratings_len.columns:
            df_ratings_len[col] = df_ratings_len[col].apply(len)
        df_ratings_pulled = pd.DataFrame(
            {
                "id": boardgame_ratings["id"].tolist(),
                "ratings_pulled": df_ratings_len.sum(axis=1).tolist(),
            }
        )
        boardgame_data_ratings = boardgame_data_ratings.merge(df_ratings_pulled, on="id", how="left")
        completed_ids = boardgame_data_ratings.loc[
            (boardgame_data_ratings["ratings_pulled"] - boardgame_data_ratings["numratings"])
            / (boardgame_data_ratings["numratings"])
            >= -0.01,
            "id",
        ].tolist()
        logger.info(
            f"Found {len(completed_ids)} boardgames with all ratings already pulled to completion"
        )
        boardgame_ids = list(set(boardgame_ids).difference(set(completed_ids)))
        df_missing_ratings = boardgame_data_ratings.loc[
            (boardgame_data_ratings["ratings_pulled"] - boardgame_data_ratings["numratings"])
            / (boardgame_data_ratings["numratings"])
            < -0.01
        ]
        logger.info(
            f"Found {df_missing_ratings.shape[0]} boardgames with missing ratings"
        )
        if drop_partial_ratings:
            logger.info("Dropping partial ratings")
            boardgame_ratings = boardgame_ratings.loc[
                ~(boardgame_ratings["id"].isin(df_missing_ratings["id"]))
            ]
        else:
            logger.info(
                "Keeping partial ratings and will continue to pull down the missing ratings"
            )

        df_ratings_tmp = boardgame_ratings.copy().set_index("id")
        df_ratings_tmp.index.name = None
        boardgame_master_dict = df_ratings_tmp.to_dict(orient="index")

        if not drop_partial_ratings and df_missing_ratings.shape[0] > 0:
            for _, row in df_missing_ratings.iterrows():
                ratings_count_dict = {row["id"]: row["numratings"]}
                max_ratings_page = math.ceil(row["numratings"] / 100)
                start_page = int(row["ratings_pulled"] / 100) + 1
                boardgame_master_dict = iterate_through_ratings_pages(
                    boardgame_master_dict=boardgame_master_dict,
                    max_ratings_page=max_ratings_page,
                    ratings_count_dict=ratings_count_dict,
                    start_page=start_page,
                    batch_saves=batch_saves,
                    save_path=save_path,
                )
                logger.info(f"Successfully completed fetching ratings for {row['id']}")
            df_ratings = (
                pd.DataFrame()
                .from_dict(data=boardgame_master_dict, orient="index")
                .reset_index(names="id")
            )
            boardgame_ids = list(
                set(boardgame_ids).difference(set(df_ratings["id"].tolist()))
            )

        # Update numratings if requested
        if update_numratings:
            game_data_save_path = data_dir / f"boardgame_data_{query_time}.parquet"
            logger.info("Updating number of ratings for games with missing ratings")
            for batch_num in range(math.ceil(len(boardgame_ids) / batch_size)):
                logger.info(
                    f"Processing numratings batch {batch_num} of {math.ceil(len(boardgame_ids) / batch_size)}"
                )
                batch_ids = boardgame_ids[
                    batch_num * batch_size : (batch_num + 1) * batch_size
                ]
                batch_ids = [str(x) for x in batch_ids]
                logger.debug(f"Processing boardgame IDs for numratings: {batch_ids}")

                bg_info_url = f"https://www.boardgamegeek.com/xmlapi2/thing?type=boardgame&ratingcomments=1&id={','.join(batch_ids)}"
                bgg_response = requests.get(bg_info_url)
                soup_xml = BeautifulSoup(bgg_response.content, "xml")
                games_xml_list = soup_xml.find_all(
                    "item", attrs={"type": ["boardgame", "boardgameexpansion"]}
                )

                for game_xml in games_xml_list:
                    game_id = int(game_xml["id"])
                    if game_xml.find("comments") is not None:
                        boardgame_data.loc[
                            boardgame_data["id"] == game_id, "numratings"
                        ] = int(game_xml.find("comments")["totalitems"])
                    else:
                        boardgame_data.loc[
                            boardgame_data["id"] == game_id, "numratings"
                        ] = 0
                if batch_saves and (batch_num + 1) % 20 == 0:
                    logger.info(f"Saving batch {batch_num} data")
                    boardgame_data.to_parquet(game_data_save_path)
                    logger.info(f"Saved batch {batch_num} data to {game_data_save_path}")

                sleep(1)

            # Save updated game data            
            boardgame_data.to_parquet(game_data_save_path)
            logger.info(f"Saved updated game data to {game_data_save_path}")
            boardgame_data_ratings = boardgame_data.loc[boardgame_data["numratings"] > 100].sort_values(
                by="numratings", ascending=False
            )
            

    logger.info(f"Starting to fetch ratings for {len(boardgame_ids)} boardgames")

    for batch_num in range(math.ceil(len(boardgame_ids) / batch_size)):
        logger.info(
            f"Processing batch {batch_num + 1} of {math.ceil(len(boardgame_ids) / batch_size)}"
        )
        batch_ids = boardgame_ids[batch_num * batch_size : (batch_num + 1) * batch_size]
        df_batch_games = boardgame_data_ratings.loc[boardgame_data_ratings["id"].isin(batch_ids)]
        ratings_count_dict = pd.Series(
            df_batch_games["numratings"].values,
            index=df_batch_games["id"],
        ).to_dict()
        max_ratings_page = math.ceil(max(ratings_count_dict.values()) / 100)
        logger.info(
            f"Processing {max_ratings_page} rating pages for batch {batch_num + 1}"
        )
        boardgame_master_dict = iterate_through_ratings_pages(
            boardgame_master_dict=boardgame_master_dict,
            max_ratings_page=max_ratings_page,
            ratings_count_dict=ratings_count_dict,
            batch_saves=batch_saves,
            save_path=save_path,
        )

        if batch_saves:
            logger.info(f"Saving batch {batch_num + 1} data")
            df_ratings = (
                pd.DataFrame()
                .from_dict(data=boardgame_master_dict, orient="index")
                .reset_index(names="id")
            )
            df_ratings.to_parquet(save_path)
            logger.info(f"Saved batch {batch_num + 1} data to {save_path}")

    if len(boardgame_ids) > 0:
        df_ratings = (
            pd.DataFrame()
            .from_dict(data=boardgame_master_dict, orient="index")
            .reset_index(names="id")
        )
        logger.info("Successfully completed fetching all ratings")
        df_ratings.to_parquet(save_path)
        logger.info(f"Saved final data to {save_path}")
    else:
        logger.warning("No ratings were fetched")

    # Restore original logging level
    logger.setLevel(current_level)


def iterate_through_ratings_pages(
    boardgame_master_dict: dict,
    max_ratings_page: int,
    ratings_count_dict: dict,
    start_page: int = 1,
    batch_saves: bool = False,
    save_path: str = None,
):
    """
    Helper function to iterate through paginated rating data from BGG API.

    Args:
        boardgame_master_dict (dict): Dictionary to store rating data
        max_ratings_page (int): Maximum number of rating pages to process. Derived from the number of ratings for each game.
        ratings_count_dict (dict): Dictionary mapping game IDs to number of ratings
        start_page (int): Page number to start processing from
        batch_saves (bool): Whether to save data periodically
        save_path (str): Path to save data to

    Returns:
        dict: Updated dictionary containing rating data
    """
    for page_num in range(start_page, max_ratings_page + 1):
        # Only grab the pages for games which have enough ratings to be on the page num
        batch_ids_ratings = [
            str(x)
            for x in ratings_count_dict.keys()
            if math.ceil(ratings_count_dict[x] / 100) >= page_num
        ]
        bg_rating_url = f"https://www.boardgamegeek.com/xmlapi2/thing?type=boardgame&ratingcomments=1&pagesize=100&page={page_num}&id={','.join(batch_ids_ratings)}"
        bgg_rating_response = requests.get(bg_rating_url)
        soup_rating_xml = BeautifulSoup(bgg_rating_response.content, "xml")
        ratings_xml_list = soup_rating_xml.find_all("item", attrs={"type": "boardgame"})

        for game_xml in ratings_xml_list:
            if int(game_xml["id"]) not in boardgame_master_dict:
                boardgame_master_dict[int(game_xml["id"])] = {}
            boardgame_master_dict[int(game_xml["id"])] = extract_ratings(
                game_dict=boardgame_master_dict[int(game_xml["id"])], game_xml=game_xml
            )
        if batch_saves and page_num % 100 == 0:
            df_ratings = (
                pd.DataFrame()
                .from_dict(data=boardgame_master_dict, orient="index")
                .reset_index(names="id")
            )
            logger.info(f"Saving ratings page {page_num} of {max_ratings_page} data to {save_path}")
            df_ratings.to_parquet(save_path)
            logger.info(
                f"Saved ratings page {page_num} of {max_ratings_page} data to {save_path}"
            )
        elif page_num % 100 == 0:
            logger.info(f"Processed ratings page {page_num} of {max_ratings_page}")
        sleep(1)
    return boardgame_master_dict


def extract_ratings(game_dict: dict, game_xml: bs4.element.Tag):
    """
    Extract user ratings from BGG XML.

    Args:
        game_dict (dict): Dictionary to store rating data
        game_xml (bs4.element.Tag): BeautifulSoup XML element for a game

    Returns:
        dict: Updated dictionary containing user ratings
    """
    ratings_list = game_xml.find_all("comment")
    for rating in ratings_list:
        # round the rating to the nearest 0.5
        rating_round = str(round(2 * float(rating["rating"])) / 2)
        if rating_round not in game_dict:
            game_dict[rating_round] = [rating["username"]]
        else:
            game_dict[rating_round].append(rating["username"])
    return game_dict


def main():
    """Main function to get board game ratings."""
    try:
        parser = argparse.ArgumentParser(description="Get board game ratings from BGG")
        parser.add_argument(
            "--continue-from-last",
            action="store_true",
            help="Continue from the most recent output file",
        )
        parser.add_argument(
            "--drop-partial-ratings",
            action="store_true",
            help="Drop games with partial ratings instead of continuing to fetch missing ratings",
        )
        parser.add_argument(
            "--update-numratings",
            action="store_true",
            help="Update number of ratings for games with missing ratings",
        )
        args = parser.parse_args()

        # Get the most recent game data file
        data_dir = Path(__file__).parent.parent.parent / "data" / "crawler"
        game_files = list(data_dir.glob("boardgame_data_*.parquet"))
        if not game_files:
            raise FileNotFoundError("No game data files found")

        latest_games = max(game_files, key=lambda x: x.stat().st_mtime)
        logger.info(f"Using game data file: {latest_games}")

        # Read game data
        df_games = pd.read_parquet(latest_games)

        # Get existing ratings if continuing
        existing_ratings = None
        if args.continue_from_last:
            ratings_files = list(data_dir.glob("boardgame_ratings_*.parquet"))
            if ratings_files:
                latest_ratings = max(ratings_files, key=lambda x: x.stat().st_mtime)
                logger.info(f"Continuing from ratings file: {latest_ratings}")
                existing_ratings = pd.read_parquet(latest_ratings)

        # Get ratings
        get_boardgame_ratings(
            df_games,
            boardgame_ratings=existing_ratings,
            batch_saves=True,
            drop_partial_ratings=args.drop_partial_ratings,
            update_numratings=args.update_numratings,
        )
        logger.info("Successfully completed getting board game ratings")

    except Exception as e:
        logger.error(f"Error getting board game ratings: {str(e)}")
        raise


if __name__ == "__main__":
    main()
