from peewee import *
from playhouse.postgres_ext import *
from db import db
from werkzeug.security import generate_password_hash
from datetime import datetime


class BaseModel(Model):
    class Meta:
        database = db
        

class User(BaseModel):
    username = TextField(unique=True, primary_key=True)
    password = TextField()
    name = TextField(null=True)
    surname = TextField(null=True)
    is_active = BooleanField(default=True)
    is_authenticated = BooleanField(default=True)

    def get_id(self):
        return self.username


class Season (BaseModel):
    season_id = PrimaryKeyField()
    season_link = TextField()
    clubs_link = TextField()
    statistics_link = TextField(null=True)
    scoreboard_link = TextField()
    description = TextField(null=True)


class Player (BaseModel):
    player_id = PrimaryKeyField()
    full_name = TextField()
    year_of_birth = IntegerField(null=True)
    img_path = TextField(null=True)
    league_statistic = JSONField(null=True)
    sum_competitions = JSONField(null=True)
    description = TextField(null=True)
    updated_at = DateTimeField(default=datetime.now)


class PlayerCompetition (BaseModel):
    id = TextField(primary_key=True)
    matches = JSONField(null=True)
    sum_competitions = JSONField(null=True)
    competition_id = IntegerField()
    player_id = ForeignKeyField(Player, backref='player_competitions')

class Staff (BaseModel):
    staff_id = PrimaryKeyField()
    full_name = TextField()
    role = TextField(null=True)
    img_path = TextField(null=True)
    season_id = ForeignKeyField(Season, backref='staffs')

class Club (BaseModel):
    club_id = PrimaryKeyField()
    name = TextField()
    original_logo_path = TextField(null=True)
    small_logo_path = TextField(null=True)


class Match (BaseModel):
    match_id = PrimaryKeyField()
    match_num = IntegerField(null=True)
    location = TextField(null=True)
    finished_match = BooleanField(null=True)
    home_team_goals = IntegerField(null=True)
    road_team_goals = IntegerField(null=True)
    scores = JSONField(null=True)
    match_date = DateTimeField(null=True)
    delegat = TextField(null=True)
    referees = TextField(null=True)
    num_of_people = IntegerField(null=True)
    events = JSONField(null=True)
    home_team_coach = TextField(null=True)
    road_team_coach = TextField(null=True)
    players = JSONField(null=True)
    home_team = ForeignKeyField(Club, backref='home_team_matches')
    road_team = ForeignKeyField(Club, backref='road_team_matches')
    season_id = ForeignKeyField(Season, backref='season_matches')


class PlayerSeason (BaseModel):
    id = PrimaryKeyField()
    player_id = ForeignKeyField(Player, backref='player_seasons')
    season_id = ForeignKeyField(Season, backref='season_players')
    position = TextField(default='NA')


class ClubScoreboard(BaseModel):
    id = TextField(primary_key=True)
    club_id = ForeignKeyField(Club, backref='club_scoreboard', null=True)
    club_position = IntegerField()
    num_matches = IntegerField()
    wins = IntegerField()
    draws = IntegerField()
    losses = IntegerField()
    points_get_lost = TextField()
    points_difference = IntegerField()
    points = IntegerField()


class ScoreboardSeason(BaseModel):
    id = PrimaryKeyField()
    season_id = ForeignKeyField(Season, backref='season_scoreboard')
    club_scoreboard = ForeignKeyField(
        ClubScoreboard, backref='scoreboard_season')


class StatsPlayer(BaseModel):
    id = TextField(primary_key=True)
    goals = IntegerField()
    yellow_cards = IntegerField()
    red_cards = IntegerField()
    minutes = IntegerField()
    num_appearances = IntegerField()
    player_id = ForeignKeyField(Player, backref='player_stats')
    season_id = ForeignKeyField(Season, backref='season_stats')


class StatsPlayerSeason(BaseModel):
    id = PrimaryKeyField()
    season_id = ForeignKeyField(Season, backref='season_scoreboard')
    stats_player_id = ForeignKeyField(
        StatsPlayer, backref='stats_player_season')

# ---------------------------------------------------------------


class Article (BaseModel):
    article_id = PrimaryKeyField()
    title = TextField(null=True)
    preview = TextField(null=True)
    content = TextField(null=True)
    thumbnail = TextField(null=True)
    images = JSONField(null=True)
    gallery_images = JSONField(null=True)
    created = DateTimeField(default=datetime.now())
    updated = DateTimeField(default=datetime.now())
    visible = BooleanField(default=False)

class Sync(BaseModel):
    id = PrimaryKeyField()
    name = TextField()
    status = TextField(null=True)
    message = TextField(null=True)
    created = DateTimeField(default=datetime.now())
    finished = DateTimeField(default=None, null=True)

class Event(BaseModel):
    id = PrimaryKeyField()
    category = TextField()
    name = TextField()
    color = TextField()
    description = TextField(null=True)
    timed = BooleanField()
    start = DateTimeField()
    end = DateTimeField()
    
class Sponsors(BaseModel):
    id = PrimaryKeyField()
    name = TextField()
    tier = TextField()
    url = TextField(null=True)
    img = TextField(null=True)
    
class YoungerTeam(BaseModel):
    id = TextField(primary_key=True)
    original_group_photo = TextField(null=True)
    lazy_group_photo = TextField(null=True)
    content = TextField(null=True)


def create_user(username, password):
    try:
        User.create(
            username=username,
            password=generate_password_hash(password))
    except IntegrityError:
        print("User already exists")


def delete_user(user_id):
    try:
        user = User.get(User.username == user_id)
        user.delete_instance()
        print(user_id + " deleted")
    except User.DoesNotExist:
        print('no such user')


def list_users():
    try:
        print('Users: '),
        for person in User.select():
            print(person.username),
    except:
        print('no users')


def get_username(data):
    return User.get(User.username == data)


def get_password(data):
    return User.get(User.password == data)


db.create_tables([
    User,
    Player,
    PlayerCompetition,
    Club,
    Season,
    Match,
    Article,
    PlayerSeason,
    ClubScoreboard,
    ScoreboardSeason,
    StatsPlayer,
    StatsPlayerSeason,
    Sync,
    Event,
    Sponsors,
    Staff,
    YoungerTeam
])
