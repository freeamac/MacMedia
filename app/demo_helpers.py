import json
import os

from .models import DVD, Location_Type_Enum, Media_Type_Enum


def load_dvds_data_from_json(db, json_data_file, data_dir=None):
    """ Load in an application and all it's information into the database from the specified json file

    Of course wer are expecting a very specific format for this to work correctly! See below for an example.

    :param db:              The database instance
    :type db:               :class:`SQLAlchemy`

    :param json_data_file:  The file in json format to read and apply to the database
    :type json_data_file:   str

    :param data_dir:        The data directory containing the binaries referenced in the data. For
                            example icons and application packages
    :type data_dir:         str
    """
    if data_dir is not None:
        data_file = os.path.join(data_dir, json_data_file)
    else:
        data_file = json_data_file
    with open(data_file, 'r') as (json_file):
        dvds_json = json.load(json_file)
    load_dvds_data_from_dict(db, dvds_json)


def load_dvds_data_from_dict(db, data_dict):
    """ Load in a DVD and all it's information from the specified dictionary.
    Of course we are expecting a very specific format for this to work correctly! See below for an example.

    :param db:            The database instance
    :type db:             :class:`SQLAlchemy`

    :param data_dict:     The file in json format to read and apply to the database
    :type data_dict:      str
    """
    for dvd in data_dict:
        new_dvd = DVD(title=(dvd.get('title')), series=(dvd.get('series', None)),
                      year=(dvd.get('year')),
                      set=(dvd.get('set', None)),
                      media_type=(dvd.get('media_type', Media_Type_Enum.dvd)),
                      music_type=(dvd.get('music_type', False)),
                      artist=(dvd.get('artist', None)),
                      location=(dvd.get('location', Location_Type_Enum.home)))
        db.session.add(new_dvd)
        db.session.commit()


DVDs_data = [{'title': 'The World Is Not Enough',
              'series': 'James Bond',
              'year': 1999,
              'set': 'James Bond Ultimate Edition',
              'media_type': Media_Type_Enum.dvd,
              'music_type': False,
              'artist': None,
              'location': Location_Type_Enum.home},
             {'title': 'Dr No',
              'series': 'James Bond',
              'year': 1962,
              'set': 'Sean Connery Collection - Volume 1',
              'music_type': False,
              'artist': None,
              'location': Location_Type_Enum.away},
             {'title': 'From Russia With Love',
              'series': 'James Bond',
              'year': 1963,
              'set': 'Sean Connery Collection - Volume 1',
              'music_type': False,
              'artist': None,
              'location': Location_Type_Enum.home},
             {'title': 'Goldfinger',
              'series': 'James Bond',
              'year': 1964,
              'set': 'Sean Connery Collection - Volume 1',
              'music_type': False,
              'artist': None,
              'location': Location_Type_Enum.home},
             {'title': 'Quantum Of Solace',
              'series': 'James Bond',
              'year': 2008,
              'set': None},
             {'title': 'Star Trek',
              'year': 2009,
              'series': 'Star Trek'},
             {'title': 'The Chronicles Of Riddick',
              'year': 2004,
              'series': 'Riddick'}]


def load_demo_data(db):
    """ Load the demo application data into the database """
    load_dvds_data_from_dict(db, DVDs_data)


def dump_demo_data(demo_data_outfile):
    """ Quick utility to dump the demo data information to a file in json format """
    with open(demo_data_outfile, 'w') as (fp):
        json.dump(DVDs_data, fp)
