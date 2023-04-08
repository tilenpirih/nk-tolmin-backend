import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from flask_restful import Resource
from playhouse.shortcuts import model_to_dict
from schema import Club, Season
from urllib.parse import quote, unquote
from PIL import Image
from flask import request

class GetAllClubs(Resource):
    def get(self):
        query = [model_to_dict(row) for row in Club.select()]
        return query

class GetClub(Resource):
    def get(self, club_id):
        query = model_to_dict(Club.get_by_id(club_id))
        return query

class UpdateClubLogo(Resource):
    def post(self, club_id):
        club = Club.get_by_id(club_id)
        file_exists = False
        if club.original_logo_path:
            file_exists = os.path.exists(unquote(club.original_logo_path))
        if file_exists:
            os.remove(unquote(club.original_logo_path))    
            os.remove(unquote(club.small_logo_path))    
        file = request.files['image']
        fileExt = os.path.splitext(file.filename)[1]
        file.save(os.path.join('assets/grbi/original',f'{club.name}{fileExt}'))
        Image.open(file).resize((72, 72)).save(os.path.join('assets/grbi/72',f'{club.name}{fileExt}'))
        club.original_logo_path = f"assets/grbi/original/{quote(club.name)}{fileExt}"
        club.small_logo_path = f"assets/grbi/72/{quote(club.name)}{fileExt}"
        club.save()
        return model_to_dict(club)

class DeleteClubLogo(Resource):
    def delete(self, club_id):
        club = Club.get_by_id(club_id)
        file_exists = False
        if club.original_logo_path:
            file_exists = os.path.exists(unquote(club.original_logo_path))
        if file_exists:
            os.remove(unquote(club.original_logo_path))    
            os.remove(unquote(club.small_logo_path))    
        club.original_logo_path = None
        club.small_logo_path = None
        club.save()
        return model_to_dict(club)