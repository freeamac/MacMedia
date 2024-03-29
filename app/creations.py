###########
# Handle creation of data objects in the model
###########
from app.exceptions import UniqueNameError
from app.models import DVD
from app.queries import dvd_exists


def db_create_dvd(db, data):
    """ Create the specified new DVD in the library

    :param db:        The database instance
    :type db:         :class:`SQLAlchemy`

    :param data:       Additional data defining the application
    :type data:        dict

    :returns:  The application object created
    :rtype:    class:`models.DVD`
    """

    # Check DVD does not already exist
    if dvd_exists(db, title=data['title'],
                  series=data['series'],
                  year=data['year'],
                  set=data['set'],
                  media_type=data['media_type'],
                  location=data['location']):
        raise UniqueNameError('DVD "{}" with this information already exists in the library'.format(data['title']))

    # Add the new DVD
    new_dvd = DVD(title=data['title'],
                  series=data['series'],
                  year=data['year'],
                  set=data['set'],
                  media_type=data['media_type'],
                  music_type=data['music_type'],
                  artist=data['artist'],
                  location=data['location'])
    db.session.add(new_dvd)
    db.session.commit()

    return new_dvd
