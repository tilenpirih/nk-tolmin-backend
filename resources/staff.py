from urllib.parse import quote, unquote
from pathlib import Path
from flask import request
from playhouse.shortcuts import model_to_dict
from flask_restful import Resource
from schema import Staff, Season
from db import db
from slugify import slugify
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

def getStaff(season_id):
    return [model_to_dict(row, recurse=False) for row in Staff.select().where(Staff.season_id == season_id)]

class GetStaff(Resource):
    def get(self, season_id):
        return getStaff(season_id)


class AddStaff(Resource):
    def post(self, season_id):
        full_name = request.form.get('full_name')
        role = request.form.get('role') or None
        image = request.files.get('image')
        img_path = None
        # print(full_name, role, image)
        sluggified = slugify(full_name)
        if image:
            fileExt = os.path.splitext(image.filename)[1]
            file = Path(
                f'./assets/staff/{sluggified}{os.path.splitext(image.filename)[1]}')
            print(file)
            if not file.exists():
                image.save(os.path.join(f'./assets/staff', f'{sluggified}{fileExt}'))
                img_path = f"assets/staff/{quote(sluggified)}{fileExt}"
        Staff.create(full_name=full_name, role=role, img_path=img_path, season_id=season_id)
        return getStaff(season_id)

class DeleteStaff(Resource):
    def post(self, season_id, staff_id):
        print(staff_id)
        staff = Staff.get_by_id(staff_id)
        # delete image
        if staff.img_path:
            os.remove(f"./{unquote(staff.img_path)}")
        staff.delete_instance()
        return getStaff(season_id)