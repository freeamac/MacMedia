from flask import render_template
from flask_login import login_required

from . import lps

from app.musicmedia.musicmedia_objects import MediaType
from app.musicmedia.musicmedia_routes import (
    add_media,
    add_track,
    delete,
    expand,
    modify,
    modify_track,
    modify_track_song
)


@lps.route('/')
@login_required
def index():
    """ Main landing page for the LPs library """

    # The magic here is the template calls the api
    # route to get all the dvds which are rendered
    # via ajax.
    return render_template('musicmedia_main.html', media_str=MediaType.LP.value)


@lps.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """ Add a new LP to the LPs library """
    return add_media(MediaType.LP)


@lps.route('/add_track/<int:id>/<int:track_id>', methods=['GET', 'POST'])
@login_required
def add_lp_track(id, track_id):
    """ Add a new track to the LP  """
    return add_track(MediaType.LP, id, track_id)


@lps.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_lp(id):
    """ Delete LP from the LP library """
    return delete(MediaType.LP, id)


@lps.route('/expand/<int:id>', methods=['GET', 'POST'])
@login_required
def expand_lp(id):
    """ Expand to show all information on the LP """
    return expand(MediaType.LP, id)


@lps.route('/modify/<int:id>', methods=['GET', 'POST'])
@login_required
def modify_lp(id):
    """ Modify information on the LP in the LP library """
    return modify(MediaType.LP, id)


@lps.route('/modify_track/<int:id>/<int:track_id>', methods=['GET', 'POST'])
@login_required
def modify_lp_track(id, track_id):
    """ Modify the data of the LP track """
    return modify_track(MediaType.LP, id, track_id)


@lps.route('/modify_track_song/<int:id>/<int:track_id>/<int(signed=True):song_id>', methods=['GET', 'POST'])
@login_required
def modify_lp_track_song(id, track_id, song_id):
    """ Modify the data of the song on the CD track """
    return modify_track_song(MediaType.LP, id, track_id, song_id)