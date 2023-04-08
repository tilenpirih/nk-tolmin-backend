import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from urllib.parse import quote, unquote
from flask import request
from flask_restful import Resource
from playhouse.shortcuts import model_to_dict
from scraping.players import addPlayer, getPlayerCompetitions
from schema import Player, PlayerCompetition, PlayerSeason, Sync
from datetime import datetime
from sync import queue

class GetPlayersFromSeason(Resource):
    def get(self, season_id):
        query = Player.select(Player.player_id, Player.full_name, Player.year_of_birth, Player.description, Player.img_path, PlayerSeason.position).join(PlayerSeason).where(
            PlayerSeason.season_id == season_id
        )
        result = []
        for row in query:
            dict = model_to_dict(row, fields_from_query=query)
            dict['position'] = row.playerseason.position
            # print(model_to_dict(row.playerseason, fields_from_query=query))
            result.append(dict)
            # print(dict)
        return result
        # query = Player.select(Player.player_id, Player.full_name, Player.year_of_birth, Player.position, Player.description, Player.img_path)
        # return [model_to_dict(row, fields_from_query=query) for row in query]


class GetAllPlayers(Resource):
    # @login_required
    def get(self):
        query = Player.select(Player.player_id, Player.full_name, Player.year_of_birth,
                              Player.description, Player.img_path).order_by(Player.updated_at.desc())
        query = [model_to_dict(row, fields_from_query=query) for row in query]
        return query


class GetPlayer(Resource):
    def get(self, player_id):
        query = model_to_dict(Player.get_by_id(player_id))
        query["updated_at"] = query["updated_at"].isoformat()
        return query

class AdminGetPlayer(Resource):
    def get(self, player_id):
        positions = PlayerSeason.select(PlayerSeason.season_id, PlayerSeason.position).where(PlayerSeason.player_id==player_id).order_by(PlayerSeason.season_id.desc())
        positions = [model_to_dict(row, recurse=False, fields_from_query=positions) for row in positions]
        query = model_to_dict(Player.get_by_id(player_id))
        query["positions"] = positions
        query["updated_at"] = query["updated_at"].isoformat()
        return query

class GetCompetition(Resource):
    def get(self):
        player_id = request.args.get('player_id')
        competition_id = request.args.get('competition_id')
        player_name = Player.get_by_id(player_id).full_name
        query = model_to_dict(PlayerCompetition.get_by_id(
            player_id+competition_id), recurse=False)
        query['player_name'] = player_name
        return query


class UpdatePlayer(Resource):
    def post(self, player_id):
        player = Player.select().where(Player.player_id == player_id)
        if player.exists():
            year_of_birth = request.form.get('year_of_birth')
            description = request.form.get('description')
            Player.update(year_of_birth=year_of_birth, description=description, updated_at=datetime.now()).where(
                Player.player_id == player_id).execute()
            model = model_to_dict(player.get())
            model["updated_at"] = model["updated_at"].isoformat()
            return model
        else:
            return {'message': 'player not found'}, 400


class UpdatePlayerImage(Resource):
    def post(self, player_id):
        player = Player.get_by_id(player_id)
        file_exists = False
        if player.img_path:
            file_exists = os.path.exists(unquote(player.img_path))
        if file_exists:
            os.remove(unquote(player.img_path))
        file = request.files['image']
        fileExt = os.path.splitext(file.filename)[1]
        file.save(os.path.join('assets/players',
                  f'{player.full_name}{fileExt}'))
        player.img_path = f"assets/players/{quote(player.full_name)}{fileExt}"
        player.save()
        model = model_to_dict(player)
        model["updated_at"] = model["updated_at"].isoformat()
        return model
    
class DeletePlayerImage(Resource):
    def delete(self, player_id):
        player = Player.get_by_id(player_id)
        file_exists = os.path.exists(unquote(player.img_path))
        if file_exists:
            os.remove(unquote(player.img_path))
        player.img_path = None
        player.save()
        model = model_to_dict(player)
        model["updated_at"] = model["updated_at"].isoformat()
        return model

class ChangePlayerPosition(Resource):
    def post(self, player_id):
        season_id = int(request.form.get('season_id'))
        position = request.form.get('position')
        player_season = PlayerSeason.get(PlayerSeason.player_id == player_id, PlayerSeason.season_id == season_id)
        player_season.position = position
        player_season.save()
        positions = PlayerSeason.select(PlayerSeason.season_id, PlayerSeason.position).where(PlayerSeason.player_id==player_id).order_by(PlayerSeason.season_id.desc())
        positions = [model_to_dict(row, recurse=False, fields_from_query=positions) for row in positions]
        return positions

class SyncPlayer(Resource):
    def post(self, player_id):
        sync = Sync.create(name=f'Sync player: {player_id}', status='pending', created=datetime.now())
        queue.enqueue(syncPlayer, player_id, sync.id)
        return {'message': 'success'}, 200

def syncPlayer(player_id, sync_id):
    sync = Sync.get_by_id(sync_id)
    sync.status = 'executing'
    sync.save()
    try:
        addPlayer(player_id)
        getPlayerCompetitions(player_id)
        sync.status = 'completed'
    except Exception as e:
        sync.message = str(e)
        sync.status = 'failed'
    finally:
        sync.finished = datetime.now()
        sync.save()