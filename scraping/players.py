import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from schema import Player, PlayerCompetition, Season, PlayerSeason
from playhouse.shortcuts import model_to_dict
import requests
import re
from urllib.parse import parse_qs
from urllib.parse import urlparse
from bs4 import BeautifulSoup

scrapped_players = []


def getAllPlayers():
    global scrapped_players
    query = Season.select(Season.statistics_link, Season.season_id).where(
        Season.statistics_link.is_null(False), Season.statistics_link != "")
    for season in query:
        print(season.statistics_link, season.season_id)
        getPlayersFromSeason(season.season_id, season.statistics_link)
    scrapped_players = []


def getPlayersFromSeason(season_id, url):
    result = requests.get(url)
    result.encoding = result.apparent_encoding
    doc = BeautifulSoup(result.text, "html.parser")

    for row in doc.find_all("tr", {"class": "hand"}):
        player_id = int(
            re.sub("[^0-9]", "", parse_qs(urlparse(row['onclick']).query)['id_igralca'][0]))

        player_name = re.sub("[*]", "", row.td.text).strip().replace(u'\xa0', ' ')
        print(player_id, player_name)
        
        if player_id not in scrapped_players:
            print("Scraping player: "+player_name)
            addPlayer(player_id)
            getPlayerCompetitions(player_id)
            scrapped_players.append(player_id)
            print("Finished scraping player: "+player_name)
        else:
            print("Player already scrapped: " +
                  player_name + " " + str(player_id))
        if not PlayerSeason.select().where(PlayerSeason.player_id == player_id, PlayerSeason.season_id == season_id).exists():
            PlayerSeason.insert(
                player_id=player_id,
                season_id=season_id,
            ).execute()

def getPlayerCompetitions(player_id):
    url = "https://www.nzs.si/tekmovanja/?action=igralecStat&id_igralca=" + \
        str(player_id)
    result = requests.get(url)
    result.encoding = result.apparent_encoding
    doc = BeautifulSoup(result.text, "html.parser")
    for row in doc.find("tbody").find_all("tr"):
        com_id = parse_qs(urlparse(row['onclick']).query)['id_tekmovanja'][0]
        getPlayerCompetition(player_id, com_id)


def addPlayer(player_id):
    url = "https://www.nzs.si/tekmovanja/?action=igralecStat&id_igralca=" + \
        str(player_id)
    result = requests.get(url)
    result.encoding = result.apparent_encoding
    doc = BeautifulSoup(result.text, "html.parser")
    full_name = re.sub("[0-9]", "", doc.find("h1").text).strip().replace(u'\xa0', ' ')
    year_of_birth = int(doc.find(text="Leto rojstva:").parent.parent.find_all("td")[1].text.strip())
    league_statistic = []
    table = doc.find(
        "table", {"class": "table Tabela1 table-hover dataTablesSort"})
    for row in table.tbody.find_all("tr"):
        arr = row.find_all("td")
        competition_id = parse_qs(urlparse(row['onclick']).query)[
            'id_tekmovanja'][0]
        league_name = arr[0].text.strip()
        num_performances = int(arr[1].text.strip())
        goals = int(arr[2].text.strip())
        yellow_cards = int(arr[3].text.strip())
        red_cards = int(arr[4].text.strip())
        minutes = int(re.sub("[^0-9]", "", arr[5].text.strip()))
        club = arr[6].text.strip()
        league_statistic.append({
            "competition_id": competition_id,
            "league_name": league_name,
            "num_performances": num_performances,
            "goals": goals,
            "yellow_cards": yellow_cards,
            "red_cards": red_cards,
            "minutes": minutes,
            "club": club
        })
    sum_competitions = []
    tfoot = table.tfoot.find_all("tr")
    del tfoot[0]
    for row in tfoot:
        arr = row.find_all("td")
        competition_name = arr[0].text.strip()
        num_performances = int(arr[1].text.strip())
        goals = int(arr[2].text.strip())
        yellow_cards = int(arr[3].text.strip())
        red_cards = int(arr[4].text.strip())
        minutes = int(re.sub("[^0-9]", "", arr[5].text.strip()))
        sum_competitions.append({
            "competition_name": competition_name,
            "num_performances": num_performances,
            "goals": goals,
            "yellow_cards": yellow_cards,
            "red_cards": red_cards,
            "minutes": minutes,
        })
    Player.insert(
        player_id=player_id,
        full_name=full_name,
        year_of_birth=year_of_birth,
        img_path=None,
        league_statistic=league_statistic,
        sum_competitions=sum_competitions,
        description=None,
    ).on_conflict(
        conflict_target=[Player.player_id],
        preserve=[
            Player.league_statistic,
            Player.sum_competitions,
        ]).execute()


