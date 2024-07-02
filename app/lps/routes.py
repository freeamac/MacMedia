from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required

from . import lps
from app.musicmedia_objects import (
    Additional_Artist,
    Artists,
    LPException,
    LPs,
    MediaType,
    Song,
    TrackList,
    media_to_hash
)
from .forms import DeleteLPForm, NewLPMetaForm, NewLPTrackForm  # , ModifyLPForm, NewLPForm

from app import app


def field_value_or_none(form, field):
    """ Return the field value on the form or None if empty """
    value = form[field].data.strip()
    if value is not None and value != '':
        return value


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

    if request.method == 'GET':
        form.lp_title.data = ''
        form.lp_main_artist.data = ''
        form.lp_mixer.data = ''
        form.lp_classical_composer.data = ''

    if request.method == 'POST':
        if form.cancel.data:
            return redirect(url_for('.index'))

        if form.validate:
            lp_title = form['lp_title'].data.strip()
            lp_artist_str = form['lp_main_artist'].data.strip()
            lp_additional_artists = form['lp_additional_artists']
            lp_mixer_str = form['lp_mixer'].data.strip()
            lp_classical_composer_str = form['lp_classical_composer'].data.strip()
            lp_year = form['lp_year'].data
            if lp_title is None or lp_title == '':
                flash('Error: A title is required for a new LP.')
            elif (lp_artist_str is None or lp_artist_str == '') and (lp_mixer_str is None or lp_mixer_str == ''):
                flash('Error a Main Artist or Mixer is required for a new LP.')

            # Check LP  does not already exist
            lp_unique = True
            results = LPs.find_lp_by_title(lp_title)
            if len(results) > 0:
                # Need to check hash id
                new_album_hash = media_to_hash(MediaType.LP, lp_title, lp_artist_str)
                for result in results:
                    if result._hash == new_album_hash:
                        lp_unique = False
                        flash('LP already exists in music media library!')
            if lp_unique:
                # Start processing the new album data
                if lp_artist_str is not None or lp_artist_str != '':
                    lp_artists = [Artists.create_Artist(lp_artist_str)]
                    if lp_additional_artists is None:
                        lp_artist_particles = None
                    else:
                        lp_artist_particles = []
                        for artist_info in lp_additional_artists:
                            particle = artist_info['additional_artist_particle'].data  # Awkward: Need to maintain spacing
                            additional_artist_str = artist_info['additional_artist'].data.strip()
                            if additional_artist_str is None or additional_artist_str == '':
                                continue
                            lp_artist_particles.append(particle)
                            additional_artist = Artists.create_Artist(additional_artist_str)
                            lp_artists.append(additional_artist)
                else:
                    lp_artists = None
                    lp_artist_particles = None
                if lp_mixer_str is not None and lp_mixer_str != '':
                    lp_mixer = Artists.create_Artist(lp_mixer_str)
                else:
                    lp_mixer = None
                if lp_classical_composer_str is not None and lp_classical_composer_str != '':
                    lp_classical_composer = Artists.create_Artist(lp_classical_composer_str)
                else:
                    lp_classical_composer = None

                new_lp = LPs.create_LP(media_type=MediaType.LP,
                                       title=lp_title,
                                       artists=lp_artists,
                                       year=lp_year,
                                       mixer=lp_mixer,
                                       classical_composer=lp_classical_composer,
                                       artist_particles=lp_artist_particles)
                return redirect(url_for('.add_lp_track', album_id=new_lp.index, track_id=0))

    return render_template('add_new_lp.html', form=form, lp_additional_artists=additional_artists)


