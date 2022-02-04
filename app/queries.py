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
    