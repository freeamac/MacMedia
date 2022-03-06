from flask import render_template

from . import cds


@cds.route('/cds/')
def index():
    """ Main landing page for the CDs library """
    library_type = "Music CDs"
    return render_template('coming_soon.html', library_type=library_type)
