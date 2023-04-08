import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from schema import Season, StatsPlayer, StatsPlayerSeason, Player
from playhouse.shortcuts import model_to_dict
import requests
import re
from urllib.parse import parse_qs
from urllib.parse import urlparse
from bs4 import BeautifulSoup


def getAllStats():
    global scrapped_players
    query = Season.select(Season.statistics_link, Season.season_id).where(
        Season.statistics_link.is_null(False), Season.statistics_link != "")
    for season in query:
        print(season.statistics_link, season.season_id)
        getStatsFromSeason(season.season_id, season.statistics_link)


def getStatsFromSeason(season_id, url):
    result = requests.get(url)
    result.encoding = result.apparent_encoding
    doc = BeautifulSoup(result.text, "html.parser")
    table = doc.find_all("tr", {"class": "hand"})
    for row in table:
        player_id = int(
            re.sub("[^0-9]", "", parse_qs(urlparse(row['onclick']).query)['id_igralca'][0]))
        arr = row.find_all("td")
        goals = int(arr[1].text.strip())
        yellow_cards = int(arr[2].text.strip())
        red_cards = int(arr[3].text.strip())
        minutes = int(arr[4].text.strip())
        num_appearances = int(arr[5].text.strip())
        stats_player_id = str(player_id)+str(season_id)

        StatsPlayer.insert(
            id=stats_player_id,
            player_id=player_id,
            season_id=season_id,
            goals=goals,
            yellow_cards=yellow_cards,
            red_cards=red_cards,
            minutes=minutes,
            num_appearances=num_appearances,
        ).on_conflict(
            conflict_target=[StatsPlayer.id],
            preserve=[
                StatsPlayer.goals,
                StatsPlayer.yellow_cards,
                StatsPlayer.red_cards,
                StatsPlayer.minutes,
                StatsPlayer.num_appearances,
            ]).execute()

        if not StatsPlayerSeason.select().where(StatsPlayerSeason.season_id == season_id, StatsPlayerSeason.stats_player_id == stats_player_id).exists():
            StatsPlayerSeason.insert(
                season_id=season_id,
                stats_player_id=stats_player_id,
            ).execute()


# getAllStats()
# getStatsFromSeason(
#     2022, 'https://www.nzs.si/tekmovanja/default.asp?action=klub&id_menu=721&id_kluba=277&prikaz=5&id_sezone=2022')
