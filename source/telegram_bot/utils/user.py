import sqlalchemy
from .connect_creater import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'
    chat_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    player_id = sqlalchemy.Column(sqlalchemy.Integer, default=-1)
    message_id = sqlalchemy.Column(sqlalchemy.Integer, default=-1)
    liked = sqlalchemy.Column(sqlalchemy.String, default='[]')
    language = sqlalchemy.Column(sqlalchemy.String, default='eng')
    playlists = sqlalchemy.Column(sqlalchemy.String, default='{}')
    playlist_names = sqlalchemy.Column(sqlalchemy.String, default='{}')
    script = sqlalchemy.Column(sqlalchemy.String, default='')
    track_id = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    playlist = sqlalchemy.Column(sqlalchemy.String, default='')

    def default(self):
        self.player_id = -1
        self.liked = '[]'
        self.track_id = 0
        self.playlists = '{}'
        self.playlist_names = '{}'
        self.script = ''
        self.language = 'eng'
        self.playlist = ''
