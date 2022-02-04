from flask import render_template

from . import api
from app.queries import get_all_dvds
from app import db


@api.route('/dvds')
def dvds_data():
    """ API for the DVDs library information """
    
    dvds = get_all_dvds(db)
    return {'data': dvds}