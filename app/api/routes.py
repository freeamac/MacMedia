from flask import url_for

from . import api
from app import db
from app.musicmedia_objects import CDs, ELPs, LPs, MINI_CDs, MediaException, MediaType
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


@api.route('/musicmedia_data/<media_type>', methods=['GET'])
def musicmedia_data(media_type):
    """ API returning a summary of all music media of the specified type in Music Media library """
    musicmedia_summary = []
    if media_type == MediaType.LP.value:
        musicmedia_list = LPs().lps
    elif media_type == MediaType.CD.value:
        musicmedia_list = CDs().cds
    elif media_type == MediaType.ELP.value:
        musicmedia_list = ELPs().elps
    elif media_type == MediaType.MINI_CD.value:
        musicmedia_list = MINI_CDs().mini_cds
    else:
        raise MediaException('Unknown Music Media Type: {}'.format(media_type))

    for musicmedia in musicmedia_list:
        if musicmedia is None:  # Skip holes in the list due to deletions
            continue
        if musicmedia.artist_particles is None:
            artists = str(musicmedia.artists[0].name)
        else:
            artists = str(musicmedia.artists[0].name)
            for i, particle in enumerate(musicmedia.artist_particles):
                if i == len(musicmedia.artists) - 1:
                    # Handle dangling particle
                    artists += particle
                else:
                    artists += particle + str(musicmedia.artists[i + 1].name)

        if musicmedia.classical_composers is None:
            classical_composers = ''
        else:
            classical_composers = ', '.join([classical_composer.name for classical_composer in musicmedia.classical_composers])
        mixer = '' if musicmedia.mixer is None else str(musicmedia.mixer.name)
        media_data = {'id': musicmedia.index,
                      'title': musicmedia.title,
                      'artists': artists,
                      'classical_composers': classical_composers,
                      'mixer': mixer,
                      'year': musicmedia.year,
                      'expand_url_title': '<a href="{}">{}</a>'.format(url_for(media_type + 's.expand_' + media_type, id=musicmedia.index), musicmedia.title)
                      }
        musicmedia_summary.append(media_data)
    musicmedia_summary = sorted(musicmedia_summary, key=lambda d: d['title'])

    return {'data': musicmedia_summary}