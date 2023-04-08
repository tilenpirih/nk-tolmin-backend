import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from schema import Season, ScoreboardSeason, ClubScoreboard, Club
from playhouse.shortcuts import model_to_dict
import requests
import re
from urllib.parse import parse_qs
from urllib.parse import urlparse
from bs4 import BeautifulSoup


def getAllScoreboards():
    global scrapped_players
    query = Season.select(Season.scoreboard_link, Season.season_id).where(
        Season.scoreboard_link.is_null(False), Season.scoreboard_link != "")
    for season in query:
        print(season.season_id, season.scoreboard_link)
        getScoreboardFromSeason(season.season_id, season.scoreboard_link)

def getScoreboardFromSeason(season_id, url):
    result = requests.get(url)
    result.encoding = result.apparent_encoding
    doc = BeautifulSoup(result.text, "html.parser")
    table = doc.find(
        "table", {"class": "table Tabela1 table-hover table-striped"})
    for row in table.find_all("tr", {"class": "hand"}):
        arr = row.find_all("td")
        arrLen = len(arr)
        club_id = int(parse_qs(urlparse(row['onclick']).query)[
                      'id_kluba'][0].strip())
        club_position = int(re.sub("[^0-9]", "", arr[0].text))
        club_name = arr[arrLen-8].text.strip()
        num_matches = int(arr[arrLen-7].text.strip())
        wins = int(arr[arrLen-6].text.strip())
        draws = int(arr[arrLen-5].text.strip())
        losses = int(arr[arrLen-4].text.strip())
        points_get_lost = arr[arrLen-3].text.strip()
        points_difference = int(arr[arrLen-2].text.strip())
        points = int(arr[arrLen-1].text.strip())
        club_scoreboard_id = str(club_id)+str(season_id)
        if not Club.select().where(Club.club_id == club_id).exists():
            print("club doesn't exist, adding club")
            Club.insert(
                club_id=club_id,
                name=club_name,
            ).execute()

        ClubScoreboard.insert(
            id=club_scoreboard_id,
            club_id=club_id,
            club_position=club_position,
            num_matches=num_matches,
            wins=wins,
            draws=draws,
            losses=losses,
            points_get_lost=points_get_lost,
            points_difference=points_difference,
            points=points,
        ).on_conflict(
            conflict_target=[ClubScoreboard.id],
            preserve=[
                ClubScoreboard.club_position,
                ClubScoreboard.num_matches,
                ClubScoreboard.wins,
                ClubScoreboard.draws,
                ClubScoreboard.losses,
                ClubScoreboard.points_get_lost,
                ClubScoreboard.points_difference,
                ClubScoreboard.points,
            ]).execute()
        if not ScoreboardSeason.select().where(ScoreboardSeason.season_id == season_id, ScoreboardSeason.club_scoreboard_id == club_scoreboard_id).exists():
            ScoreboardSeason.insert(
                season_id=season_id,
                club_scoreboard_id=club_scoreboard_id,
            ).execute()


# getScoreboardFromSeason(
#     2021, 'https://www.nzs.si/tekmovanja/default.asp?action=lestvica&id_menu=301&id_sezone=2021')
# getAllScoreboards()