def getPlayerCompetition(player_id, competition_id):
    # uncomment this line for debugging
    # print(player_id, competition_id)
    url = "https://www.nzs.si/tekmovanja/?action=igralec&id_igralca=" + \
        str(player_id) + "&id_tekmovanja=" + str(competition_id)
    result = requests.get(url)
    result.encoding = result.apparent_encoding
    doc = BeautifulSoup(result.text, "html.parser")
    table = doc.find("table", {"class": "table Tabela1 table-hover"})
    matches = []
    krogIndex = tekmaIndex = stausIndex = goliIndex = rumeniIndex = rdeciIndex = minuteIndex = klubIndex = -1
    for index, row in enumerate(doc.find("thead").tr.find_all("th")):
        text = row.text
        if text == 'Krog':
            krogIndex = index
        elif text == 'Tekma':
            tekmaIndex = index
        elif text == 'Status':
            stausIndex = index
        elif text == 'Goli':
            goliIndex = index
        elif text == 'Rumeni':
            rumeniIndex = index
        elif text == 'Rdeči':
            rdeciIndex = index
        elif text == 'Minute':
            minuteIndex = index
        elif text == 'Klub':
            klubIndex = index
    for row in table.find_all("tr", {"class": "hand"}):
        arr = row.find_all("td")
        competition_name = arr[0].text.strip()
        match_id = int(re.sub(
            "[^0-9]", "", parse_qs(urlparse(row['onclick']).query)['id_tekme'][0]))
        match_num = None if krogIndex == -1 else int(arr[krogIndex].text)
        match_name = None if tekmaIndex == 1 else re.sub(
            ' +', ' ', arr[tekmaIndex].text)
        status = None if stausIndex == -1 else arr[stausIndex].text
        goals = None if goliIndex == 1 else len(arr[goliIndex].find_all("img"))
        yellow_cards = None if rumeniIndex == 1 else len(
            arr[rumeniIndex].find_all("img"))
        red_cards = None if rdeciIndex == 1 else len(
            arr[rdeciIndex].find_all("img"))
        minutes = None if minuteIndex == 1 else int(arr[minuteIndex].text)
        club = None if klubIndex == -1 else arr[klubIndex].text.strip()
        matches.append({
            "match_id": match_id,
            "competition_name": competition_name,
            "match_num": match_num,
            "match_name": match_name,
            "status": status,
            "goals": goals,
            "yellow_cards": yellow_cards,
            "red_cards": red_cards,
            "minutes": minutes,
            "club": club
        })
    tfoot = table.tfoot.find_all("tr")
    del tfoot[0]
    sum_competitions = []
    if len(tfoot) != 0 and len(tfoot[0].find_all("td")) == 7:
        for row in tfoot:
            arr = row.find_all("td")
            league_name = arr[0].text.strip()
            num_performances = int(arr[1].text.strip())
            goals = int(arr[2].text.strip())
            yellow_cards = int(arr[3].text.strip())
            red_cards = int(arr[4].text.strip())
            minutes = int(re.sub("[^0-9]", "", arr[5].text.strip()))
            club = arr[6].text.strip()
            sum_competitions.append({
                "league_name": league_name,
                "num_performances": num_performances,
                "goals": goals,
                "yellow_cards": yellow_cards,
                "red_cards": red_cards,
                "minutes": minutes,
                "club": club
            })
    PlayerCompetition.insert(
        id=str(player_id)+str(competition_id),
        player_id=player_id,
        competition_id=competition_id,
        matches=matches,
        sum_competitions=sum_competitions
    ).on_conflict(
        conflict_target=[PlayerCompetition.id],
        preserve=[
            PlayerCompetition.matches,
            PlayerCompetition.sum_competitions,
        ]).execute()


# getAllPlayers()
# getPlayersFromSeason(2023,'https://www.nzs.si/tekmovanja/default.asp?action=klub&id_menu=721&id_kluba=277&prikaz=5&id_sezone=2023')
# addPlayer(81809, 2023)
# getPlayerCompetition(81809, 624)
# getPlayerCompetition(63260, 232)
# updatePlayerInfo(81809)
# updateAllPlayers()
