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
from .forms import (
    DeleteLPForm,
    ModifyLPMetaForm,
    ModifyLPTrackForm,
    ModifySongForm,
    NewLPMetaForm,
    NewLPTrackForm
)

from app import app


class FormValidateException(Exception):
    pass


def field_value_or_none(form, field):
    """ Return the field value on the form or None if empty.

        None that the field value is stripped of surrounding white space.

        :param form:   The form to query.
        :type form:    :class:`wtforms.Form`

        :param field:  Field of the form to query. The key of the form dict to query.
        :type field:   str

        : returns:     The field value or None if empty
        :rtype:        str | None
    """
    value = form[field].data.strip()
    if value is not None and value != '':
        return value


def name_value_or_blank(data_value):
    """ Return the Artist's name or '' if the Artist is set to None.

        :param data_value:  The Artist whose name is checked
        :type data_value:   :class:`_Artist`

        :returns:           The Artist's name or '' if the Artist is None
        :rtype:             str
    """
    return '' if data_value is None else data_value.name


def massage_particle(particle):
    """ Massage an Artist particle to the correct format.

        For word particles, we want to surround them with spaces. In the case
        of a comma, we only want a space at the end.

        :param particle:  The Artist particle to format
        :type particle:   str

        :returns:         The correctly formatted Artist particle
        :rtype:           srt
    """
    massaged_particle = ''
    if particle is not None and particle != '':
        if particle == ',':
            massaged_particle = ', '
        else:
            massaged_particle = ' ' + particle + ' '
    return massaged_particle


def build_additional_artist_tuples(additional_artists):
    """ Build all the additional artist info list and tuples (prequels, names, sequels).

        :param additional_artists:   A list of Additional Artists information
        :type additional_artists:    list(:class:`Additional_Artist`)

        :returns:                    A tuple containing a list of Additional Artists info, a tuple of
                                     the Additional Artists' prequels, a tuple of the Additinal Artists' names,
                                     a tuple of the Additional Artists' sequels
        :rtype:                      tuple(list(dict()), tuple(str), tuple(str), tuple(str))
    """
    additional_artists_prequels = []
    additional_artists_names = []
    additional_artists_sequels = []
    additional_artists_info = []
    if additional_artists is not None:

        for additional_artist in additional_artists:
            additional_artists_info.append({'additional_artist_prequel': additional_artist.prequel,
                                            'additional_artist': additional_artist.artist.name,
                                            'additional_artist_sequel': additional_artist.sequel})
            additional_artists_prequels.append(additional_artist.prequel)
            additional_artists_names.append(additional_artist.artist.name)
            additional_artists_sequels.append(additional_artist.seequel)
    additional_artists_prequel_tuple = tuple(additional_artists_prequels)
    additional_artists_name_tuple = tuple(additional_artists_names)
    additional_artists_sequel_tuple = tuple(additional_artists_sequels)

    return additional_artists_info, additional_artists_prequel_tuple, additional_artists_name_tuple, additional_artists_sequel_tuple


def build_classical_composer_names_tuple(classical_composers):
    """ Build a tuple of the classical composer names

    :param classical_composers:  The list of classical composers
    :type classical_composers:   list(:class:`_Artist`)

    :returns:                    A tuple of the classical composer names
    :rtype:                      tuple(str)
    """
    classical_composer_names = []
    if classical_composers is not None:
        for composer in classical_composers:
            classical_composer_names.append(composer.name)
    classical_composers_name_tuple = tuple(classical_composer_names)
    return classical_composers_name_tuple


def replace_artist(artist_element, new_artist_name, lp_data):
    """ Replace the Artist in the passed element (eg. Song, LP, etc) with a newly constructed Artist.

        The replacement also requires an update to associated LP information. This means remove the LP
        from the old Artist, create a new Artist, replace the old with the new Artist and add associate
        the LP with the new Artist.

        :param artist_element:  The element which is associated with the Artist
        :type artist_element:   class:`_Artist`

        :param new_artist_name:  The name of the new Artist to create
        :type new_artist_name:   str

        :param lp_data:          The LP to remove from the old Artist and add to the new Artist
        :type lp_data:           :class:`_LP`

        :raises Exception:       Only class:`LPException` is caught when adding the LP to the new Artist
                                 under the assumption the Artist may have already be associated on another
                                 song or the LP
    """
    if artist_element is not None:
        artist_element.delete_media(lp_data)  # TO DO: perhaps they artist is still associated with a sone on the LP

    new_artist = Artists.create_Artist(new_artist_name)
    artist_element = new_artist
    try:
        new_artist.add_media(lp_data)
    except LPException as e:
        # Could be an artist on a song of the album
        app.app.logger.warning('LP Exception {} ignored. Assuming artist associated with other songs on the LP'.format(e))
    except Exception as e:
        raise e


