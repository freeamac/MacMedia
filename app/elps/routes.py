from flask import render_template
from flask_login import login_required

from . import elps

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


@elps.route('/')
@login_required
def index():
    """ Main landing page for the ELPs library """

    # The magic here is the template calls the api
    # route to get all the dvds which are rendered
    # via ajax.
    return render_template('musicmedia_main.html', media_str=MediaType.ELP.value)


@elps.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """ Add a new ELP to the ELPs library """
    return add_media(MediaType.ELP)


@elps.route('/add_track/<int:id>/<int:track_id>', methods=['GET', 'POST'])
@login_required
def add_elp_track(id, track_id):
    """ Add a new track to the ELP  """
    return add_track(MediaType.ELP, id, track_id)


@elps.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_elp(id):
    """ Delete ELP from the ELPs library """
    return delete(MediaType.ELP, id)


@elps.route('/expand/<int:id>', methods=['GET', 'POST'])
@login_required
def expand_elp(id):
    """ Expand to show all information on the ELP """
    return expand(MediaType.ELP, id)


@elps.route('/modify/<int:id>', methods=['GET', 'POST'])
@login_required
def modify_elp(id):
    """ Modify information on the ELP in the ELPs library """
    return modify(MediaType.ELP, id)


@elps.route('/modify_track/<int:id>/<int:track_id>', methods=['GET', 'POST'])
@login_required
def modify_elp_track(id, track_id):
    """ Modify the data of the ELP track """
    return modify_track(MediaType.ELP, id, track_id)


@elps.route('/modify_track_song/<int:id>/<int:track_id>/<int(signed=True):song_id>', methods=['GET', 'POST'])
@login_required
def modify_elp_track_song(id, track_id, song_id):
    """ Modify the data of the song on the ELP track """
    return modify_track_song(MediaType.ELP, id, track_id, song_id)
