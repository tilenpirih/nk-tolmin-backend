import requests
import re
from bs4 import BeautifulSoup
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from urllib.parse import urlparse, parse_qs, quote
# from urllib.request import urlretrieve
from schema import Season, Club, Match
from datetime import datetime
from peewee import fn

def getAllMatches():
    print("Getting all matches")
    for row in Season.select():
        getMatchesFromSeason(row.season_link)


def getMatchesFromSeason(url):
    print(url)
    result = requests.get(url)
    result.encoding = result.apparent_encoding
    doc = BeautifulSoup(result.text, "html.parser")
    for row in doc.find("table").tbody.find_all("tr", {"class": "klub_all"}):
        if row.find_all("td", {"class": "bold"})[0].text.lower().find("tolmin") != -1 or row.find_all("td", {"class": "bold"})[1].text.lower().find("tolmin") != -1:
            if not row.span.text.strip() == "PRELOŽENO":
                addMatch(parse_qs(urlparse(row.find("a", {"class": "gumb"})["href"]).query)[
                    "id_tekme"][0])
    print("Season finished")


def getMatchSeasonID(matchID):
    print("getting season ID: " + str(matchID))
    result = requests.get(
        f"https://www.nzs.si/tekmovanja/?action=tekma&id_menu=237&id_tekme={matchID}&prikaz=7")
    result.encoding = result.apparent_encoding
    doc = BeautifulSoup(result.text, "html.parser")
    header = doc.find(
        "div", {"class": "text-center header"}).text.strip().split('|')
    matchDate = header[2].strip().split(" ")[0]
    for row in doc.find("table", {"class": "table table-hover table-striped"}).find_all("tr"):
        arr = row.find_all("td")
        if matchDate in arr[2].text.strip():
            return int("20"+arr[0].text.strip()[-2:])
    return None