def append_new_artists(artists_list, new_artist_names, lp_data):
    """ Create a new Artist and append them to the passed list of artists.

        Each new Artist will also be associated with the passed LP

        :param artists_list:       The list of Artists to append to
        :type artisst_list:        list(:class:`_Artist`)

        :param new_artist_names:   The names of the new Artists to create
        :type new_artist_names:    list(str)

        :param lp_data:            The LP to associate with the new Artist
        :type lp_data:             :class:`_LP`

        :raises Exception:         Only class:`LPException` is caught when adding the LP to the new Artist
                                   under the assumption the Artist may have already be associated on another
                                   song or the LP
    """
    for artist_name in new_artist_names:
        new_additional_artist = Artists.create_Artist(artist_name)
        artists_list.append(new_additional_artist)
        try:
            new_additional_artist.add_media(lp_data)
        except LPException as e:
            # Could be an artist of a song on the album
            app.app.logger.warning('LP Exception {} ignored. Assuming additional artist to be associated with other songs on LP'.format(e))
        except Exception as e:
            raise e


def append_new_additional_artists(additional_artists_list,
                                  new_additional_artist_names,
                                  new_additional_artist_prequels,
                                  new_additional_artist_sequels,
                                  lp_data):
    """ Create a new Additional Artist and append them to the passed list of additional artists.

        Each new Additional Artist will also be associated with the passed LP

        :param additional_artists_list:         The list of Additional Artists to append to
        :type additional_artists_list:          list(:class:`Additional_Artist`)

        :param new_additional_artist_names:     The names of the new Additional Artists to create
        :type new_additional_artist_names:      list(str)

        :param new_additional_artist_prequels:  The prequels for the new Additional Artists
        :type new_additional_artist_prequels:   list(str)

        :param new_additional_artist_sequels:   The sequels for the new Additional Artists
        :type new_additional_artist_sequels:    list(str)

        :param lp_data:                         The LP to associate with the new Artist
        :type lp_data:                          :class:`_LP`

        :raises Exception:                      Only class:`LPException` is caught when adding the LP to
                                                the new Artist under the assumption the Artist may have
                                                already be associated on another
    """
    for index, artist_name in enumerate(new_additional_artist_names):
        new_additional_artist = Artists.create_Artist(artist_name)
        new_additional_artist = Additional_Artist(artist=new_additional_artist,
                                                  prequel=new_additional_artist_prequels[index],
                                                  sequel=new_additional_artist_sequels[index])
        additional_artists_list.append(new_additional_artist)
        try:
            new_additional_artist.add_media(lp_data)
        except LPException as e:
            # Could be an artist of a song on the album
            app.app.logger.warning('LP Exception {} ignored. Assuming artist associated with other songs or the LP'.format(e))
        except Exception as e:
            raise e


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
        form.lp_classical_composer_1.data = ''
        form.lp_classical_composer_2.data = ''

    if request.method == 'POST':
        if form.cancel.data:
            return redirect(url_for('.index'))

        try:
            if form.validate:
                lp_title = form['lp_title'].data.strip()
                lp_artist_str = form['lp_main_artist'].data.strip()
                lp_additional_artists = form['lp_additional_artists']
                lp_mixer_str = form['lp_mixer'].data.strip()
                lp_classical_composer_1_str = form['lp_classical_composer_1'].data.strip()
                lp_classical_composer_2_str = form['lp_classical_composer_2'].data.strip()
                lp_year = form['lp_year'].data
                if lp_title is None or lp_title == '':
                    flash('Error: A title is required for a new LP.')
                    raise FormValidateException()
                elif (lp_artist_str is None or lp_artist_str == '') and (lp_mixer_str is None or lp_mixer_str == ''):
                    flash('Error a Main Artist or Mixer is required for a new LP.')
                    raise FormValidateException()

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
                            raise FormValidateException()
                if lp_unique:
                    # Start processing the new album data
                    if lp_artist_str is not None or lp_artist_str != '':
                        lp_artists = [Artists.create_Artist(lp_artist_str)]
                        if lp_additional_artists is None:
                            lp_artist_particles = None
                        else:
                            lp_artist_particles = []
                            for artist_info in lp_additional_artists:
                                particle = artist_info['additional_artist_particle'].data.strip()
                                particle = massage_particle(particle)
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

                    # Handle addition of up to two classical composers
                    lp_classical_composers = []
                    if lp_classical_composer_1_str is not None and lp_classical_composer_1_str != '':
                        lp_classical_composers.append(Artists.create_Artist(lp_classical_composer_1_str))
                    if lp_classical_composer_2_str is not None and lp_classical_composer_2_str != '':
                        lp_classical_composers.append(Artists.create_Artist(lp_classical_composer_2_str))
                    if lp_classical_composers == []:
                        lp_classical_composers = None

                    new_lp = LPs.create_LP(media_type=MediaType.LP,
                                           title=lp_title,
                                           artists=lp_artists,
                                           year=lp_year,
                                           mixer=lp_mixer,
                                           classical_composers=lp_classical_composers,
                                           artist_particles=lp_artist_particles)
                    return redirect(url_for('.add_lp_track', album_id=new_lp.index, track_id=0))
        except FormValidateException:
            pass
        except Exception as e:
            raise e

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
        form.track_num = track_id
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
                        app.app.logger.warning('LP Exception {} ignored. Assumed to be associated with multiple songs'.format(e))

            if form.add_track.data:
                track_id += 1
                return redirect(url_for('.add_lp_track', album_id=album_id, track_id=track_id))

            return redirect(url_for('.index'))

    return render_template('add_lp_track.html', form=form, track_songs=track_songs,
                           track_songs_additional_artists=track_songs_additional_artists,
                           track_song_classical_composers=track_song_classical_composers)


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
        form.lp_classical_composer_1.data = ''
        form.lp_classical_composer_2.data = ''
        if lp_data.classical_composers is not None:
            form.lp_classical_composer_1.data = lp_data.classical_composers[0].name
            if len(lp_data.classical_composers) == 2:
                form.lp_classical_composer_2.data = lp_data.classical_composers[1].name
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
def modify_lp(id):
    """ Modify the data of a LP """
    additional_artists = []

    form = ModifyLPMetaForm()
    lp_data = LPs.find_by_index(id)

    # Build up tuple of additional artists and artist particles for
    # future use
    artist_particles_tuple = tuple([lp_data.artist_particles[x - 1] for x in range(1, len(lp_data.artists))])
    additional_artists_name_tuple = tuple([lp_data.artists[x].name for x in range(1, len(lp_data.artists))])
    classical_composer_names_tuple = ()

    if request.method == 'GET':

        if len(lp_data.artists) > 1:
            for x in range(len(additional_artists_name_tuple)):
                additional_artist = {'additional_artist_particle': artist_particles_tuple[x],
                                     'additional_artist': additional_artists_name_tuple[x]}
                additional_artists.append(additional_artist)
        form.process(lp_additional_artists=additional_artists)
        form.lp_title.data = lp_data.title
        form.lp_main_artist.data = lp_data.artists[0].name
        form.lp_mixer.data = name_value_or_blank(lp_data.mixer)

        form.lp_classical_composer_1.data = ''
        form.lp_classical_composer_2.data = ''
        classical_composer_names_tuple = build_classical_composer_names_tuple(lp_data.classical_composers)
        if lp_data.classical_composers is not None:
            form.lp_classical_composer_1.data = lp_data.classical_composers[0].name
            if len(lp_data.classical_composers) == 2:
                form.lp_classical_composer_2.data = lp_data.classical_composers[1].name

        form.lp_year.data = lp_data.year

    if request.method == 'POST':
        if form.cancel.data:
            return redirect(url_for('.index'))

        try:
            if form.validate:

                if form.modify_tracks.data:
                    return redirect(url_for('.modify_lp_track', lp_id=lp_data.index, track_id=0))

                if form.save.data or form.save_and_modify_tracks.data:
                    lp_title = form['lp_title'].data.strip()
                    lp_artist_str = form['lp_main_artist'].data.strip()
                    lp_additional_artists = form['lp_additional_artists']
                    lp_mixer_str = form['lp_mixer'].data.strip()
                    new_classical_composer_names = []
                    lp_classical_composer_1_str = form['lp_classical_composer_1'].data.strip()
                    if lp_classical_composer_1_str is not None and lp_classical_composer_1_str != '':
                        new_classical_composer_names.append(lp_classical_composer_1_str)
                    lp_classical_composer_2_str = form['lp_classical_composer_2'].data.strip()
                    if lp_classical_composer_2_str is not None and lp_classical_composer_2_str != '':
                        new_classical_composer_names.append(lp_classical_composer_2_str)
                    lp_year = form['lp_year'].data
                    if lp_title is None or lp_title == '':
                        flash('Error: A title is required for an LP.')
                        raise FormValidateException
                    elif (lp_artist_str is None or lp_artist_str == '') and (lp_mixer_str is None or lp_mixer_str == ''):
                        flash('Error a Main Artist or Mixer is required for an LP.')
                        raise FormValidateException

                    # See if any updates are required
                    changes = False

                    # Check title change
                    if lp_title != lp_data.title:
                        # Check LP does not already exist
                        results = LPs.find_lp_by_title(lp_title)
                        if len(results) > 0:
                            # Need to check hash id
                            new_album_hash = media_to_hash(MediaType.LP, lp_title, lp_artist_str)
                            for result in results:
                                if result._hash == new_album_hash:
                                    flash('LP already exists in music media library!')
                                    raise FormValidateException
                        changes = True
                        lp_data.title = lp_title

                    # Check main artist change
                    if lp_artist_str != lp_data.artists[0].name:
                        changes = True

                        if lp_artist_str == '':
                            lp_data.artists[0].delete_media(lp_data)  # TO DO: perhaps they artist is still associated with a sone on the LP
                            lp_data.artists.remove(lp_data.artists[0])
                        else:
                            replace_artist(lp_data.artists[0], lp_artist_str, lp_data)

                    # Check mixer change
                    if (lp_data.mixer is not None and lp_mixer_str != lp_data.mixer.name) or (lp_data.mixer is None and lp_mixer_str != ''):
                        changes = True
                        if lp_mixer_str == '':
                            if lp_data.mixer is not None:
                                lp_data.mixer.delete_media(lp_data)
                            lp_data.mixer = None
                        else:
                            replace_artist(lp_data.mixer, lp_mixer_str, lp_data)

                    # Check if classical composers change. If so, rebuild completely
                    if (set(classical_composer_names_tuple) != set(new_classical_composer_names)):
                        changes = True
                        if lp_data.classical_composers is not None:
                            for classical_composer in lp_data.classical_composers:
                                classical_composer.delete_media(lp_data)

                        lp_data.classical_composers = []
                        if len(new_classical_composer_names) == 0:
                            lp_data.classical_composers = None
                        else:
                            append_new_artists(lp_data.classical_composers, new_classical_composer_names, lp_data)

                    # Check if year change
                    if lp_year != lp_data.year:
                        changes = True
                        lp_data.year = lp_year

                    # Check for changes in the additional artists fields. First get
                    # all the form data
                    artist_particle_list = []
                    additional_artists_name_list = []
                    for artist_info in lp_additional_artists:
                        if artist_info['additional_artist_particle'].data is None:
                            # Handle non-existing data
                            artist_particle_list.append('')
                        else:
                            particle = artist_info['additional_artist_particle'].data.strip()
                            artist_particle_list.append(massage_particle(particle))
                        if artist_info['additional_artist'].data is None:
                            # Handle non-existing data
                            additional_artists_name_list.append('')
                        else:
                            additional_artists_name_list.append(artist_info['additional_artist'].data.strip())
                    # Compare form data versus existing data for any changes
                    if not ((set(artist_particle_list) == set(artist_particles_tuple)) and
                            (set(additional_artists_name_list) == set(additional_artists_name_tuple)) and
                            (len(artist_particle_list) == len(additional_artists_name_tuple))):

                        # With changes, we completely rebuild the LP's additional artists and particles list
                        changes = True
                        for index, artist_name in enumerate(additional_artists_name_tuple):
                            if artist_name not in additional_artists_name_list:
                                lp_data.artists[index + 1].delete_media(lp_data)  # Recall main artist at first entry

                        # Check we have additional artists and update appropriately
                        del lp_data.artists[1:]
                        if set(additional_artists_name_list) == set(['']):
                            lp_data.artist_particles = None
                        else:
                            lp_data.artist_particles = artist_particle_list
                            append_new_artists(additional_artists_name_list, lp_data.artists, lp_data)

                    if not changes:
                        flash('No changes made that need to be saved.')
                        raise FormValidateException

                    if form.save.data:
                        return redirect(url_for('.index'))

        except FormValidateException:
            pass
        except Exception as e:
            raise e

    return render_template('modify_lp.html', form=form, lp_additional_artists=additional_artists)


