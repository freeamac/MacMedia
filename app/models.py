import enum
import pprint

from flask_login import UserMixin

from app import db as DB


class Location_Type_Enum(enum.Enum):
    home = 1
    away = 2

    @staticmethod
    def from_string(s):
        if s.lower() == 'home':
            return Location_Type_Enum(1)
        elif s.lower() == 'away':
            return Location_Type_Enum(2)
        else:
            raise TypeError('{} is not a valid Location Type'.format(s))


class Media_Type_Enum(enum.Enum):
    dvd = 1
    blueray = 2

    @staticmethod
    def from_string(s):
        if s.lower() == 'dvd':
            return Media_Type_Enum(1)
        elif s.lower() == 'blueray':
            return Media_Type_Enum(2)
        else:
            raise TypeError('{} is not a valid Media Type'.format(s))


DEFAULT_DVD_MEDIA_TYPE = Media_Type_Enum.dvd
DEFAULT_LOCATION_TYPE = Location_Type_Enum.home


class DVD(DB.Model):
    __tablename__ = 'DVD'

    id = DB.Column(DB.Integer, primary_key=True)
    title = DB.Column(DB.String(60), nullable=False)
    series = DB.Column(DB.String(60), default=None, nullable=True)
    year = DB.Column(DB.Integer, nullable=False)
    set = DB.Column(DB.String(60), default=None, nullable=True)
    media_type = DB.Column(DB.Enum(Media_Type_Enum), default=DEFAULT_DVD_MEDIA_TYPE, nullable=False)
    music_type = DB.Column(DB.Boolean, default=False, nullable=False)
    artist = DB.Column(DB.String(60), default=None, nullable=True)
    location = DB.Column(DB.Enum(Location_Type_Enum), default=DEFAULT_LOCATION_TYPE, nullable=False)

    def to_dict(self) -> dict:
        result = {}
        result['id'] = self.id
        result['title'] = self.title
        result['series'] = self.series
        result['year'] = self.year
        result['set'] = self.set
        result['media_type'] = str(self.media_type.name)
        if self.music_type:
            result['music_type'] = 'Yes'
        else:
            result['music_type'] = 'No'
        result['artist'] = self.artist
        result['location'] = str(self.location.name)
        return result

    def __repr__(self) -> str:
        return pprint.pformat(self.to_dict())


class User(UserMixin, DB.Model):
    __tablename__ = 'USERS'

    id = DB.Column(DB.Integer, primary_key=True)
    username = DB.Column(DB.String(60), nullable=False)
    password = DB.Column(DB.String(256), nullable=False)

    def to_dict(self) -> dict:
        result = {}
        result['id'] = self.id
        result['username'] = self.username
        result['password'] = self.password
        return result


def load_initial_users(db):
   user = User()
   user.username = 'Andy'
   user.password = 'pbkdf2:sha256:260000$s4wuv5pHJy7TwTYL$e52ee054fc1364bd00a069b2d9301ac70813f174cca00bc95a3c0e233782935e'  # nosec
   db.session.add(user)
   db.session.commit()
   user = User()
   user.username = 'Tomomi'
   user.password = 'pbkdf2:sha256:260000$s4wuv5pHJy7TwTYL$e52ee054fc1364bd00a069b2d9301ac70813f174cca00bc95a3c0e233782935e'  # nosec
   db.session.add(user)
   db.session.commit()
