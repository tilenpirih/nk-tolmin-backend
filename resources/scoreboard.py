from db import db
from schema import ScoreboardSeason, ClubScoreboard, Club
from flask_restful import Resource
from playhouse.shortcuts import model_to_dict
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


class GetScoreboardFromSeason(Resource):
    def get(self, season_id):
        query = ClubScoreboard.select(
            ClubScoreboard, ScoreboardSeason, Club
        ).join(Club).switch(ClubScoreboard).join(ScoreboardSeason).where(ScoreboardSeason.season_id == season_id).order_by(ClubScoreboard.club_position.asc())
        query = [model_to_dict(row, fields_from_query=query) for row in query]
        return query
