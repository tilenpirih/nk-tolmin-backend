from db import db
from schema import Event
from flask_restful import Resource
from playhouse.shortcuts import model_to_dict
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from flask import request
from datetime import datetime


class AddEvent(Resource):
    def post(self):
        data = request.get_json()
        if data["timed"] == True:
            start = datetime.strptime(data["start"], "%d.%m.%Y %H:%M")
            end = datetime.strptime(data["end"], "%d.%m.%Y %H:%M")
        else:
            start = datetime.strptime(data["start"], "%d.%m.%Y")
            end = datetime.strptime(data["end"], "%d.%m.%Y")
        event = Event.create(name=data["name"], description=data["description"], start=start, end=end, timed=data["timed"], color=data["color"], category=data["category"])
        # print(event)
        event = model_to_dict(event)
        event["start"] = event["start"].isoformat()
        event["end"] = event["end"].isoformat()
        return event

class GetEvents(Resource):
    def get(self, category):
        start = datetime.strptime(request.args.get('start'), "%Y-%m-%d")
        end = datetime.strptime(request.args.get('end'), "%Y-%m-%d")
        if category == "VSI":
            query = Event.select().where(Event.start >= start, Event.end <= end)
        else:
            query = Event.select().where(Event.category == category, Event.start >= start, Event.end <= end)
        query = [model_to_dict(row) for row in query]
        for row in query:
            row["start"] = row["start"].isoformat() 
            row["end"] = row["end"].isoformat() 
        return query

class DeleteEvent(Resource):
    def delete(self, id):
        event = Event.get(Event.id == id)
        event.delete_instance()
        return "Event deleted"
