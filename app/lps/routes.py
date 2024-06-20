from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required

from . import lps
from app.musicmedia_objects import (
    LPs
)
from .forms import DeleteLPForm  # , ModifyLPForm, NewLPForm


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
    return render_template('coming_soon.html', library='Add LP')


"""
    form = NewLPForm()

    if request.method == 'POST':
        if form.cancel.data:
            return redirect(url_for('.index'))

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

    return render_template('add_new_dvd.html', form=form)
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
        if lp_data.artist_particles is None:
            form.lp_artists.data = str(lp_data.artists[0].name)
        else:
            lp_artists = str(lp_data.artists[0].name)
            for i, particle in enumerate(lp_data.artist_particles):
                lp_artists += particle + str(lp_data.artists[i + 1].name)
            form.lp_artists.data = lp_artists
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
