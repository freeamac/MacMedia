import enum
import pprint

from app import db as DB


class Media_Type_Enum(enum.Enum):
    dvd = 1
    blueray = 2


class DVDs(DB.Model):
    __tablename__ = 'DVDs'

    id = DB.Column(DB.Integer, primary_key=True)
    title = DB.Column(DB.String(60), nullable=False)
    series = DB.Column(DB.String(60), default=None, nullable=True)
    year = DB.Column(DB.Integer, nullable=False)
    set = DB.Column(DB.String(60), default=None, nullable=True)
    media_type = DB.Column(DB.Enum(Media_Type_Enum), default=Media_Type_Enum.dvd, nullable=False)
    music_type = DB.Column(DB.Boolean, default=False, nullable=False)
    artist =  DB.Column(DB.String(60), default=None, nullable=True)

    def to_dict(self) -> dict:
        result = {}
        result['id'] = self.id
        result['title'] = self.title
        result['series'] = self.series
        result['year'] = self.year
        result['set'] = self.set
        result['media_type'] = str(self.media_type.name)
        result['music_type'] = self.music_type
        result['artist'] = self.artist
        return result

    def __repr__(self) -> str:
        return pprint.pformat(self.to_dict())