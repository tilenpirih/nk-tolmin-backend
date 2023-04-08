import os
import sys

from async_timeout import timeout
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from db import db
from schema import Sync
from flask_restful import Resource
from playhouse.shortcuts import model_to_dict
from math import ceil
from sync import queue
from datetime import datetime
from scraping.clubs import getAllClubs
from scraping.players import getAllPlayers
from scraping.matches import getAllMatches
from scraping.scoreboard import getAllScoreboards
from scraping.statistics import getAllStats

class GetSyncs(Resource):
    def get(self, page):
        numSyncs = Sync.select().count()
        numPages = ceil(numSyncs / 10)
        if page > numPages:
            page = numPages
        syncs = Sync.select().order_by(Sync.created.desc()).paginate(page, 10)
        for sync in syncs:
            sync.created = sync.created.isoformat()
            if sync.finished is not None:
                sync.finished = sync.finished.isoformat()
        obj = {}
        obj["syncs"] = [model_to_dict(sync, fields_from_query=syncs) for sync in syncs]
        obj["page"] = page
        obj["pages"] = numPages
        return obj

class SyncAllClubs(Resource):
    def post(self):
        sync = Sync.create(name=f'Sync all clubs', status='pending', created=datetime.now())
        queue.enqueue(syncAllClubs,sync.id)
        return "ok"
    
class SyncAllPlayers(Resource):
    def post(self):
        sync = Sync.create(name=f'Sync all players', status='pending', created=datetime.now())
        queue.enqueue(syncAllPlayers,sync.id)
        return "ok"

class SyncAllMatches(Resource):
    def post(self):
        sync = Sync.create(name=f'Sync all matches', status='pending', created=datetime.now())
        queue.enqueue(syncAllMatches,sync.id)
        return "ok"
    
class SyncAllScoreboards(Resource):
    def post(self):
        sync = Sync.create(name=f'Sync all scoreboards', status='pending', created=datetime.now())
        queue.enqueue(syncAllScoreboards,sync.id)
        return "ok"

class SyncAllStats(Resource):
    def post(self):
        sync = Sync.create(name=f'Sync all stats', status='pending', created=datetime.now())
        queue.enqueue(syncAllStats,sync.id)
        return "ok"
    
def syncAllClubs(sync_id):
    sync = Sync.get_by_id(sync_id)
    sync.status = 'executing'
    sync.save()
    try:
        print("syncing all clubs")
        getAllClubs()
        sync.status = 'completed'
    except Exception as e:
        sync.message = str(e)
        sync.status = 'failed'
    finally:
        sync.finished = datetime.now()
        sync.save()

def syncAllPlayers(sync_id):
    sync = Sync.get_by_id(sync_id)
    sync.status = 'executing'
    sync.save()
    try:
        print("syncing all players")
        getAllPlayers()
        sync.status = 'completed'
    except Exception as e:
        sync.message = str(e)
        sync.status = 'failed'
    finally:
        sync.finished = datetime.now()
        sync.save()

def syncAllMatches(sync_id):
    sync = Sync.get_by_id(sync_id)
    sync.status = 'executing'
    sync.save()
    try:
        print("syncing all matches")
        getAllMatches()
        sync.status = 'completed'
    except Exception as e:
        sync.message = str(e)
        sync.status = 'failed'
    finally:
        sync.finished = datetime.now()
        sync.save()

def syncAllScoreboards(sync_id):
    sync = Sync.get_by_id(sync_id)
    sync.status = 'executing'
    sync.save()
    try:
        print("syncing all scoreboards")
        getAllScoreboards()
        sync.status = 'completed'
    except Exception as e:
        sync.message = str(e)
        sync.status = 'failed'
    finally:
        sync.finished = datetime.now()
        sync.save()

def syncAllStats(sync_id):
    sync = Sync.get_by_id(sync_id)
    sync.status = 'executing'
    sync.save()
    try:
        print("syncing all scoreboards")
        getAllStats()
        sync.status = 'completed'
    except Exception as e:
        sync.message = str(e)
        sync.status = 'failed'
    finally:
        sync.finished = datetime.now()
        sync.save()