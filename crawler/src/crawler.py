from bs4 import BeautifulSoup
import json
import requests
from zipfile import ZipFile
from io import BytesIO
from time import sleep, time
import pandas as pd
from datetime import datetime
import math
import bs4
import logging
import csv

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("crawler.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def get_driver_and_cookies():
    logger.info("Initializing web driver and getting cookies")
    LOGIN_USERNAME_FIELD = '//*[@id="inputUsername"]'
    LOGIN_PASSWORD_FIELD = '//*[@id="inputPassword"]'
    LOGIN_BUTTON = '//*[@id="mainbody"]/div/div/gg-login-page/div[1]/div/gg-login-form/form/fieldset/div[3]/button[1]'

    with open("/home/msnow/config.json", "r") as fp:
        secrets = json.load(fp)
    USERNAME = secrets["bgg_crawler"]["username"]
    PASSWORD = secrets["bgg_crawler"]["password"]

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    cookies = {}

    driver = webdriver.Chrome(
        service=Service("/usr/lib/chromium-browser/chromedriver"),
        options=chrome_options,
    )
    logger.info("Chrome driver initialized successfully")

    driver.get("https://boardgamegeek.com/login")
    login = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, LOGIN_USERNAME_FIELD))
    )
    password = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, LOGIN_PASSWORD_FIELD))
    )

    login_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, LOGIN_BUTTON))
    )

    login.send_keys(USERNAME)
    password.send_keys(PASSWORD)

    login_button.click()
    sleep(1)
    logger.info("Successfully logged in to BoardGameGeek")

    selenium_cookies = driver.get_cookies()
    for cookie in selenium_cookies:
        cookies[cookie["name"]] = cookie["value"]
    logger.info("Successfully retrieved cookies")
    return cookies


def get_boardgame_ranks(cookies: dict, save_file: bool = False):
    logger.info("Fetching boardgame ranks")
    bg_ranks_pg_url = "https://boardgamegeek.com/data_dumps/bg_ranks"
    resp = requests.get(bg_ranks_pg_url, cookies=cookies)
    soup = BeautifulSoup(resp.content, "html.parser")
    bg_ranks_url = soup.find("div", {"id": "maincontent"})("a")[0]["href"]
    bg_ranks_zip = requests.get(bg_ranks_url)
    queried_at_utc = datetime.now().replace(microsecond=0).isoformat()
    with ZipFile(BytesIO(bg_ranks_zip.content)) as archive:
        with archive.open("boardgames_ranks.csv") as csv:
            df_bg_ranks = pd.read_csv(csv)
            df_bg_ranks["queried_at_utc"] = queried_at_utc
            logger.info(f"Successfully loaded {len(df_bg_ranks)} boardgames")
            if save_file:
                df_bg_ranks.to_csv(
                    f"../../data/boardgame_ranks_{queried_at_utc[:10].replace('-','')}.csv",
                    index=False,
                    sep="|",
                    escapechar="\\",
                    quoting=csv.QUOTE_NONE,
                )
            return df_bg_ranks


