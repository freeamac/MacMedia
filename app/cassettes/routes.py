from flask import render_template
from flask_login import login_required

from . import cassettes

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


@cassettes.route('/')
@login_required
def index():
    """ Main landing page for the Cassettes library """

    # Write out any pending changes to file
    write_out_changes()

    # The magic here is the template calls the api
    # route to get all the dvds which are rendered
    # via ajax.
    return render_template('musicmedia_main.html', media_str=MediaType.CASSETTE.value)


@cassettes.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """ Add a new cassette to the Cassettes library """
    return add_media(MediaType.CASSETTE)


@cassettes.route('/add_track/<int:id>/<int:track_id>', methods=['GET', 'POST'])
@login_required
def add_cassette_track(id, track_id):
    """ Add a new track to the cassette """
    return add_track(MediaType.CASSETTE, id, track_id)


@cassettes.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_cassette(id):
    """ Delete cassette from the Cassettes library """
    return delete(MediaType.CASSETTE, id)


@cassettes.route('/expand/<int:id>', methods=['GET', 'POST'])
@login_required
def expand_cassette(id):
    """ Expand to show all information on the cassette """
    return expand(MediaType.CASSETTE, id)


@cassettes.route('/modify/<int:id>', methods=['GET', 'POST'])
@login_required
def modify_cassette(id):
    """ Modify information on the cassette in the Cassettes library """
    return modify(MediaType.CASSETTE, id)


@cassettes.route('/modify_track/<int:id>/<int:track_id>', methods=['GET', 'POST'])
@login_required
def modify_cassette_track(id, track_id):
    """ Modify the data of the cassette track """
    return modify_track(MediaType.CASSETTE, id, track_id)


@cassettes.route('/modify_track_song/<int:id>/<int:track_id>/<int(signed=True):song_id>', methods=['GET', 'POST'])
@login_required
def modify_cassette_track_song(id, track_id, song_id):
    """ Modify the data of the song on the cassette track """
    return modify_track_song(MediaType.CASSETTE, id, track_id, song_id)
