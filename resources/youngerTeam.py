from urllib.parse import quote, unquote
from pathlib import Path
from flask import request
from playhouse.shortcuts import model_to_dict
from flask_restful import Resource
from schema import YoungerTeam
from PIL import Image
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

def get_team(id):
    return model_to_dict(YoungerTeam.get_by_id(id))

class GetYoungerTeam(Resource):
    def get(self, id):
        return get_team(id)


class UpdateYoungerTeamPhoto(Resource):
    def post(self, id):
        team = YoungerTeam.get_by_id(id)
        file_exists = False
        if team.original_group_photo:
            file_exists = os.path.exists(unquote(team.original_group_photo))
        if file_exists:
            os.remove(unquote(team.original_group_photo))    
            os.remove(unquote(team.lazy_group_photo))    
        file = request.files['image']
        fileExt = os.path.splitext(file.filename)[1]
        file.save(os.path.join('assets/youngerTeam/original',f'{team.id}{fileExt}'))
        # Image.open(file).resize((72, 72)).save(os.path.join('assets/youngerTeam/lazy',f'{team.id}{fileExt}'))
        # resize image to lazy image but keep aspect ratio
        img = Image.open(file)
        new_height = int(img.size[1]*(20/img.size[0]))
        img.resize((20, new_height)).save(os.path.join('assets/youngerTeam/lazy',f'{team.id}{fileExt}'))
        # Image.open(file).resize((72, 72), Image.ANTIALIAS).save(os.path.join('assets/youngerTeam/lazy',f'{team.id}{fileExt}'))
        team.original_group_photo = f"assets/youngerTeam/original/{quote(team.id)}{fileExt}"
        team.lazy_group_photo = f"assets/youngerTeam/lazy/{quote(team.id)}{fileExt}"
        team.save()
        return model_to_dict(team)

class UpdateYoungerTeamContent(Resource):
    def post(self, id):
        team = YoungerTeam.get_by_id(id)
        team.content = request.form['content']
        team.save()
        return model_to_dict(team)

class DeleteYoungerTeamPhoto(Resource):
    def delete(self, id):
        team = YoungerTeam.get_by_id(id)
        file_exists = False
        if team.original_group_photo:
            file_exists = os.path.exists(unquote(team.original_group_photo))
        if file_exists:
            os.remove(unquote(team.original_group_photo))    
            os.remove(unquote(team.lazy_group_photo))    
        team.original_group_photo = None
        team.lazy_group_photo = None
        team.save()
        return model_to_dict(team)