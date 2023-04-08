from peewee import fn
from schema import Season, Match
from playhouse.shortcuts import model_to_dict
from flask_restful import Resource
from scraping.matches import addMatch
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


class MatchRoute(Resource):
    def get(self, match_id):
        query = model_to_dict(Match.get_by_id(match_id))
        query["match_date"] = query["match_date"].isoformat()
        return query

    def post(self, match_id):
        addMatch(match_id)
        return 'Match '+str(match_id)+' synced'


class MatchesFromSeason(Resource):
    def get(self, season_id):
        query = Match.select(Match.match_id, Match.match_date, Match.home_team, Match.road_team, Match.location, Match.home_team_goals, Match.road_team_goals, Match.match_num, Match.finished_match).where(
            Match.season_id == season_id).order_by(Match.match_date)
        query = [model_to_dict(row, fields_from_query=query, extra_attrs=['home_team', 'road_team']) for row in query]
        for row in query:
            row["home_team"] = model_to_dict(row["home_team"])
            row["road_team"] = model_to_dict(row["road_team"])
            row["match_date"] = row["match_date"].isoformat()   
        return query


class MatchesFromLastSeason(Resource):
    # TODO maybe there is a cleaner way to do this
    def get(self):
        query = Match.select(Match.match_id, Match.match_date, Match.home_team, Match.road_team, Match.location, Match.home_team_goals, Match.road_team_goals).where(
            Match.season_id == Season.select(fn.Max(Season.season_id)).scalar(), Match.finished_match == True).order_by(Match.match_date.asc())
        query2 = Match.select(Match.match_id, Match.match_date, Match.home_team, Match.road_team, Match.location).where(
            Match.season_id == Season.select(fn.Max(Season.season_id)).scalar(), Match.finished_match == False).order_by(Match.match_date.asc())
            
        query = [model_to_dict(row, fields_from_query=query, extra_attrs=['home_team', 'road_team']) for row in query]
        for row in query:
            row["home_team"] = model_to_dict(row["home_team"])
            row["road_team"] = model_to_dict(row["road_team"])
            row["match_date"] = row["match_date"].isoformat()   

        query2 = [model_to_dict(row, fields_from_query=query2, extra_attrs=['home_team', 'road_team']) for row in query2]
        for row in query2:
            row["home_team"] = model_to_dict(row["home_team"])
            row["road_team"] = model_to_dict(row["road_team"])
            row["match_date"] = row["match_date"].isoformat()
        return {"finished": query, "unfinished": query2}
