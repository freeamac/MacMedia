###########
# Handle creation of data objects in the model
###########
from app.queries import get_dvd_by_id


def db_delete_dvd(db, id):
    """ Delete the specified DVD in the library

    :param db:        The database instance
    :type db:         :class:`SQLAlchemy`

    :param id:        Id of the DVD to delete
    :type data:       `str`
    """
    dvd = get_dvd_by_id(db, id, model=True)
    db.session.delete(dvd)
    db.session.commit()