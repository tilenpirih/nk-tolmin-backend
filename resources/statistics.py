from schema import StatsPlayer, StatsPlayerSeason, Player
from flask_restful import Resource
from playhouse.shortcuts import model_to_dict
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


class GetStatsFromSeason(Resource):
    def get(self, season_id):
        query = StatsPlayer.select(
            StatsPlayer.id,
            StatsPlayer.num_appearances,
            StatsPlayer.minutes,
            StatsPlayer.goals,
            StatsPlayer.yellow_cards,
            StatsPlayer.red_cards,
            Player.full_name,
        ).join(Player, attr="player").switch(StatsPlayer).join(StatsPlayerSeason).switch(StatsPlayer).where(StatsPlayerSeason.season_id == season_id).order_by(StatsPlayer.goals.desc())
        arr = []
        for row in query:
            dict = model_to_dict(row, fields_from_query=query)
            dict['player'] = row.player.full_name
            arr.append(dict)
        return arr

