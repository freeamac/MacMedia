from flask import render_template
from flask_login import login_required

from . import mini_cds

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
from app.musicmedia.route_utilities import write_out_changes


@mini_cds.route('/')
@login_required
def index():
    """ Main landing page for the Mini CDs library """

    # Write out any pending changes to file
    write_out_changes()

    # The magic here is the template calls the api
    # route to get all the dvds which are rendered
    # via ajax.
    return render_template('musicmedia_main.html', media_str=MediaType.MINI_CD.value)


@mini_cds.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """ Add a new Mini CD to the Mini CDs library """
    return add_media(MediaType.MINI_CD)


@mini_cds.route('/add_track/<int:id>/<int:track_id>', methods=['GET', 'POST'])
@login_required
def add_mini_cd_track(id, track_id):
    """ Add a new track to the Mini CD  """
    return add_track(MediaType.MINI_CD, id, track_id)


@mini_cds.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_mini_cd(id):
    """ Delete Mini CD from the Mini CDs library """
    return delete(MediaType.MINI_CD, id)


@mini_cds.route('/expand/<int:id>', methods=['GET', 'POST'])
@login_required
def expand_mini_cd(id):
    """ Expand to show all information on the Mini CD"""
    return expand(MediaType.MINI_CD, id)


@mini_cds.route('/modify/<int:id>', methods=['GET', 'POST'])
@login_required
def modify_mini_cd(id):
    """ Modify information on the Mini CD in the Mini CDs library """
    return modify(MediaType.MINI_CD, id)


@mini_cds.route('/modify_track/<int:id>/<int:track_id>', methods=['GET', 'POST'])
@login_required
def modify_mini_cd_track(id, track_id):
    """ Modify the data of the Mini CD track """
    return modify_track(MediaType.MINI_CD, id, track_id)


@mini_cds.route('/modify_track_song/<int:id>/<int:track_id>/<int(signed=True):song_id>', methods=['GET', 'POST'])
@login_required
def modify_mini_cd_track_song(id, track_id, song_id):
    """ Modify the data of the song on the Mini CD track """
    return modify_track_song(MediaType.MINI_CD, id, track_id, song_id)