@lps.route('/modify_track/<int:lp_id>/<int:track_id>', methods=['GET', 'POST'])
@login_required
def modify_lp_track(lp_id, track_id):
    """ Modify the data of a LP track """

    form = ModifyLPTrackForm()
    lp_data = LPs.find_by_index(lp_id)
    form.lp_title = lp_data.title

    if request.method == 'GET':
        if len(lp_data.tracks) < track_id + 1:
            # Adding a new track
            form.track_name.data = ''
            form.track_mixer.data = ''
            form.track_num = 0
            form.new_track = True
        else:
            form.track_name.data = lp_data.tracks[track_id].name
            form.track_mixer.data = lp_data.tracks[track_id].side_mixer
            form.track_num = track_id
            form.new_track = False

    if request.method == 'POST':
        if form.cancel.data:
            return redirect(url_for('.modify_lp', id=lp_id))

        if form.validate:
            track_name = form['track_name'].data.strip()
            track_mixer = form['track_mixer'].data.strip()

            if len(lp_data.tracks) < track_id + 1:
                # Adding a new track
                if track_mixer == '':
                    track_mixer = None
                new_tracklist = TrackList(track_name, track_mixer)
                lp_data.tracks.append(new_tracklist)
            else:
                if track_name != lp_data.tracks[track_id].name:
                    lp_data.tracks[track_id].name = track_name
                if track_mixer != lp_data.tracks[track_id].side_mixer:
                    lp_data.tracks[track_id].side_mixer = track_mixer

            if form.modify_next_track.data:
                return redirect(url_for('.modify_lp_track', lp_id=lp_id, track_id=track_id + 1))

            if form.modify_songs.data:
                return redirect(url_for('.modify_lp_track_song', lp_id=lp_id, track_id=track_id, song_id=0))

            if form.save.data:
                return redirect(url_for('.index'))

    return render_template('modify_lp_track.html', form=form)


