from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required

from . import dvds
from .forms import DeleteDVDForm, ModifyDVDForm, NewDVDForm
from app import db
from app.creations import db_create_dvd
from app.deletions import db_delete_dvd
from app.exceptions import UniqueNameError, ModelNotFound
from app.queries import get_dvd_by_id
from app.updates import db_update_dvd


@dvds.route('/')
@login_required
def index():
    """ Main landing page for the DVD library """

    # dvds = get_all_dvds(db)
    # return render_template('dvds_main.html', dvds=dvds)
    return render_template('dvds_main.html')


@dvds.route('/add/', methods=['GET', 'POST'])
@login_required
def add_dvd():
    """ Add a new DVD to the list of DVDs """

    form = NewDVDForm()

    if request.method == 'POST':
        if form.cancel.data:
            return redirect(url_for('.index'))

        if form.validate():
            data = {}
            data['title'] = form.dvd_title.data
            data['series'] = form.dvd_series.data
            data['year'] = form.dvd_year.data
            data['set'] = form.dvd_set.data
            data['media_type'] = form.dvd_media_type.data
            if form.dvd_music_type.data == 'No':
                data['music_type'] = False
            else:
                data['music_type'] = True
            data['artist'] = form.dvd_music_artist.data

            try:
                new_dvd = db_create_dvd(db, data)
                if new_dvd is None:
                    flash('Error: Unable to add "{}" to the DVD library'.format(new_dvd.title))
                else:
                    flash('Added "{}" to the DVD library'.format(new_dvd.title))
            except (ModelNotFound, UniqueNameError) as err:
                flash('ERROR: ' + str(err))
            return redirect(url_for('.index'))

    return render_template('add_new_dvd.html', form=form)


@dvds.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_dvd(id):
    """ Delete the DVD from the list """

    dvd_data = get_dvd_by_id(db, id)
    if dvd_data is None:
        flash('ERROR: DVD with identifier "{}" not found'.format(id))
        return redirect(url_for('.index'))

    # Set up form
    form = DeleteDVDForm()

    if request.method == 'GET':
        form.dvd_title.data = dvd_data.get('title')
        form.dvd_series.data = dvd_data.get('series', '')
        form.dvd_year.data = str(dvd_data.get('year'))
        form.dvd_set.data = dvd_data.get('set', '')
        form.dvd_media_type.data = dvd_data.get('media_type').capitalize()
        form.dvd_music_type.data = dvd_data.get('music_type')
        form.dvd_music_artist.data = dvd_data.get('artist', '')

    if request.method == 'POST':
        # Take action based on the button pressed

        if form.cancel.data:
            # User cancels form submission
            return redirect(url_for('.index'))

        db_delete_dvd(db, dvd_data['id'])

        return redirect(url_for('.index'))

    return render_template('delete_dvd.html', form=form)


@dvds.route('/modify/<int:id>', methods=['GET', 'POST'])
@login_required
def modify_dvd(id):
    """ Modify the data of a DVD """

    dvd_data = get_dvd_by_id(db, id)
    if dvd_data is None:
        flash('ERROR: DVD with identifier "{}" not found'.format(id))
        return redirect(url_for('.index'))

    # Set up form
    form = ModifyDVDForm()

    if request.method == 'GET':
        form.dvd_title.data = dvd_data.get('title')
        form.dvd_series.data = dvd_data.get('series', '')
        form.dvd_year.data = dvd_data.get('year')
        form.dvd_set.data = dvd_data.get('set', '')
        form.dvd_media_type.data = dvd_data.get('media_type').capitalize()
        form.dvd_music_type.data = dvd_data.get('music_type')
        form.dvd_music_artist.data = dvd_data.get('artist', '')

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

            try:
                dvd = db_update_dvd(db, dvd_data)
                if dvd is not None:
                    flash('DVD titled "{}" updated'.format(dvd_data['title']))
                else:
                    flash('No changes made to DVD titled "{}"'.format(dvd_data['title']))
            except (ModelNotFound, UniqueNameError) as err:
                flash('ERROR: ' + str(err))

            return redirect(url_for('.index'))

    return render_template('modify_dvd.html', form=form)


@dvds.route('/search/')
@login_required
def search_dvds():
    """ Search for DVDs in the list """
    return render_template('404.html')


@dvds.route('/results')
@login_required
def search_results():
    """ List of DVD search results """
    return render_template('404.html')
