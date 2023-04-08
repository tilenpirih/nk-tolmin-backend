# from app import db
from schema import *
from seasons import createSeasons

from scraping.clubs import getAllClubs
from scraping.players import getAllPlayers
from scraping.matches import getAllMatches
from scraping.scoreboard import getAllScoreboards
from scraping.statistics import getAllStats
from scraping.articles import getAllArticles


createSeasons()
getAllClubs()
getAllPlayers()
getAllMatches()
getAllScoreboards()
getAllStats()
getAllArticles()

User.insert(
        username='admin',
        name='name admin',
        surname='admin surname',
        password=generate_password_hash('admin')
    ).on_conflict_ignore().execute()

YoungerTeam.get_or_create(id='U7', defaults={'content': 'Igralci U7'})
YoungerTeam.get_or_create(id='U9', defaults={'content': 'Igralci U9'})
YoungerTeam.get_or_create(id='U11', defaults={'content': 'Igralci U11'})
YoungerTeam.get_or_create(id='U13', defaults={'content': 'Igralci U13'})
YoungerTeam.get_or_create(id='U15', defaults={'content': 'Igralci U15'})
YoungerTeam.get_or_create(id='U17', defaults={'content': 'Igralci U17'})
YoungerTeam.get_or_create(id='U19', defaults={'content': 'Igralci U19'})

