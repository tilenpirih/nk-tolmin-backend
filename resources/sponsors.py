from urllib.parse import quote, unquote
from pathlib import Path
from flask import request
from playhouse.shortcuts import model_to_dict
from flask_restful import Resource
from schema import Sponsors
from db import db
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

def get_sponsors():
    query = [model_to_dict(row) for row in Sponsors.select()]
    query2 = {
        "main": [],
        "gold": [],
        "silver": [],
        "other": [],
    }
    for sponsor in query:
        query2[sponsor["tier"]].append(sponsor)
    return query2

class GetAllSponsors(Resource):
    def get(self):
        return get_sponsors()


class AddSponsor(Resource):
    def post(self):
        name = request.form.get('name')
        url = request.form.get('url') or None
        tier = request.form.get('tier')
        image = request.files.get('image')
        image_path = None
        if image:
            fileExt = os.path.splitext(image.filename)[1]
            file = Path(
                f'./assets/sponsors/{name}{os.path.splitext(image.filename)[1]}')
            if not file.exists():
                image.save(os.path.join(f'./assets/sponsors', f'{name}{fileExt}'))
                image_path = f"assets/sponsors/{quote(name)}{fileExt}"
        Sponsors.create(name=name, url=url, tier=tier, img=image_path)
        return get_sponsors()

class DeleteSponsor(Resource):
    def post(self, id):
        print(id)
        sponsor = Sponsors.get_by_id(id)
        # delete image
        if sponsor.img:
            os.remove(f"./{unquote(sponsor.img)}")
        sponsor.delete_instance()
        return get_sponsors()