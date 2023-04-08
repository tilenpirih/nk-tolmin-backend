from dotenv import load_dotenv
from flask import Flask, send_from_directory
from peewee import *
from flask_restful import Api, Resource
from resources.match import MatchRoute, MatchesFromSeason, MatchesFromLastSeason
from resources.season import GetSeasons, UpdateSeason, SyncSeason, AddSeason
from resources.player import GetAllPlayers, GetPlayer, GetCompetition, UpdatePlayerImage, UpdatePlayer, GetPlayersFromSeason, AdminGetPlayer, DeletePlayerImage, ChangePlayerPosition, SyncPlayer
from resources.admin import AddUser, Logout, GetUsers, IsLoggedIn, DeleteUser
from resources.article import CreateArticle, DeleteImage, UpdateArticle, AddImagesArticle, DeleteArticle, GetArticle, GetArticles, GetAllArticles
from resources.scoreboard import GetScoreboardFromSeason
from resources.statistics import GetStatsFromSeason
from resources.club import GetAllClubs, GetClub, UpdateClubLogo, DeleteClubLogo
from resources.sync import GetSyncs, SyncAllClubs, SyncAllPlayers, SyncAllMatches, SyncAllScoreboards, SyncAllStats
from resources.events import AddEvent, GetEvents, DeleteEvent
from resources.sponsors import GetAllSponsors, AddSponsor, DeleteSponsor
from resources.staff import GetStaff, AddStaff, DeleteStaff
from resources.youngerTeam import UpdateYoungerTeamPhoto, GetYoungerTeam, DeleteYoungerTeamPhoto, UpdateYoungerTeamContent

from schema import *
from db import db
from flask_login import LoginManager, login_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import check_password_hash
from flask import request
from flask_cors import CORS
import os
load_dotenv()

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['SECRET_KEY'] = 'secret_key'
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
# disable this line if you want to use postman
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
login_manager = LoginManager()
login_manager.init_app(app)

# TODO add storage options because now everything is stored in memory
limiter = Limiter(
    app,
    key_func=get_remote_address,
    storage_uri="memory://",
)
# temp solution to rate limit because of circular error... move this to resource/admin.py in the future


class Login(Resource):
    decorators = [limiter.limit("5/5 seconds")]
    def post(self):
        username = request.json["username"]
        password = request.json["password"]
        user = User.select().where(User.username == username)
        if not user.exists():
            return {'data': 'No such user'}, 400

        if not check_password_hash(user.get().password, password):
            return {'data': 'Wrong password'}, 400
        login_user(user.get())
        return {'username': user.get().username, 'name': user.get().name, 'surname': user.get().surname}


@app.before_request
def _db_connect():
    db.connect()


@app.teardown_request
def _db_close(exc):
    if not db.is_closed():
        db.close()


api = Api(app, prefix="/api")

api.add_resource(MatchRoute, '/match/<int:match_id>')
api.add_resource(MatchesFromSeason, '/matchesFromSeason/<int:season_id>')
api.add_resource(MatchesFromLastSeason, '/matchesLastSeason')

api.add_resource(GetSeasons, '/seasons')
api.add_resource(SyncSeason, '/syncSeason/<int:season_id>')
api.add_resource(UpdateSeason, '/updateSeason')
api.add_resource(AddSeason, '/addSeason')

api.add_resource(GetAllPlayers, '/getAllPlayers')
api.add_resource(GetPlayersFromSeason, '/getPlayersFromSeason/<int:season_id>')
api.add_resource(GetPlayer, '/getPlayer/<int:player_id>')
api.add_resource(UpdatePlayerImage, '/updatePlayerImage/<int:player_id>')
api.add_resource(UpdatePlayer, '/updatePlayer/<int:player_id>')
api.add_resource(DeletePlayerImage, '/deletePlayerImage/<int:player_id>')
api.add_resource(ChangePlayerPosition, '/changePlayerPosition/<int:player_id>')
api.add_resource(AdminGetPlayer, '/adminGetPlayer/<int:player_id>')
api.add_resource(SyncPlayer, '/syncPlayer/<int:player_id>')

api.add_resource(GetCompetition, '/getCompetition')
api.add_resource(AddUser, '/addUser')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(GetUsers, '/users')
api.add_resource(DeleteUser, '/deleteUser/<int:user_id>')
api.add_resource(IsLoggedIn, '/isLoggedIn')
api.add_resource(GetAllClubs, '/getAllClubs')
api.add_resource(GetClub, '/getClub/<int:club_id>')
api.add_resource(UpdateClubLogo, '/updateClubLogo/<int:club_id>')
api.add_resource(DeleteClubLogo, '/deleteClubLogo/<int:club_id>')

api.add_resource(GetAllArticles, '/getAllArticles')
api.add_resource(GetArticles, '/articles/<int:page>')
api.add_resource(GetArticle, '/article/<int:article_id>')
api.add_resource(CreateArticle, '/createArticle')
api.add_resource(UpdateArticle, '/updateArticle/<int:article_id>')
api.add_resource(DeleteImage, '/deleteImage/<int:article_id>')
api.add_resource(AddImagesArticle, '/addImagesArticle/<int:article_id>')
api.add_resource(DeleteArticle, '/deleteArticle/<int:article_id>')
api.add_resource(GetScoreboardFromSeason,
                 '/getScoreboardFromSeason/<int:season_id>')
api.add_resource(GetStatsFromSeason, '/getStatsFromSeason/<int:season_id>')

api.add_resource(GetSyncs, '/syncs/<int:page>')
api.add_resource(SyncAllClubs, '/syncAllClubs')
api.add_resource(SyncAllPlayers, '/syncAllPlayers')
api.add_resource(SyncAllMatches, '/syncAllMatches')
api.add_resource(SyncAllScoreboards, '/syncAllScoreboards')
api.add_resource(SyncAllStats, '/syncAllStats')

api.add_resource(AddEvent, '/addEvent')
api.add_resource(GetEvents, '/getEvents/<string:category>')
api.add_resource(DeleteEvent, '/deleteEvent/<int:id>')

api.add_resource(GetAllSponsors, '/sponsors')
api.add_resource(AddSponsor, '/addSponsor')
api.add_resource(DeleteSponsor, '/deleteSponsor/<int:id>')

api.add_resource(GetStaff, '/staff/<int:season_id>')
api.add_resource(AddStaff, '/addStaff/<int:season_id>')
api.add_resource(DeleteStaff, '/deleteStaff/<int:season_id>/<int:staff_id>')

api.add_resource(GetYoungerTeam, '/getYoungerTeam/<string:id>')
api.add_resource(UpdateYoungerTeamPhoto, '/updateYoungerTeamPhoto/<string:id>')
api.add_resource(DeleteYoungerTeamPhoto, '/deleteYoungerTeamPhoto/<string:id>')
api.add_resource(UpdateYoungerTeamContent, '/updateYoungerTeamContent/<string:id>')



# user_manager = UserManager(app, db, User)

@app.route("/api/health")
def admin():
    return "OK"


@login_manager.user_loader
def load_user(id):
    return get_username(id)


@app.route("/api/assets/<path:path>")
def static_dir(path):
    return send_from_directory("assets", path)


if __name__ == "__main__":
    if os.getenv("BASE_URL") == "http://127.0.0.1:5000/":
        app.run(debug=True)
    else:
        from waitress import serve
        serve(app, host="0.0.0.0", port=5000)
        
