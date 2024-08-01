from flask import url_for

from . import api
from app import db
from app.musicmedia_objects import LPs
from app.queries import get_all_dvds


@api.route('/dvds')
def dvds_data():
    """ API returning all DVDs in the DVD library  """

    dvds = get_all_dvds(db)
    return {'data': dvds}


@api.route('/lps')
def lps_data():
    """ API returning a summary of all LPs in Music Media library """
    lps_summary = []
    for lp in LPs().lps:
        if lp is None:  # Skip holes in the list due to deletions
            continue
        if lp.artist_particles is None:
            lp_artists = str(lp.artists[0].name)
        else:
            lp_artists = str(lp.artists[0].name)
            for i, particle in enumerate(lp.artist_particles):
                lp_artists += particle + str(lp.artists[i + 1].name)

        if lp.classical_composers is None:
            classical_composers = ''
        else:
            classical_composers = ', '.join([classical_composer.name for classical_composer in lp.classical_composers])
        mixer = '' if lp.mixer is None else str(lp.mixer.name)
        lp_data = {'id': lp.index,
                   'title': lp.title,
                   'artists': lp_artists,
                   'classical_composers': classical_composers,
                   'mixer': mixer,
                   'year': lp.year,
                   'expand_url_title': '<a href="{}">{}</a>'.format(url_for('lps.expand_lps', id=lp.index), lp.title)
                   }
        lps_summary.append(lp_data)
    lps_summary = sorted(lps_summary, key=lambda d: d['title'])

    return {'data': lps_summary}
