from flask import render_template

from . import lps


@lps.route('/lps/')
def index():
    """ Main landing page for the LPs library """
    library_type = "Music LPs"
    return render_template('coming_soon.html', library_type=library_type)