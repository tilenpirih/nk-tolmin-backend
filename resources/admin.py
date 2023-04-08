import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from werkzeug.security import generate_password_hash, check_password_hash
from peewee import IntegrityError
from flask import request
from schema import User
from flask_restful import Resource
from flask_login import LoginManager, login_required, login_user, logout_user
from playhouse.shortcuts import model_to_dict
from flask_login import current_user
# from app import limiter
# get logged in user info

class GetUsers(Resource):
    @login_required
    def get(self):
        query = User.select(User.id, User.username, User.name, User.surname)
        test = [model_to_dict(user, fields_from_query=query) for user in query]
        return test

class GetAllPlayers(Resource):
    # @login_required
    def get(self):
        query = User.select(User.id, User.username, User.name, User.surname)
        test = [model_to_dict(user, fields_from_query=query) for user in query]
        return test
    
class AddUser(Resource):
    def post(self):
        try:
            username = request.args.get('username')
            password = request.args.get('password')
            name = request.args.get('name')
            surname = request.args.get('surname')
            User.create(username=username, name=name,surname=surname,
                        password=generate_password_hash(password))
            return {'data': 'User created'}
        except IntegrityError:
            print("User already exists")
            return {'data': 'User already exists'}, 400


# class Login(Resource):
#     def post(self):
#         username = request.args.get('username')
#         password = request.args.get('password')
#         user = User.select().where(User.username == username)
#         if not user.exists():
#             return {'data': 'No such user'}, 400

#         if not check_password_hash(user.get().password, password):
#             return {'data': 'Wrong password'}, 400
#         login_user(user.get())
#         return { 'username': user.get().username, 'id': user.get().id, 'name': user.get().name, 'surname': user.get().surname }


class Logout(Resource):
    def post(self):
        logout_user()
        return {'data': 'Logged out'}

class DeleteUser(Resource):
    def post(self, user_id):
        user = User.get_by_id(user_id)
        user.delete_instance()
        # username = request.args.get('username')
        # if not User.select().where(User.username == username).exists():
        #     return {'data': 'No such user'}, 400
        # User.delete().where(User.username == username).execute()
        return {'data': 'User deleted'}

class IsLoggedIn(Resource):
    def get(self):
        current_user
        if current_user.is_authenticated:
            query = User.get_by_id(current_user)
            dict = {}
            dict['username'] = query.username
            dict['name'] = query.name
            dict['surname'] = query.surname
            return dict
        return
        
