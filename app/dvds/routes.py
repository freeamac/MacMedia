from flask import flash, redirect, render_template, request, url_for

from app.creations import create_dvd

from . import dvds
from .forms import NewDVDForm
from app.queries import get_all_dvds
from app.exceptions import UniqueNameError, ModelNotFound
from app import db


@dvds.route('/')
def index():
    """ Main landing page for the DVDs library """
    
    dvds = get_all_dvds(db)
    print(len(dvds))
    # return render_template('dvds_main.html', dvds=dvds)
    return render_template('dvds_main.html')

@dvds.route('/add/', methods=['GET', 'POST'])
def add_dvd():
    """ Add a new DVD to the list of DVDs """

    form = NewDVDForm()

    if request.method == 'POST':
        if form.cancel.data:
            return redirect(url_for('.index'))

        if form.validate:
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
                new_dvd = create_dvd(db, data)
                if new_dvd is None:
                    flash('Error: Unable to add "{}" to the DVD library'.format(new_dvd.title))
                else:
                    flash('Added "{}" to the DVD library'.format(new_dvd.title))
            except (ModelNotFound, UniqueNameError) as err:
                flash(str(err))
            return redirect(url_for('.index'))

    return render_template('add_new_dvd.html', form=form)

@dvds.route('/delete/<id>')
def delete_dvd():
    """ Delete the DVD from the list """
    return render_template('404.html')

@dvds.route('/modify/<id>')
def modify_dvd():
    """ Modify the data of a DVD """
    return render_template('404.html')

@dvds.route('/search/')
def search_dvds():
    """ Search for DVDs in the list """
    return render_template('404.html')

@dvds.route('/results')
def search_results():
    """ List of DVD search results """
    return render_template('404.html')