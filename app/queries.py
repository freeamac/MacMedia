from .models import DVD, User


def get_all_dvds(db):
    """ Return a list of all the DVDs in the database.

    Each entry in the list will be a dictionary containing
    the returned information of one unique DVD in the database.

    If no DVDs are found, an empty list will be returned.

    :param db:        The database instance
    :type db:         :class:`SQLAlchemy`

    :returns:  All platforms information
    :rtype:    list(dict)
    """

    dvds = db.session.query(DVD).all()

    return [dvd.to_dict() for dvd in dvds]


def get_dvd_by_id(db, id, model=False):
    """ Return the DVD with the specified id. If not found, return None.

    :param db:        The database instance
    :type db:         :class:`SQLAlchemy`

    :param model:     Indicate if the model instead of the dictionary representation
                      should be returned
    :type model:      `bool`

    :returns:  All platforms information
    :rtype:    `dict` or class:`models.DVD`
    """

    dvd = db.session.query(DVD).filter_by(id=id).first()
    if dvd is None:
        return None
    elif model:
        return dvd
    else:
        return dvd.to_dict()


def dvd_exists(db, title, series=None, year=None, set=None, media_type=None):
    """ Returns True if the DVD already exists in the database

    :param db:        The database instance
    :type db:         :class:`SQLAlchemy`

    :returns:         If DVD exists in library
    :rtype:           `bool`
    """

    if title is None or title == '':
        raise ModuleNotFoundError('DVD title must not be blank.')

    query_args = {'title': title}
    if series == '':
        query_args['series'] = None
    else:
        query_args['series'] = series
    query_args['year'] = year
    if set == '':
        query_args['set'] = None
    else:
        query_args['set'] = set
    query_args['media_type'] = media_type

    result = db.session.query(DVD).filter_by(**query_args).first()
    return result is not None


def get_user(db, username):
    """ Return the specified username's information

    :param db:        The database instance
    :type db:         :class:`SQLAlchemy`

    :param username:  The username's information to return
    :type username:   `str`

    :returns:         The usernames' information or None
    :rtye:            :class:`models.User`
    """

    user = db.session.query(User).filter_by(username=username).first()
    return user
