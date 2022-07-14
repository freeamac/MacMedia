###########
# Handle updates of data objects in the model
###########
from werkzeug.security import generate_password_hash

from app.exceptions import InvalidAdministrator, ModelNotFound, UniqueNameError, UpdateError, ResourceNotFound  # noqa
from app.models import Media_Type_Enum, User
from app.queries import dvd_exists, get_dvd_by_id


def db_update_dvd(db, dvd_data):
    """ Update the DVD with any new information in the passed DVD data dictionary

    If there is no new information, None is returned.

    :param db:        The database instance
    :type db:         :class:`SQLAlchemy`

    :param dvd_data:  Dictionary containing the information about the DVD. Each key
                      is a column in the model with the corresponding value.
    :type dvd_data:   `dict`

    :returns:         Updated model
    :rtype:           class:`models.DVD`
    """

    # First ensure the modified data does not represent and existing DVD in the library
    query_args = {}
    query_args['title'] = dvd_data['title']
    if dvd_data['series'] == '':
        query_args['series'] = None
    else:
        query_args['series'] = dvd_data['series']
    query_args['year'] = dvd_data['year']
    if dvd_data['set'] == '':
        query_args['set'] = None
    else:
        query_args['set'] = dvd_data['set']
    query_args['media_type'] = dvd_data['media_type']

    if dvd_exists(db, ** query_args):
        raise UniqueNameError('DVD "{}" with this information already exists in library. Cannot save to an existing DVD'.format(dvd_data['title']))

    # Ensure there are changes to commit
    current_dvd = get_dvd_by_id(db, dvd_data['id'], model=True)
    if current_dvd.to_dict() == dvd_data:
        return None

    # Re-use query args from above where empty string conversions have already been handled
    current_dvd.title = query_args['title']
    current_dvd.series = query_args['series']
    current_dvd.year = query_args['year']
    current_dvd.set = query_args['set']

    current_dvd.media_type = Media_Type_Enum.from_string(dvd_data['media_type'])
    if dvd_data['music_type'] == 'No':
        current_dvd.music_type = False
    elif dvd_data['music_type'] == 'Yes':
        current_dvd.music_type = True
    else:
        current_dvd.music_type = dvd_data['music_type']
    if dvd_data['artist'] == '':
        current_dvd.artist = None
    else:
        current_dvd.artist = dvd_data['artist']
    db.session.commit()
    return current_dvd


def db_update_user_password(db, username, password):
    """ Update the hashed password for the specified username

    :param db:        The database instance
    :type db:         :class:`SQLAlchemy`

    :param username:  The username to update the password for
    :type username:   `str`

    :param password:  The new password
    :type password:   `str`
    """
    user = db.session.query(User).filter_by(username=username).first()
    if user is not None:
        user.password = generate_password_hash(password)
        db.session.commit()
