from flask import render_template

from . import dvds
from app.queries import get_all_dvds
from app import db


@dvds.route('/')
def index():
    """ Main landing page for the DVDs library """
    
    dvds = get_all_dvds(db)
    print(len(dvds))
    # return render_template('dvds_main.html', dvds=dvds)
    return render_template('dvds_main.html')

@dvds.route('/add/')
def add_dvd():
    """ Add a new DVD to the list of DVDs """
    return render_template('404.html')

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