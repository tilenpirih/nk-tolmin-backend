from flask_restful import Resource
from playhouse.shortcuts import model_to_dict
import os
import sys
from flask import request
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from schema import Season, Sync
# from time import sleep
from peewee import fn
from scraping.matches import getMatchesFromSeason
from scraping.clubs import getClubsFromSeason
from scraping.players import getPlayersFromSeason
from scraping.scoreboard import getScoreboardFromSeason
from scraping.statistics import getStatsFromSeason
from sync import queue
from datetime import datetime

class GetSeasons(Resource):
    def get(self):
        query = [model_to_dict(row) for row in Season.select().order_by(Season.season_id.desc())]
        return query
    
class UpdateSeason(Resource):
    def post(self):
        data = request.get_json()
        season = Season.get(Season.season_id == data["season_id"])
        season.season_link = data["season_link"]
        season.clubs_link = data["clubs_link"]
        season.statistics_link = data["statistics_link"]
        season.scoreboard_link = data["scoreboard_link"]
        season.save()
        return [model_to_dict(row) for row in Season.select().order_by(Season.season_id.desc())]
    
class SyncSeason(Resource):
    def post(self, season_id):
        sync = Sync.create(name=f'Sync season: {season_id}', status='pending', created=datetime.now())
        queue.enqueue(syncSeason, season_id, sync.id)
        return "ok"

class AddSeason(Resource):
    def post(self):
        data = request.get_json()
        print()
        print(data["season_link"])
        Season.create(
            season_id=Season.select(fn.Max(Season.season_id)).scalar()+1,
            season_link=data["season_link"],
            clubs_link=data["clubs_link"],
            statistics_link=data["statistics_link"],
            scoreboard_link=data["scoreboard_link"],
            description=None)
        return [model_to_dict(row) for row in Season.select().order_by(Season.season_id.desc())]

def syncSeason(season_id, sync_id):
    sync = Sync.get_by_id(sync_id)
    sync.status = 'executing'
    sync.save()
    try:
        print("task running")
        query = Season.select().where(Season.season_id == season_id).get()
        print("getting clubs")
        getClubsFromSeason(query.clubs_link)
        if(query.statistics_link != "" and query.statistics_link != None):
            print("getting players")
            getPlayersFromSeason(query.season_id, query.statistics_link)
            print("getting stats")
            getStatsFromSeason(query.season_id, query.statistics_link)
        print("getting matches")
        getMatchesFromSeason(query.season_link)
        print("getting scoreboard")
        getScoreboardFromSeason(query.season_id, query.scoreboard_link)
        sync.status = 'completed'
    except Exception as e:
        sync.message = str(e)
        sync.status = 'failed'
    finally:
        sync.finished = datetime.now()
        sync.save()