@lps.route('/add_track/<int:album_id>/<int:track_id>', methods=['GET', 'POST'])
@login_required
def add_lp_track(album_id, track_id):
    """ Add a new track to the LP  """

    track_songs = [{'song_title': ''}] * 30
    track_songs_additional_artists = [{'song_additional_artist': ''}] * 3
    track_song_classical_composers = [{'song_classical_composer': ''}] * 2
    form = NewLPTrackForm()

    if request.method == "GET":
        form.track_name.data = ''
        form.track_mixer.data = ''

    if request.method == 'POST':
        if form.cancel.data:
            return redirect(url_for('.index'))

        if form.validate:
            lp = LPs.find_by_index(album_id)
            all_song_artists = set()
            track_name = form['track_name'].data.strip()
            track_mixer_str = form['track_mixer'].data.strip()
            track_song_fields = form['track_songs']

            if track_name == '':
                track_name = None
            if track_mixer_str is None or track_mixer_str == '':
                track_mixer = None
            else:
                track_mixer = Artists.create_Artist(track_mixer_str)
                all_song_artists.add(track_mixer)

            songs = []
            for song_num, song_field in enumerate(track_song_fields):
                song_title_str = song_field['song_title'].data.strip()
                if song_title_str is None or song_title_str == '':
                    continue

                # Handle simple song fields
                song_mix = field_value_or_none(song_field, 'song_mix')
                song_featured_in = field_value_or_none(song_field, 'song_featured_in')
                list_main_artist = song_field['song_list_main_artist'].data
                song_country = field_value_or_none(song_field, 'song_country')

                # Cleanly handle year of song which could be invalid
                song_year = field_value_or_none(song_field, 'song_year')
                if song_year is not None:
                    try:
                        song_year = int(song_year)
                    except ValueError:
                        flash('Error: Year in Song #{} is not an integer.'.format(song_num + 1))
                        return render_template('add_lp_track.html', form=form, track_songs=track_songs,
                                               track_songs_additional_artists=track_songs_additional_artists,
                                               track_song_classical_composers=track_song_classical_composers)

                # Handle additional song artists
                song_additional_artists = []
                additional_artists = song_field['song_additional_artists']
                for additional_artist in additional_artists:
                    additional_artist_str = field_value_or_none(additional_artist, 'additional_artist')
                    if additional_artist_str is None:
                        continue
                    additional_artist_prequel = field_value_or_none(additional_artist, 'additional_artist_prequel')
                    additional_artist_sequel = field_value_or_none(additional_artist, 'additional_artist_sequel')
                    artist = Artists.create_Artist(additional_artist_str)
                    song_additional_artist = Additional_Artist(artist=artist, sequel=additional_artist_sequel, prequel=additional_artist_prequel)
                    song_additional_artists.append(song_additional_artist)
                    all_song_artists.add(artist)
                if song_additional_artists == []:
                    song_additional_artists = None

                # Handle classical musical aspects of a song
                song_classical_composers = []
                song_classical_work = field_value_or_none(song_field, 'song_classical_work')
                classical_composers = song_field['song_classical_composers']
                for classical_composer in classical_composers:
                    classical_composer_str = field_value_or_none(classical_composer, 'classical_composer')
                    if classical_composer_str is None:
                        continue
                    song_classical_composer = Artists.create_Artist(classical_composer_str)
                    song_classical_composers.append(song_classical_composer)
                    all_song_artists.add(song_classical_composer)
                song_classical_composers = None if song_classical_composers == [] else song_classical_composers

                # Handle song parts
                song_parts_text = song_field['song_parts'].data
                if song_parts_text is not None and song_parts_text != '':
                    song_parts = []
                    song_parts_lines = song_parts_text.split('\n')
                    for line in song_parts_lines:
                        song_parts.append(line.strip())
                else:
                    song_parts = None

                if song_additional_artists is not None:
                    main_artist = song_additional_artists[0].artist
                elif lp.artists != []:
                    main_artist = lp.artists[0]
                else:
                    main_artist = None

                song = Song(title=song_title_str,
                            main_artist=main_artist,
                            exp_main_artist=list_main_artist,
                            album=lp.title,
                            additional_artists=song_additional_artists,
                            classical_composers=song_classical_composers,
                            classical_work=song_classical_work,
                            country=song_country,
                            year=song_year,
                            mix=song_mix,
                            featured_in=song_featured_in,
                            parts=song_parts)
                songs.append(song)

            tracklist = TrackList(side_name=track_name, side_mixer_artist=track_mixer, songs=songs)
            lp.add_track(tracklist)

            # Add the LP to all Artists referenced on this track
            if all_song_artists != set():
                for artist in all_song_artists:
                    try:
                        artist.add_media(lp)
                    except LPException as e:
                        app.app.logger.info('LP Exception {} ignored. Assumed to be associated with multiple songs'.format(e))

            if form.add_track.data:
                track_id += 1
                return redirect(url_for('.add_lp_track', album_id=album_id, track_id=track_id))

            return redirect(url_for('.index'))

    return render_template('add_lp_track.html', form=form, track_songs=track_songs,
                           track_songs_additional_artists=track_songs_additional_artists,
                           track_song_classical_composers=track_song_classical_composers)


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