def get_boardgame_raw_data(
    boardgame_ranks: pd.DataFrame,
    bg_data_raw: pd.DataFrame = None,
    batch_saves: bool = False,
    batch_size: int = 20,
    log_level: str = "INFO",
):
    # Set logging level for this function
    current_level = logger.level
    logger.setLevel(getattr(logging, log_level.upper()))

    logger.info(f"Starting to fetch raw data for {len(boardgame_ranks)} boardgames")
    query_time = int(time())
    save_path = f"../../data/boardgame_data/boardgame_data_raw_{query_time}.parquet"
    boardgame_ids = boardgame_ranks["id"].tolist()
    boardgame_master_dict = {}
    if bg_data_raw is not None:
        logger.info("Using existing boardgame data as base")
        boardgame_master_dict = {
            str(x["game_id"]): x for x in bg_data_raw.to_dict(orient="records")
        }
        boardgame_ids = list(
            set(boardgame_ids).difference(
                set(bg_data_raw["game_id"].astype(int).tolist())
            )
        )
        # processed_ids = bg_data_raw["game_id"].tolist()
    logger.info(f"Found {len(boardgame_ids)} new boardgames to process")
    for batch_num in range(math.ceil(len(boardgame_ids) / batch_size)):
        logger.info(
            f"Processing batch {batch_num + 1} of {math.ceil(len(boardgame_ids) / batch_size)}"
        )
        batch_ids = boardgame_ids[batch_num * batch_size : (batch_num + 1) * batch_size]
        batch_ids = [str(x) for x in batch_ids]
        logger.debug(f"Processing boardgame IDs: {batch_ids}")
        bg_info_url = f"https://www.boardgamegeek.com/xmlapi2/thing?type=boardgame&stats=1&versions=1&ratingcomments=1&pagesize=100&page=1&id={','.join(batch_ids)}"
        bgg_response = requests.get(bg_info_url)
        soup_xml = BeautifulSoup(bgg_response.content, "xml")
        games_xml_list = soup_xml.find_all("item", attrs={"type": "boardgame"})
        ratings_count_dict = {}
        for game_xml in games_xml_list:
            game_dict = extract_basic_game_info(game_xml=game_xml)
            game_dict = extract_polls(game_dict=game_dict, game_xml=game_xml)
            game_dict = extract_poll_player_count(
                game_dict=game_dict, game_xml=game_xml
            )
            game_dict = extract_version_info(game_dict=game_dict, game_xml=game_xml)
            # if game_dict["numratings"] > 0:
            #     game_dict = extract_ratings(game_dict=game_dict, game_xml=game_xml)
            ratings_count_dict[game_dict["game_id"]] = game_dict["numratings"]
            boardgame_master_dict[game_dict["game_id"]] = game_dict
            logger.debug(f"Completed processing game ID: {game_xml['id']}")

        # max_ratings_page = math.ceil(max(ratings_count_dict.values()) / 100)
        # logger.info(
        #     f"Processing {max_ratings_page} rating pages for batch {batch_num + 1}"
        # )
        # boardgame_master_dict = iterate_through_ratings_pages(
        #     boardgame_master_dict=boardgame_master_dict,
        #     max_ratings_page=max_ratings_page,
        #     ratings_count_dict=ratings_count_dict,
        #     start_page=2,
        #     batch_saves=batch_saves,
        # )
        if batch_saves:
            logger.info(f"Saving batch {batch_num + 1} data")
            bg_data_raw = pd.DataFrame(list(boardgame_master_dict.values()))
            bg_data_raw.to_parquet(save_path)
            logger.info(f"Saved batch {batch_num + 1} data to {save_path}")
        sleep(1)

    bg_data_raw = pd.DataFrame(list(boardgame_master_dict.values()))
    logger.info("Successfully completed fetching all boardgame data")
    bg_data_raw.to_parquet(save_path)
    logger.info(f"Saved final data to {save_path}")

    # Restore original logging level
    logger.setLevel(current_level)
    return bg_data_raw


def get_rankings_data(
    boardgame_data: pd.DataFrame,
    rankings_dataframe: pd.DataFrame = None,
    batch_saves: bool = False,
    batch_size: int = 20,
):
    boardgame_master_dict = {}
    # Check if there are any ids which have not had all their ratings pulled down yet
    if rankings_dataframe is not None:
        df_ratings_len = rankings_dataframe.copy()
        df_ratings_len = df_ratings_len.drop(columns=["game_id"])
        df_ratings_len = df_ratings_len.fillna("")
        for col in df_ratings_len.columns:
            df_ratings_len[col] = df_ratings_len[col].apply(len)
        df_ratings_pulled = pd.DataFrame(
            {
                "game_id": rankings_dataframe["game_id"].tolist(),
                "ratings_pulled": df_ratings_len.sum(axis=1).tolist(),
            }
        )
        boardgame_data = boardgame_data.merge(
            df_ratings_pulled, on="game_id", how="left"
        )
        df_missing_ratings = boardgame_data[
            boardgame_data["ratings_pulled"] < boardgame_data["numratings"]
        ]
        df_ratings_tmp = rankings_dataframe.copy().set_index("game_id")
        df_ratings_tmp.index.name = None
        boardgame_master_dict = df_ratings_tmp.to_dict(orient="index")

        if df_missing_ratings.shape[0] > 0:
            ratings_count_dict = pd.Series(
                df_missing_ratings["numratings"].values,
                index=df_missing_ratings["game_id"],
            ).to_dict()
            max_ratings_page = math.ceil(max(ratings_count_dict.values()) / 100)
            start_page = int(df_missing_ratings["ratings_pulled"].min() / 100)
            boardgame_master_dict = iterate_through_ratings_pages(
                boardgame_master_dict=boardgame_master_dict,
                max_ratings_page=max_ratings_page,
                ratings_count_dict=ratings_count_dict,
                start_page=start_page,
                batch_saves=batch_saves,
            )
    boardgame_data = boardgame_data.loc[boardgame_data["numratings"] > 0].sort_values(
        by="numratings", ascending=False
    )
    boardgame_ids = boardgame_data["game_id"].tolist()
    save_time = int(time())
    save_path = f"../../data/boardgame_data/boardgame_rating_data_{save_time}.parquet"
    for batch_num in range(math.ceil(len(boardgame_ids) / batch_size)):
        logger.info(
            f"Processing batch {batch_num + 1} of {math.ceil(len(boardgame_ids) / batch_size)}"
        )
        batch_ids = boardgame_ids[batch_num * batch_size : (batch_num + 1) * batch_size]
        df_batch_games = boardgame_data.loc[boardgame_data["game_id"].isin(batch_ids)]
        ratings_count_dict = pd.Series(
            df_batch_games["numratings"].values,
            index=df_batch_games["game_id"],
        ).to_dict()
        max_ratings_page = math.ceil(max(ratings_count_dict.values()) / 100)
        logger.info(
            f"Processing {max_ratings_page} rating pages for batch {batch_num + 1}"
        )
        boardgame_master_dict = iterate_through_ratings_pages(
            boardgame_master_dict=boardgame_master_dict,
            max_ratings_page=max_ratings_page,
            ratings_count_dict=ratings_count_dict,
            start_page=1,
            batch_saves=batch_saves,
            save_path=save_path,
        )

        if batch_saves:
            logger.info(f"Saving batch {batch_num + 1} data")
            df_ratings = (
                pd.DataFrame()
                .from_dict(data=boardgame_master_dict, orient="index")
                .reset_index(names="game_id")
            )
            df_ratings.to_parquet(save_path)
            logger.info(f"Saved batch {batch_num + 1} data to {save_path}")
    df_ratings = (
        pd.DataFrame()
        .from_dict(data=boardgame_master_dict, orient="index")
        .reset_index(names="game_id")
    )
    df_ratings.to_parquet(save_path)
    logger.info(f"Saved final data to {save_path}")
    return df_ratings


