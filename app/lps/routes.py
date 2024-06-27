from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required

from . import lps
from app.musicmedia_objects import (
    Artists,
    LPs,
    MediaType,
    TrackList
)
from .forms import DeleteLPForm, NewLPMetaForm, NewLPTrackForm  # , ModifyLPForm, NewLPForm

from app import app


@lps.route('/')
@login_required
def index():
    """ Main landing page for the LPs library """

    # The magic here is the template calls the api
    # route to get all the dvds which are rendered
    # via ajax.
    return render_template('lps_main.html')


@lps.route('/add/', methods=['GET', 'POST'])
@login_required
def add_lp():
    """ Add a new LP to the list of LPs """

    additional_artists = [{'artist_particle': '', 'additional_artist': ''}] * 5

    form = NewLPMetaForm()
    app.app.logger.info('In add LP - Method: {}'.format(request.method))

    if request.method == 'GET':
        app.app.logger.info('Get method')

        form.lp_title.data = ''
        form.lp_main_artist.data = ''
        form.lp_mixer.data = ''
        form.lp_classical_composer.data = ''

    if request.method == 'POST':
        if form.cancel.data:
            return redirect(url_for('.index'))

        app.app.logger.info('About to validate')
        if form.validate:
            lp_title = form['lp_title'].data.strip()
            lp_artist_str = form['lp_main_artist'].data.strip()
            lp_mixer_str = form['lp_mixer'].data.strip()
            lp_classical_composer_str = form['lp_classical_composer'].data.strip()
            lp_year = form['lp_year'].data
            app.app.logger.info('Title: "{}"'.format(lp_title))
            app.app.logger.info('Artist: "{}"'.format(lp_artist_str))
            app.app.logger.info('Mixer: "{}" len{}'.format(lp_mixer_str, len(lp_mixer_str)))
            if lp_title is None or lp_title == '':
                flash('Error: A title is required for a new LP.')
            elif (lp_artist_str is None or lp_artist_str == '') and (lp_mixer_str is None or lp_mixer_str == ''):
                flash('Error a Main Artist or Mixer is required for a new LP.')
            else:
                if lp_artist_str is not None or lp_artist_str != '':
                    lp_artist = Artists.create_Artist(lp_artist_str)
                else:
                    lp_artist = None
                if lp_mixer_str is not None and lp_mixer_str != '':
                    lp_mixer = Artists.create_Artist(lp_mixer_str)
                    app.app.logger.info('Mixer being set to an Artist: "{}"'.format(lp_mixer_str))
                else:
                    lp_mixer = None
                    app.app.logger.info('Mixer begin set to None: "{}"'.format(lp_mixer_str))
                if lp_classical_composer_str is not None and lp_classical_composer_str != '':
                    lp_classical_composer = Artists.create_Artist(lp_classical_composer_str)
                else:
                    lp_classical_composer = None
                new_lp = LPs.create_LP(media_type=MediaType.LP, title=lp_title, artists=[lp_artist], year=lp_year,
                                       mixer=lp_mixer, classical_composer=lp_classical_composer)
                return redirect(url_for('.add_lp_track', album_id=new_lp.index, track_id=0))

    return render_template('add_new_lp.html', form=form, lp_additional_artists=additional_artists)


@lps.route('/add_track/<int:album_id>/<int:track_id>', methods=['GET', 'POST'])
@login_required
def add_lp_track(album_id, track_id):
    """ Add a new track to the LP  """

    track_songs = [''] * 30
    form = NewLPTrackForm()

    if request.method == "GET":
        form.track_name.data = ''
        form.track_mixer.data = ''

    if request.method == 'POST':
        if form.cancel.data:
            return redirect(url_for('.index'))

        if form.validate:
            track_name = form['track_name'].data.strip()
            track_mixer_str = form['track_mixer'].data.strip()

            if track_name == '':
                track_name = None
            if track_mixer_str is None or track_mixer_str == '':
                track_mixer = None
            else:
                track_mixer = Artists.create_Artist(track_mixer_str)

            # ToDo: Process Songs

            tracklist = TrackList(side_name=track_name, side_mixer_artist=track_mixer)
            LPs().find_by_index(album_id).add_track(tracklist)

            if form.add_track.data:
                track_id += 1
                return redirect(url_for('.add_lp_track', album_id=album_id, track_id=track_id))

            return redirect(url_for('.index'))

    return render_template('add_lp_track.html', form=form, track_songs=track_songs)