def addMatch(matchID):
    print("syncing match: " + str(matchID))
    result = requests.get(
        f"https://www.nzs.si/tekmovanja/?action=tekma&id_tekme={matchID}")
    result.encoding = result.apparent_encoding
    doc = BeautifulSoup(result.text, "html.parser")
    # getting season ID
    try:
        seasonID = int(
            "20"+doc.find("div", {"class": "menuBanner"}).text.strip()[-2:])
    except:
        seasonID = getMatchSeasonID(matchID)
    # getting matchNum, match location and match date
    header = doc.find(
        "div", {"class": "text-center header"}).text.strip().split('|')
    matchNum = re.sub("[^0-9]", "", header[0])
    location = header[1].strip()
    matchDate = header[2]
    matchDateArr = matchDate.strip().split(' ')
    matchDateIso = None
    if len(matchDateArr) == 3:
        matchDateIso = datetime.strptime(
            matchDateArr[0]+matchDateArr[2], "%d.%m.%Y%H.%M").isoformat()
    elif len(matchDateArr) == 1:
        matchDateIso = datetime.strptime(
            matchDateArr[0], "%d.%m.%Y").isoformat()
    # deleting all matches from this day (bug on NZS.si that sometimes same match have different ID)
    Match.delete().where(Match.match_date == matchDateIso[:10]+"T00:00:00").execute()
    # getting clubs name and ID
    clubs = doc.findAll("div", {"class": "klub"})
    homeTeamName = clubs[0].text.strip()
    roadTeamName = clubs[1].text.strip()
    clubs = doc.find(text="LESTVICA").parent.parent.parent.parent
    homeTeamID = int(parse_qs(
        urlparse(clubs.find(text=homeTeamName).parent["href"]).query)["id_kluba"][0])
    roadTeamID = int(parse_qs(
        urlparse(clubs.find(text=roadTeamName).parent["href"]).query)["id_kluba"][0])
    # getting match score
    scoresArr = doc.find(
        "div", {"class": "rezultat"}).find_all("span")
    finishedMatch = False
    homeTeamGoals = roadTeamGoals = None
    if scoresArr[0].text.isnumeric() and scoresArr[1].text.isnumeric():
        finishedMatch = True
        homeTeamGoals = int(scoresArr[0].text)
        roadTeamGoals = int(scoresArr[1].text)

    # getting referees, delegat, numPeople
    arr = doc.find("div", {"class": "sodniki"}).find_all("tr")
    referees = arr[0].find_all("td")[1].text.strip()
    delegat = arr[1].find_all("td")[1].text.strip()
    numPeopleText = arr[2].find_all("td")[1].text.strip()
    numPeople = int(numPeopleText) if numPeopleText.isnumeric() else None

    if not finishedMatch:
        Match.insert(
            match_id=matchID,
            match_num=matchNum,
            finished_match=finishedMatch,
            home_team_goals=None,
            road_team_goals=None,
            location=location,
            scores=None,
            match_date=matchDateIso,
            delegat=delegat,
            referees=referees,
            num_of_people=None,
            events=None,
            home_team_coach=None,
            road_team_coach=None,
            players=None,
            home_team_id=homeTeamID,
            road_team_id=roadTeamID,
            season_id=seasonID,
        ).on_conflict(
            conflict_target=[Match.match_id],
            preserve=[
                Match.match_num,
                Match.finished_match,
                Match.home_team_goals,
                Match.road_team_goals,
                Match.location,
                Match.scores,
                Match.match_date,
                Match.delegat,
                Match.referees,
                Match.num_of_people,
                Match.events,
                Match.home_team_coach,
                Match.road_team_coach,
                Match.players,
                Match.home_team_id,
                Match.road_team_id,
                Match.season_id
            ]
        ).execute()
        print("UNFINISHED MATCH SYNCED!!!")
        return
    # getting players
    tables = doc.find_all("table", {"class": "Tabela1"})
    homeTeam = []
    roadTeam = []
    if len(tables[0].tbody.find_all("tr")) != 0:
        firstEleven = True
        for row in tables[0].tbody.find_all("tr"):
            if not row.has_attr("class"):
                firstEleven = False
                continue
            arrRow = row.find_all("td")
            homeTeam.append({"num": int(arrRow[0].text.strip()), "full_name": arrRow[1].text.strip(),
                             "special": arrRow[2].text.strip(), "first_eleven": firstEleven})

    if len(tables[1].tbody.find_all("tr")) != 0:
        firstEleven = True
        for row in tables[1].tbody.find_all("tr"):
            if not row.has_attr("class"):
                firstEleven = False
                continue
            arrRow = row.find_all("td")
            roadTeam.append({"num": int(arrRow[0].text.strip()), "full_name": arrRow[1].text.strip(),
                             "special": arrRow[2].text.strip(), "first_eleven": firstEleven})
    players = {"home_team": homeTeam, "road_team": roadTeam}

    homeTeamCoach = tables[2].td.text.strip()
    roadTeamCoach = tables[3].td.text.strip()

    # get scores
    scores = []
    for row in tables[5].tbody.find_all("tr"):
        arr = row.find_all("td")
        eventText=arr[1].text.strip()
        playerFullName = re.sub("[\(\[].*?[\)\]]", "", eventText).strip()
        # print(re.sub("[\(\[].*?[\)\]]", "", playerFullName))
        playerClubId = None
        for player in homeTeam:
            if player["full_name"].lower() == playerFullName.lower():
                playerClubId = homeTeamID
                break
        if playerClubId == None:
            for player in roadTeam:
                if player["full_name"].lower() == playerFullName.lower():
                    playerClubId = roadTeamID
                    break
        score = arr[2].text.strip()
        minute = int(re.sub("[^0-9]", "", arr[3].text.strip()))
        scores.append({"club_id": playerClubId, "player_name": eventText,
                      "score": score, "minute": minute})

    # get events
    events = []
    for row in tables[6].tbody.find_all("tr"):
        arr = row.find_all("td")
        event = None
        eventClubId = None
        imageText = arr[1].img["src"]
        eventText = " ".join(arr[2].text.strip().split())
        if 'menjava' in imageText:
            event = 'change_player'
            lastNames = eventText.split('/')
            lastNames[0] = lastNames[0].strip()
            lastNames[1] = lastNames[1].strip()
            if any(lastNames[0] in d['full_name'] for d in homeTeam) and any(lastNames[1] in d['full_name'] for d in homeTeam):
                eventClubId = homeTeamID
            if eventClubId == None and any(lastNames[0] in d['full_name'] for d in roadTeam) and any(lastNames[1] in d['full_name'] for d in roadTeam):
                eventClubId = roadTeamID
            if eventClubId == None:
                if any(lastNames[0] in d['full_name'] for d in homeTeam) or any(lastNames[1] in d['full_name'] for d in homeTeam):
                    eventClubId = homeTeamID
                else:
                    eventClubId = roadTeamID
        else:
            if 'rumeni' in imageText:
                event = 'yellow_card'
            elif 'rdeci' in imageText:
                event = 'red_card'
            fullName = arr[2].text.strip()
            if any(d['full_name'] == fullName for d in homeTeam):
                eventClubId = homeTeamID
            if eventClubId == None and any(d['full_name'] == fullName for d in roadTeam):
                eventClubId = roadTeamID
        minute = int(re.sub("[^0-9]", "", arr[3].text))
        # print(event, eventClubId,eventText, minute)
        events.append({"clubId": eventClubId, "event": event,
                      "event_text": eventText, "minute": minute})
    Match.insert(
        match_id=matchID,
        match_num=matchNum,
        finished_match=finishedMatch,
        home_team_goals=homeTeamGoals,
        road_team_goals=roadTeamGoals,
        location=location,
        scores=scores,
        match_date=matchDateIso,
        delegat=delegat,
        referees=referees,
        num_of_people=numPeople,
        events=events,
        home_team_coach=homeTeamCoach,
        road_team_coach=roadTeamCoach,
        players=players,
        home_team_id=homeTeamID,
        road_team_id=roadTeamID,
        season_id=seasonID,
    ).on_conflict(
        conflict_target=[Match.match_id],
        preserve=[
            Match.match_num,
            Match.finished_match,
            Match.home_team_goals,
            Match.road_team_goals,
            Match.location,
            Match.scores,
            Match.match_date,
            Match.delegat,
            Match.referees,
            Match.num_of_people,
            Match.events,
            Match.home_team_coach,
            Match.road_team_coach,
            Match.players,
            Match.home_team_id,
            Match.road_team_id,
            Match.season_id
        ]
    ).execute()

    print("MATCH SYNCED!!!")
    # print(matchID),
    # print(scoresJSON),
    # print(matchNum)
    # print(location)
    # print(matchDateIso),
    # print(delegat),
    # print(referees),
    # print(numPeople),
    # print(eventsJSON),
    # print([homeTeamCoach, roadTeamCoach]),
    # print(players),
    # print(homeTeamID),
    # print(roadTeamID),
    # print(seasonID)


# print(len(matchDate.strip().split(' ')))
# print(header[0][0])

# def getSeasonInfo(clubID):
#     url = f"https://www.nzs.si/tekmovanja/default.asp?action=klub&id_kluba={clubID}&id_menu=721"
#     result = requests.get(url)
#     result.encoding = result.apparent_encoding
#     doc = BeautifulSoup(result.text, "html.parser")
#     clubName = doc.find("h3").text
#     print(doc.find_all("h3"))
#     Club.create(club_id=clubID, name=clubName)
#     print(f'added: {clubName}')


# getAllMatches()
# getMatchesFromSeason(
#     "https://www.nzs.si/tekmovanja/default.asp?id_menu=237&id_sezone=2016")
# addMatch(28848)
# addMatch(63553)
# addMatch(368837)
# getMatchesFromSeason("https://www.nzs.si/tekmovanja/default.asp?id_menu=300&id_sezone=2023")