def iterate_through_ratings_pages(
    boardgame_master_dict: dict,
    max_ratings_page: int,
    ratings_count_dict: dict,
    start_page: int,
    batch_saves: bool = False,
    save_path: str = None,
):
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
            if game_xml["id"] not in boardgame_master_dict:
                boardgame_master_dict[game_xml["id"]] = {}
            boardgame_master_dict[game_xml["id"]] = extract_ratings(
                game_dict=boardgame_master_dict[game_xml["id"]], game_xml=game_xml
            )
        if batch_saves and page_num % 30 == 0:
            df_ratings = (
                pd.DataFrame()
                .from_dict(data=boardgame_master_dict, orient="index")
                .reset_index(names="game_id")
            )
            df_ratings.to_parquet(save_path)
            logger.info(
                f"Saved ratings page {page_num} of {max_ratings_page} data to {save_path}"
            )
        elif page_num % 30 == 0:
            logger.info(f"Processed ratings page {page_num} of {max_ratings_page}")
        sleep(1)
    return boardgame_master_dict


def extract_basic_game_info(game_xml: bs4.element.Tag):
    logger.debug(f"Extracting basic game info for {game_xml['id']}")
    game_dict = {
        "game_id": game_xml["id"],
    }
    if game_xml.find("image") is not None:
        game_dict["thumbnail"] = game_xml.find("thumbnail").text
        game_dict["image"] = game_xml.find("image").text
    values_int = [
        "minplayers",
        "maxplayers",
        "playingtime",
        "minplaytime",
        "maxplaytime",
        "minage",
    ]
    for vals in values_int:
        if game_xml.find(vals) is not None:
            game_dict[vals] = game_xml.find(vals)["value"]
    link_categ = [
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
    for categ in link_categ:
        game_dict[categ] = [
            x["value"] for x in game_xml.find_all("link", {"type": categ})
        ]
    stats_float = ["stddev", "median", "averageweight"]
    for stat in stats_float:
        if game_xml.find(stat) is not None:
            game_dict[stat] = float(game_xml.find(stat)["value"])
    stats_int = [
        "owned",
        "trading",
        "wanting",
        "wishing",
        "numcomments",
        "numweights",
    ]
    for stat in stats_int:
        if game_xml.find(stat) is not None:
            game_dict[stat] = int(game_xml.find(stat)["value"])
    if game_xml.find("comments") is not None:
        game_dict["numratings"] = int(game_xml.find("comments")["totalitems"])
    else:
        game_dict["numratings"] = 0
    logger.debug(f"Successfully extracted basic game info for {game_xml['id']}")
    return game_dict


def extract_polls(game_dict: dict, game_xml: bs4.element.Tag):
    logger.debug(f"Extracting polls for {game_xml['id']}")
    for poll_name in ["suggested_playerage", "language_dependence"]:
        if poll_name == "suggested_playerage":
            raw_value_col = "value"
        elif poll_name == "language_dependence":
            raw_value_col = "level"
        poll = game_xml.find("poll", attrs={"name": poll_name})
        vote_count = int(poll.attrs["totalvotes"])
        if vote_count > 0:
            result_dict = {"total_votes": vote_count}
            cum_votes = 0
            suggested_prcnt = {}
            suggested_prcnt_col = "value"
            for result_val in poll.find("results").find_all("result"):
                num_votes = int(result_val["numvotes"])
                cum_votes += num_votes
                cum_prcnt = round(cum_votes / vote_count * 100)
                result_dict[result_val[raw_value_col]] = num_votes
                sugg_prcnt_val = result_val[suggested_prcnt_col]
                if cum_prcnt >= 75:
                    if "75 percent" not in suggested_prcnt:
                        suggested_prcnt["75 percent"] = sugg_prcnt_val
                    if "50 percent" not in suggested_prcnt:
                        suggested_prcnt["50 percent"] = sugg_prcnt_val
                    if "25 percent" not in suggested_prcnt:
                        suggested_prcnt["25 percent"] = sugg_prcnt_val
                elif cum_prcnt >= 50:
                    suggested_prcnt["50 percent"] = sugg_prcnt_val
                    if "25 percent" not in suggested_prcnt:
                        suggested_prcnt["25 percent"] = sugg_prcnt_val
                elif cum_prcnt >= 25:
                    suggested_prcnt["25 percent"] = sugg_prcnt_val
        else:
            result_dict = {}
            suggested_prcnt = {}
        game_dict[poll_name] = result_dict
        game_dict[f"{poll_name}_quartiles"] = suggested_prcnt
    logger.debug(f"Successfully extracted polls for {game_xml['id']}")
    return game_dict


def extract_poll_player_count(game_dict: dict, game_xml: bs4.element.Tag):
    logger.debug(f"Extracting player count poll for {game_xml['id']}")
    player_count_poll = game_xml.find("poll", attrs={"name": "suggested_numplayers"})
    result_dict = {"total_votes": int(player_count_poll.attrs["totalvotes"])}
    player_count_results = player_count_poll.find_all("results")
    game_dict["player_count_recs"] = {}
    for player_count in player_count_results:
        num_players = player_count.attrs["numplayers"]
        player_count_values = {
            x.attrs["value"]: int(x.attrs["numvotes"])
            for x in player_count.find_all("result")
        }
        play_count_rec = max(player_count_values, key=player_count_values.get)
        if play_count_rec in game_dict["player_count_recs"]:
            game_dict["player_count_recs"][play_count_rec].append(num_players)
        else:
            game_dict["player_count_recs"][play_count_rec] = [num_players]
        result_dict[num_players] = player_count_values
        result_dict[num_players]["total_votes"] = sum(
            int(x.attrs["numvotes"]) for x in player_count.find_all("result")
        )
    game_dict["suggested_numplayers"] = result_dict
    logger.debug(f"Successfully extracted player count poll for {game_xml['id']}")
    return game_dict


def extract_version_info(game_dict: dict, game_xml: bs4.element.Tag):
    logger.debug(f"Extracting version info for {game_xml['id']}")
    version_items = game_xml.find_all("item", attrs={"type": "boardgameversion"})
    version_list = []
    for vrs in version_items:
        try:
            version_dict = {
                "version_id": int(vrs["id"]),
                "width": round(float(vrs.find("width")["value"])),
                "length": round(float(vrs.find("length")["value"])),
                "depth": round(float(vrs.find("depth")["value"])),
                "year_published": round(float(vrs.find("yearpublished")["value"])),
            }
            if vrs.find("thumbnail") is not None:
                version_dict["thumbnail"] = vrs.find("thumbnail").text
                version_dict["image"] = vrs.find("image").text
            if vrs.find("link", attrs={"type": "language"}) is not None:
                version_dict["language"] = vrs.find("link", attrs={"type": "language"})[
                    "value"
                ].lower()
            if vrs.find("name", attrs={"type": "primary"}) is not None:
                version_dict["version_nickname"] = vrs.find(
                    "name", attrs={"type": "primary"}
                )["value"]
            if version_dict["width"] > 0:
                version_list.append(version_dict)
        except TypeError as e:
            logger.error(
                f"TypeError processing version for game ID {game_xml['id']}: {str(e)}"
            )
            raise
    if len(version_list) > 0:
        game_dict["versions"] = version_list
    logger.debug(f"Successfully extracted version info for {game_xml['id']}")
    return game_dict


def extract_ratings(game_dict: dict, game_xml: bs4.element.Tag):
    ratings_list = game_xml.find_all("comment")
    for rating in ratings_list:
        # round the rating to the nearest 0.5
        rating_round = str(round(2 * float(rating["rating"])) / 2)
        if rating_round not in game_dict:
            game_dict[rating_round] = [rating["username"]]
        else:
            game_dict[rating_round].append(rating["username"])
    return game_dict