@lps.route('/modify_track_song/<int:lp_id>/<int:track_id>/<int(signed=True):song_id>', methods=['GET', 'POST'])
@login_required
def modify_lp_track_song(lp_id, track_id, song_id):
    """ Modify the data of a LP track """

    # NEed a way to determine when we are inserting a new song at the beginning
    # of the track as -0 == 0. We use a sentinel value with the assumption we will
    # never have 1001 song entries on a tracklist.
    NEW_FIRST_SONG_SENTINEL = -1000

    form = ModifySongForm()
    lp_data = LPs.find_by_index(lp_id)
    lp_title = lp_data.title
    tracklist = lp_data.tracks[track_id]
    track_name = tracklist.name

    song_additional_artists = []
    if song_id < 0:
        # Adding a new song.
        template_new_song = True
        template_last_song = True if len(tracklist.song_list) == -1 * song_id else False   # TODO Fix

    else:
        # Existing song
        template_new_song = False
        template_last_song = True if len(tracklist.song_list) == song_id + 1 else False
        song_data = tracklist.song_list[song_id]

        # Build data used in both GET and POST requests
        (song_additional_artists, additional_artists_prequel_tuple,
         additional_artists_name_tuple, additional_artists_sequel_tuple) = build_additional_artist_tuples(song_data.additional_artists)

        classical_composers_name_tuple = build_classical_composer_names_tuple(song_data.classical_composers)

    if request.method == 'GET':
        template_song_id = song_id + 1

        # Needs to be done first to "process" and avoid blanking out the info later
        form.process(song_additional_artists=song_additional_artists)

        if song_id < 0:
            # Handle new song addition
            form.song_title.data = ''
            form.song_mix.data = ''
            form.song_featured_in.data = ''
            form.song_list_main_artist.data = False
            form.song_country.data = ''
            form.song_year.data = ''
            form.song_mix.data = ''
            form.song_parts.data = ''
            form.song_classical_work.data = ''
            form.process(song_additional_artists=song_additional_artists)
        else:
            # Pre-populate with existing song information
            form.song_title.data = song_data.title
            form.song_featured_in.data = song_data.featured_in
            form.song_list_main_artist.data = song_data.exp_main_artist
            form.song_country.data = song_data.country
            form.song_year.data = song_data.year
            form.song_mix.data = song_data.mix
            form.song_parts.data = '\n'.join(song_data.parts)
            if song_data.classical_composers is not None:
                form.song_classical_composer_1.data = song_data.classical_composers[0].name
                if len(song_data.classical_composers) == 2:
                    form.song_classical_composer_2.data = song_data.classical_composers[1].namne

            form.song_classical_work.data = song_data.classical_work

    if request.method == 'POST':
        if form.cancel.data:
            return redirect(url_for('.index'))

        if form.previous_song.data:
            if song_id < 0:
                new_display_song_id = -1 * song_id - 1
            else:
                new_display_song_id = song_id - 1
            return redirect(url_for('.modify_lp_track_song', lp_id=lp_id, track_id=track_id, song_id=new_display_song_id))

        if form.insert_song.data:
            if song_id == 0:
                new_song_insertion_id = NEW_FIRST_SONG_SENTINEL
            else:
                new_song_insertion_id = -1 * song_id
            return redirect(url_for('.modify_lp_track_song', lp_id=lp_id, track_id=track_id, song_id=new_song_insertion_id))

        if form.append_new_song.data:
            new_song_insertion_id = -1 * (song_id + 1)
            return redirect(url_for('.modify_lp_track_song', lp_id=lp_id, track_id=track_id, song_id=new_song_insertion_id))

        if form.delete_song.data:
            # Delete the current song
            if song_id + 1 == len(tracklist.song_list):
                # Move back a song to display
                new_display_song_id = song_id - 1
            else:
                new_display_song_id = song_id
            del tracklist.song_list[song_id]  # TODP: Handle removal of LP from song artists
            return redirect(url_for('.modify_lp_track_song', lp_id=lp_id, track_id=track_id, song_id=new_display_song_id))

        if form.next_song.data:
            if song_id == NEW_FIRST_SONG_SENTINEL:
                new_display_song_id = 0
            elif song_id < 0:
                new_display_song_id = -1 * song_id
            else:
                new_display_song_id = song_id + 1
            return redirect(url_for('.modify_lp_track_song', lp_id=lp_id, track_id=track_id, song_id=new_display_song_id))

        if form.validate:
            try:
                # Process song data
                if form['song_title'].data is None or form['song_title'] == '':
                    flash('Error: A title is required for a song.')
                    raise FormValidateException()
                song_title_str = form['song_title'].data.strip()

                # Handle simple song fields
                song_mix = field_value_or_none(form, 'song_mix')
                song_featured_in = field_value_or_none(form, 'song_featured_in')
                list_main_artist = form['song_list_main_artist'].data
                song_country = field_value_or_none(form, 'song_country')

                # Cleanly handle year of song which could be invalid
                song_year = field_value_or_none(form, 'song_year')
                if song_year is not None:
                    try:
                        song_year = int(song_year)
                    except ValueError:
                        flash('Error: Year in Song #{} is not an integer.'.format(song_id + 1))
                        raise FormValidateException()

                # Handle additional song artists
                additional_artists_prequel_list = []
                additional_artists_name_list = []
                additional_artists_sequel_list = []
                additional_artists = form['song_additional_artists']
                for additional_artist in additional_artists:
                    additional_artist_str = field_value_or_none(additional_artist, 'additional_artist')
                    if additional_artist_str is None:
                        continue
                    additional_artist_prequel = field_value_or_none(additional_artist, 'additional_artist_prequel')
                    additional_artist_sequel = field_value_or_none(additional_artist, 'additional_artist_sequel')
                    additional_artists_prequel_list.append(additional_artist_prequel)
                    additional_artists_name_list.append(additional_artist_str)
                    additional_artists_sequel_list.append(additional_artist_sequel)

                # Handle classical musical aspects of a song
                classical_composer_1_str = field_value_or_none(form, 'song_classical_composer_1')
                classical_composer_2_str = field_value_or_none(form, 'song_classical_composer_2')
                classical_composers_name_list = []
                if classical_composer_1_str is not None:
                    classical_composers_name_list.append(classical_composer_1_str)
                if classical_composer_2_str is not None:
                    classical_composers_name_list.append(classical_composer_2_str)
                song_classical_work = field_value_or_none(form, 'song_classical_work')

                # Handle song parts
                song_parts = []
                song_parts_text = form['song_parts'].data
                if song_parts_text is not None and song_parts_text != '':
                    song_parts_lines = song_parts_text.split('\n')
                    for line in song_parts_lines:
                        if line.strip() != '':
                            song_parts.append(line.strip())

                # Now make changes where the data differs
                if template_new_song:
                    # Create and add a new song to the track list
                    classical_composers = []
                    append_new_artists(classical_composers, classical_composers_name_list, lp_data)

                    additional_artists = []
                    append_new_additional_artists(additional_artists,
                                                  additional_artists_name_list,
                                                  additional_artists_prequel_list,
                                                  additional_artists_sequel_list,
                                                  lp_data)

                    new_song = Song(title=song_title_str,
                                    main_artist=lp_data.artists[0],
                                    exp_main_artist=list_main_artist,
                                    album=lp_data.title,
                                    additional_artists=additional_artists,
                                    classical_composers=classical_composers,
                                    classical_work=song_classical_work,
                                    country=song_country,
                                    year=song_year,
                                    mix=song_mix,
                                    featured_in=song_featured_in,
                                    parts=song_parts)
                    if song_id == NEW_FIRST_SONG_SENTINEL:
                        tracklist.song_list.insert(0, new_song)
                    elif template_last_song:
                        tracklist.song_list.append(new_song)
                    else:
                        tracklist.song_list.insert(-1 * song_id, new_song)

                # Update existing song
                else:
                    # Handle simple fields first
                    if song_data.title != song_title_str:
                        song_data.title = song_title_str
                    if song_data.mix != song_mix:
                        song_data.mix = song_mix
                    if song_data.featured_in != song_featured_in:
                        song_data.featured_in = song_featured_in
                    if song_data.year != song_year:
                        song_data.year = song_year
                    if song_data.country != song_country:
                        song_data.country = song_country
                    if song_data.classical_work != song_classical_work:
                        song_data.classical_work = song_classical_work
                    if song_data.exp_main_artist != list_main_artist:
                        song_data.exp_main_artist = list_main_artist
                        if list_main_artist:
                            # Add in main LP artist
                            song_data.main_artist = lp_data.artists[0]

                    # Blindly update parts if it has data
                    if song_parts is not None and song_parts != []:
                        song_data.parts = song_parts
                    else:
                        song_data.parts = None

                    # Handle classical composer changes
                    # First, compare form data versus existing data for any changes
                    if not ((set(classical_composers_name_list) == set(classical_composers_name_tuple)) and
                            (len(classical_composers_name_list) == len(classical_composers_name_tuple))):
                        # With changes, completely rebuild the song's classical composers list
                        for index, composer_name in enumerate(classical_composers_name_tuple):
                            if composer_name not in classical_composers_name_list:
                                song_data.classical_composers[index].delete_media(lp_data)
                        new_composers = []
                        append_new_artists(new_composers, classical_composers_name_list, lp_data)
                        song_data.classical_composers = new_composers

                    # Handle additional artist changes
                    # First, compare form data versus existing data for any changes
                    if not ((set(additional_artists_prequel_list) == set(additional_artists_prequel_tuple)) and
                            (set(additional_artists_name_list) == set(additional_artists_name_tuple)) and
                            (set(additional_artists_sequel_list) == set(additional_artists_sequel_tuple)) and
                            (len(additional_artists_name_list) == len(additional_artists_name_tuple))):

                        # With changes, we completely rebuild the song's additional artists and particles list
                        for index, artist_name in enumerate(additional_artists_name_tuple):
                            if artist_name not in additional_artists_name_list:
                                song_data.additional_artists[index].artist.delete_media(lp_data)

                        song_data.additional_artists = []
                        append_new_additional_artists(song_data.additional_artists,
                                                      additional_artists_name_list,
                                                      additional_artists_prequel_list,
                                                      additional_artists_sequel_list,
                                                      lp_data)

                return redirect(url_for('.index'))

            except FormValidateException:
               pass
            except Exception as e:
                raise e

    return render_template('modify_lp_track_song.html',
                           form=form,
                           song_additional_artists=song_additional_artists,
                           lp_title=lp_title,
                           song_id=template_song_id,
                           template_new_song=template_new_song,
                           template_last_song=template_last_song,
                           track_name=track_name)


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
