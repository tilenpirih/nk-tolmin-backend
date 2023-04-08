from bs4 import BeautifulSoup
from dotenv import load_dotenv
import requests
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from db import db
from urllib.parse import urlparse, parse_qs, quote
from urllib.request import urlretrieve
from schema import Club, Season
from PIL import Image
from datetime import date

load_dotenv()


def getAllClubs():
    print("getting all clubs")
    for season in Season.select():
        print(season.clubs_link)
        getClubsFromSeason(season.clubs_link)

def getClubsFromSeason(url):
    print(url)
    result = requests.get(url)
    result.encoding = result.apparent_encoding
    doc = BeautifulSoup(result.text, "html.parser")
    IDMenu = parse_qs(urlparse(url).query)['id_menu'][0]
    for row in doc.find_all(
            "div", {"class": "col-lg-3 col-md-3 col-sm-4 col-xs-6 text-center"}):
        clubID = parse_qs(urlparse(row.a['href']).query)['id_kluba'][0]
        response = addClub(clubID, url[-4:], IDMenu)
        if response is False:
            clubName = row.a.h4.text.strip()
            Club.create(
                club_id=clubID,
                name=clubName,
                original_logo_path=None,
                small_logo_path=None
            )
            print(f'added: {clubName} - lazy add')
    print(f"finished season {url[-4:]}")


def findClub(clubID):
    year = date.today().year
    while year >= 2010:
        print(year)
        result = requests.get(
            f'https://www.nzs.si/tekmovanja/?action=klub&id_kluba={clubID}&id_menu=721&id_sezone={year}')
        result.encoding = result.apparent_encoding
        doc = BeautifulSoup(result.text, "html.parser")
        if doc.find("div", {"class": "col-md-8 col-xs-12"}) is not None:
            print("club found")
            return doc

        result = requests.get(
            f'https://www.nzs.si/tekmovanja/?action=klub&id_kluba={clubID}&id_menu=581&id_sezone={year}')
        result.encoding = result.apparent_encoding
        doc = BeautifulSoup(result.text, "html.parser")
        if doc.find("div", {"class": "col-md-8 col-xs-12"}) is not None:
            print("club found")
            return doc
        year -= 1
    return None


def addClub(clubID, seasonID, IDMenu):
    club = Club.get_or_none(club_id=clubID)
    if club is not None:
        print("club already exists")
        return
    result = requests.get(
        f'https://www.nzs.si/tekmovanja/?action=klub&id_kluba={clubID}&id_menu={IDMenu}&id_sezone={seasonID}')
    result.encoding = result.apparent_encoding
    doc = BeautifulSoup(result.text, "html.parser")
    if doc.find("div", {"class": "col-md-8 col-xs-12"}) is None:
        doc = findClub(clubID)
        if doc is None:
            return False
    clubName = doc.find("table").h3.text.strip()
    logo = doc.find("div", {"class": "col-md-4 col-xs-12 text-center"}).img
    originalLogoUrl = None
    smallLogoUrl = None
    if logo is not None:
        nzsLogoUrl = 'https://www.nzs.si' + quote(logo['src'][2:])
        urlretrieve(nzsLogoUrl, f'./assets/grbi/original/{clubName}.png')
        image = Image.open(f'./assets/grbi/original/{clubName}.png')
        image = image.resize((72, 72))
        image.save(f'./assets/grbi/72/{clubName}.png')
        logoName = quote(clubName)
        originalLogoUrl = f"assets/grbi/original/{logoName}.png"
        smallLogoUrl = f"assets/grbi/72/{logoName}.png"
    Club.create(
        club_id=clubID,
        name=clubName,
        original_logo_path=originalLogoUrl,
        small_logo_path=smallLogoUrl
    )

    print(f'added: {clubName}')
# getAllClubs()
# getClubsFromSeason(seasons[6])
# addClub(693, '2022')
