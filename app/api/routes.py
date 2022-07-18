from . import api
from app import db
from app.queries import get_all_dvds


@api.route('/dvds')
def dvds_data():
    """ API for the DVD library information """

    dvds = get_all_dvds(db)
    return {'data': dvds}
