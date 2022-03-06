from flask import render_template

from . import cassettes


@cassettes.route('/cassettes/')
def index():
    """ Main landing page for the Cassettes library """
    library_type = "Music Cassettes"
    return render_template('coming_soon.html', library_type=library_type)
