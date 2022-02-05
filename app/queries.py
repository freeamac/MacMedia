from .models import DVDs

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

    dvds = db.session.query(DVDs).all()

    return [dvd.to_dict() for dvd in dvds]
    

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
    if series is not None and series != '':
        query_args['series'] = series
    if year is not None:
        query_args['year'] = year
    if set is not None and set != '':
        query_args['series'] = series
    if media_type is not None:
        query_args['media_type'] = media_type

    result = db.session.query(DVDs).filter_by(**query_args).first()
    return result is not None