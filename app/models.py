import enum
import pprint

from flask_login import UserMixin

from app import db as DB


class LocationTypeEnum(enum.Enum):
    home = "home"
    away = "away"

    @staticmethod
    def from_string(s):
        if s.lower() == 'home':
            return LocationTypeEnum.home
        elif s.lower() == 'away':
            return LocationTypeEnum.away
        else:
            raise TypeError('{} is not a valid Location Type'.format(s))


class MediaTypeEnum(enum.Enum):
    dvd = 1
    blueray = 2

    @staticmethod
    def from_string(s):
        if s.lower() == 'dvd':
            return MediaTypeEnum(1)
        elif s.lower() == 'blueray':
            return MediaTypeEnum(2)
        else:
            raise TypeError('{} is not a valid Media Type'.format(s))


DEFAULT_DVD_MEDIA_TYPE = MediaTypeEnum.dvd
DEFAULT_LOCATION_TYPE = LocationTypeEnum.home


class DVD(DB.Model):
    __tablename__ = 'DVD'

    id = DB.Column(DB.Integer, primary_key=True)
    title = DB.Column(DB.String(60), nullable=False)
    series = DB.Column(DB.String(60), default=None, nullable=True)
    year = DB.Column(DB.Integer, nullable=False)
    set = DB.Column(DB.String(60), default=None, nullable=True)
    media_type = DB.Column(DB.Enum(MediaTypeEnum), default=DEFAULT_DVD_MEDIA_TYPE, nullable=False)
    music_type = DB.Column(DB.Boolean, default=False, nullable=False)
    artist = DB.Column(DB.String(60), default=None, nullable=True)
    location = DB.Column(DB.Enum(LocationTypeEnum), default=DEFAULT_LOCATION_TYPE, nullable=False)

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
   user.password = 'pbkdf2:sha256:600000$HnyeSdOCt2RuMZrR$7ace957bbb8626e5ef8e4a17155be146fb723bd16cf248877dfdd4591a245aa3'  # nosec
   db.session.add(user)
   db.session.commit()
   user = User()
   user.username = 'Tomomi'
   user.password = 'pbkdf2:sha256:600000$HnyeSdOCt2RuMZrR$7ace957bbb8626e5ef8e4a17155be146fb723bd16cf248877dfdd4591a245aa3'  # nosec
   db.session.add(user)
   db.session.commit()