"""
        if form.validate():
            data = {}
            data['title'] = form.dvd_title.data
            data['series'] = form.dvd_series.data
            data['year'] = form.dvd_year.data
            data['set'] = form.dvd_set.data
            data['media_type'] = form.dvd_media_type.data.lower()
            if form.dvd_music_type.data == 'No':
                data['music_type'] = False
            else:
                data['music_type'] = True
            data['artist'] = form.dvd_music_artist.data
            data['location'] = form.dvd_location.data.lower()

            try:
                new_dvd = db_create_dvd(db, data)
                if new_dvd is None:
                    flash('Error: Unable to add "{}" to the LP library'.format(new_dvd.title))
                else:
                    flash('Added "{}" to the LP library'.format(new_dvd.title))
            except (ModelNotFound, UniqueNameError) as err:
                flash('ERROR: ' + str(err))
            return redirect(url_for('.index'))
"""


@lps.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_lps(id):
    """ Delete the LP from the list """

    lp_data = LPs.find_by_index(id)
    if lp_data is None:
        flash('ERROR: LP with identifier "{}" not found'.format(id))
        return redirect(url_for('.index'))

    # Set up form
    form = DeleteLPForm()

    if request.method == 'GET':
        form.lp_title.data = lp_data.title
        form.lp_artists.data = lp_data.artists_text
        if lp_data.mixer is not None:
            form.lp_mixer.data = lp_data.mixer
        if lp_data.classical_composer is not None:
            form.lp_classical_composer.data = lp_data.classical_composer
        form.lp_year.data = str(lp_data.year)

    if request.method == 'POST':
        # Take action based on the button pressed

        if form.cancel.data:
            # User cancels form submission
            return redirect(url_for('.index'))

        LPs.delete_lp(lp_data)

        return redirect(url_for('.index'))

    return render_template('delete_lp.html', form=form)


@lps.route('/expand/<int:id>', methods=['GET', 'POST'])
@login_required
def expand_lps(id):
    """ Expand the LP information of the passed LP id. """

    lp_data = LPs.find_by_index(id)
    if lp_data is None:
        flash('ERROR: LP with identifier "{}" not found'.format(id))
        return redirect(url_for('.index'))
    html_str = lp_data.to_html()
    return render_template('expand_lp.html', html_str=html_str)


@lps.route('/modify/<int:id>', methods=['GET', 'POST'])
@login_required
def modify_lps(id):
    """ Modify the data of a LP """

    return render_template('coming_soon.html', library_type='Modify LP')


"""
    dvd_data = get_dvd_by_id(db, id)
    if dvd_data is None:
        flash('ERROR: LP with identifier "{}" not found'.format(id))
        return redirect(url_for('.index'))

    # Set up form
    form = ModifyLPForm()

    if request.method == 'GET':
        form.dvd_title.data = dvd_data.get('title')
        form.dvd_series.data = dvd_data.get('series', '')
        form.dvd_year.data = dvd_data.get('year')
        form.dvd_set.data = dvd_data.get('set', '')
        form.dvd_media_type.data = dvd_data.get('media_type').capitalize()
        form.dvd_music_type.data = dvd_data.get('music_type')
        form.dvd_music_artist.data = dvd_data.get('artist', '')
        form.dvd_location.data = dvd_data.get('location').capitalize()

    if request.method == 'POST':
        # Take action based on the button pressed

        if form.cancel.data:
            # User cancels form submission
            return redirect(url_for('.index'))

        if form.validate():
            dvd_data['id'] = int(id)
            dvd_data['title'] = form.dvd_title.data.strip()
            dvd_data['series'] = form.dvd_series.data.strip()
            dvd_data['year'] = form.dvd_year.data
            dvd_data['set'] = form.dvd_set.data.strip()
            dvd_data['media_type'] = form.dvd_media_type.data.lower()
            if form.dvd_music_type.data.upper() == 'YES':
                dvd_data['music_type'] = True
            else:
                dvd_data['music_type'] = False
            dvd_data['artist'] = form.dvd_music_artist.data.strip()
            dvd_data['location'] = form.dvd_location.data.lower()

            try:
                dvd = db_update_dvd(db, dvd_data)
                if dvd is not None:
                    flash('LP titled "{}" updated'.format(dvd_data['title']))
                else:
                    flash('No changes made to LP titled "{}"'.format(dvd_data['title']))
            except (ModelNotFound, UniqueNameError) as err:
                flash('ERROR: ' + str(err))

            return redirect(url_for('.index'))

    return render_template('modify_dvd.html', form=form)
"""


@lps.route('/search/')
@login_required
def search_dvds():
    """ Search for LPs in the list """
    return render_template('404.html')


@lps.route('/results')
@login_required
def search_results():
    """ List of LP search results """
    return render_template('404.html')
