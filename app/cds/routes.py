from flask import render_template
from flask_login import login_required

from . import cds

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


@cds.route('/')
@login_required
def index():
    """ Main landing page for the CDs library """

    # The magic here is the template calls the api
    # route to get all the dvds which are rendered
    # via ajax.
    return render_template('musicmedia_main.html', media_str=MediaType.CD.value)


@cds.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """ Add a new CD to the CDs library """
    return add_media(MediaType.CD)


@cds.route('/add_track/<int:id>/<int:track_id>', methods=['GET', 'POST'])
@login_required
def add_cd_track(id, track_id):
    """ Add a new track to the CD  """
    return add_track(MediaType.CD, id, track_id)


@cds.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_cd(id):
    """ Delete CD from the CD library """
    return delete(MediaType.CD, id)


@cds.route('/expand/<int:id>', methods=['GET', 'POST'])
@login_required
def expand_cd(id):
    """ Expand to show all information on the CD """
    return expand(MediaType.CD, id)


@cds.route('/modify/<int:id>', methods=['GET', 'POST'])
@login_required
def modify_cd(id):
    """ Modify information on the CD in the CD library """
    return modify(MediaType.CD, id)


@cds.route('/modify_track/<int:id>/<int:track_id>', methods=['GET', 'POST'])
@login_required
def modify_cd_track(id, track_id):
    """ Modify the data of the CD track """
    return modify_track(MediaType.CD, id, track_id)


@cds.route('/modify_track_song/<int:id>/<int:track_id>/<int(signed=True):song_id>', methods=['GET', 'POST'])
@login_required
def modify_cd_track_song(id, track_id, song_id):
    """ Modify the data of the song on the CD track """
    return modify_track_song(MediaType.CD, id, track_id, song_id)