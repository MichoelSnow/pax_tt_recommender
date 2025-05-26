from bs4 import BeautifulSoup
import json
import requests
from zipfile import ZipFile
from io import BytesIO
from time import sleep
import pandas as pd
from datetime import datetime
import math
import bs4

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service


def get_driver_and_cookies():
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
    selenium_cookies = driver.get_cookies()
    for cookie in selenium_cookies:
        cookies[cookie["name"]] = cookie["value"]
    return cookies


def get_boardgame_list(cookies: dict):
    bg_list_pg_url = "https://boardgamegeek.com/data_dumps/bg_ranks"
    resp = requests.get(bg_list_pg_url, cookies=cookies)
    soup = BeautifulSoup(resp.content, "html.parser")
    bg_list_url = soup.find("div", {"id": "maincontent"})("a")[0]["href"]
    bg_list_zip = requests.get(bg_list_url)
    with ZipFile(BytesIO(bg_list_zip.content)) as archive:
        with archive.open("boardgames_ranks.csv") as csv:
            df_bg_list = pd.read_csv(csv)
            df_bg_list["queried_at_utc"] = (
                datetime.now().replace(microsecond=0).isoformat()
            )
            return df_bg_list


def get_boardgame_raw_data(boardgame_df: pd.DataFrame):
    boardgame_ids = boardgame_df["id"].tolist()
    boardgame_master_dict = {}
    batch_size = 3
    for batch_num in range(math.ceil(len(boardgame_ids) / batch_size)):
        batch_ids = boardgame_ids[batch_num * batch_size : (batch_num + 1) * batch_size]
        batch_ids = [str(x) for x in batch_ids]
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
            if game_dict["numratings"] > 0:
                game_dict = extract_ratings(game_dict=game_dict, game_xml=game_xml)
            ratings_count_dict[game_dict["game_id"]] = game_dict["numratings"]
            max_ratings_page = math.ceil(max(ratings_count_dict.values()) / 100)
            boardgame_master_dict[game_dict["game_id"]] = game_dict
        for page_num in range(2, max_ratings_page + 1):
            print(page_num)
            # Only grab the pages for games which have enough ratings to be on the page num
            batch_ids_ratings = [
                str(x)
                for x in ratings_count_dict.keys()
                if math.ceil(ratings_count_dict[x] / 100) >= page_num
            ]
            bg_rating_url = f"https://www.boardgamegeek.com/xmlapi2/thing?type=boardgame&ratingcomments=1&pagesize=100&page={page_num}&id={','.join(batch_ids_ratings)}"
            bgg_rating_response = requests.get(bg_rating_url)
            soup_rating_xml = BeautifulSoup(bgg_rating_response.content, "xml")
            ratings_xml_list = soup_rating_xml.find_all(
                "item", attrs={"type": "boardgame"}
            )
            for game_xml in ratings_xml_list:
                game_dict = boardgame_master_dict[game_xml["id"]]
                boardgame_master_dict[game_dict["game_id"]] = extract_ratings(
                    game_dict=game_dict, game_xml=game_xml
                )
        break
    return list(boardgame_master_dict.values())


def extract_basic_game_info(game_xml: bs4.element.Tag):
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
    return game_dict


def extract_polls(game_dict: dict, game_xml: bs4.element.Tag):
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
    return game_dict


def extract_poll_player_count(game_dict: dict, game_xml: bs4.element.Tag):
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
    return game_dict


def extract_version_info(game_dict: dict, game_xml: bs4.element.Tag):
    version_items = game_xml.find_all("item", attrs={"type": "boardgameversion"})
    version_list = []
    for vrs in version_items:
        version_dict = {
            "version_id": int(vrs["id"]),
            "version_nickname": vrs.find("name", attrs={"type": "primary"})["value"],
            "width": round(float(vrs.find("width")["value"])),
            "length": round(float(vrs.find("length")["value"])),
            "depth": round(float(vrs.find("depth")["value"])),
            "year_published": round(float(vrs.find("yearpublished")["value"])),
            "language": vrs.find("link", attrs={"type": "language"})["value"].lower(),
        }
        if vrs.find("thumbnail") is not None:
            version_dict["thumbnail"] = vrs.find("thumbnail").text
            version_dict["image"] = vrs.find("image").text
        if version_dict["width"] > 0:
            version_list.append(version_dict)
    if len(version_list) > 0:
        game_dict["versions"] = version_list
    return game_dict


def extract_ratings(game_dict: dict, game_xml: bs4.element.Tag):
    ratings_list = game_xml.find_all("comment")
    if "ratings" not in game_dict:
        game_dict["ratings"] = {}
    for rating in ratings_list:
        # round the rating to the nearest 0.5
        rating_round = round(2 * float(rating["rating"])) / 2
        if rating_round not in game_dict["ratings"]:
            game_dict["ratings"][rating_round] = [rating["username"]]
        else:
            game_dict["ratings"][rating_round].append(rating["username"])
    return game_dict
