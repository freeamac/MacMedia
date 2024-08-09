from flask import flash, redirect, render_template, request, url_for

from app import app
from .musicmedia_objects import (
    Additional_Artist,
    Artists,
    MEDIA,
    MediaException,
    Song,
    TrackList,
    media_to_hash
)
from .musicmedia_forms import (
    DeleteMusicMediaForm,
    NewMusicMediaMetaForm,
    NewMusicMediaTrackForm,
    ModifyMusicMediaMetaForm,
    ModifyMusicMediaTrackForm,
    ModifySongForm
)
from .route_utilities import (
    append_new_additional_artists,
    append_new_artists,
    build_additional_artist_tuples,
    build_classical_composer_names_tuple,
    field_value_or_none,
    get_macmedia_library,
    name_value_or_blank,
    massage_particle,
)


class FormValidateException(Exception):
    pass


def expand(media_type, id):
    """ Expand the Music Media information of the passed Music Media id. """
    musicmedia_library = get_macmedia_library(media_type)
    musicmedia_str = media_type.value

    musicmedia_data = musicmedia_library.find_by_index(id)
    if musicmedia_data is None:
        flash('ERROR: {} with identifier "{}" not found'.format(musicmedia_str, id))
        return redirect(url_for('.index'))
    html_str = musicmedia_data.to_html()
    return render_template('expand_musicmedia.html', media_str=musicmedia_str, html_str=html_str)


def delete(media_type, id):
    """ Delete the Music Media from the list """
    musicmedia_library = get_macmedia_library(media_type)
    musicmedia_str = media_type.value

    musicmedia_data = musicmedia_library.find_by_index(id)
    if musicmedia_data is None:
        flash('ERROR: {} with identifier "{}" not found'.format(musicmedia_str, id))
        return redirect(url_for('.index'))

    # Set up form
    form = DeleteMusicMediaForm()

    if request.method == 'GET':
        form.title.data = musicmedia_data.title
        form.artists.data = musicmedia_data.artists_text
        if musicmedia_data.mixer is not None:
            form.mixer.data = musicmedia_data.mixer
        form.classical_composer_1.data = ''
        form.classical_composer_2.data = ''
        if musicmedia_data.classical_composers is not None:
            form.classical_composer_1.data = musicmedia_data.classical_composers[0].name
            if len(musicmedia_data.classical_composers) == 2:
                form.classical_composer_2.data = musicmedia_data.classical_composers[1].name
        form.year.data = str(musicmedia_data.year)

    if request.method == 'POST':
        # Take action based on the button pressed

        if form.cancel.data:
            # User cancels form submission
            return redirect(url_for('.index'))

        musicmedia_library.delete(musicmedia_data)
        MEDIA.to_html_file()

        return redirect(url_for('.index'))

    return render_template('delete_musicmedia.html', media_str=musicmedia_str, form=form)


def add_media(media_type):
    """ Add a new Music Media item """
    musicmedia_library = get_macmedia_library(media_type)
    musicmedia_str = media_type.value
    pythonic_musicmedia_str = musicmedia_str.replace('-', '_')

    additional_artists = [{'artist_particle': '', 'additional_artist': ''}] * 5

    form = NewMusicMediaMetaForm()

    if request.method == 'GET':
        form.title.data = ''
        form.main_artist.data = ''
        form.mixer.data = ''
        form.classical_composer_1.data = ''
        form.classical_composer_2.data = ''

    if request.method == 'POST':
        if form.cancel.data:
            return redirect(url_for('.index'))

        try:
            if form.validate:
                title = form['title'].data.strip()
                artist_str = form['main_artist'].data.strip()
                additional_artists = form['additional_artists']
                mixer_str = form['mixer'].data.strip()
                classical_composer_1_str = form['classical_composer_1'].data.strip()
                classical_composer_2_str = form['classical_composer_2'].data.strip()
                year = form['year'].data
                if title is None or title == '':
                    flash('Error: A title is required for a new {}.'.format(musicmedia_str))
                    raise FormValidateException()
                elif (artist_str is None or artist_str == '') and (mixer_str is None or mixer_str == ''):
                    flash('Error a Main Artist or Mixer is required for a new {}.'.format(musicmedia_str))
                    raise FormValidateException()

                # Check item does not already exist
                unique = True
                results = musicmedia_library.find_by_title(title)
                if len(results) > 0:
                    # Need to check hash id
                    new_item_hash = media_to_hash(media_type, title, artist_str)
                    for result in results:
                        if result._hash == new_item_hash:
                            unique = False
                            flash('{} already exists in music media library!'.format(musicmedia_str))
                            raise FormValidateException()
                if unique:
                    # Start processing the new album data
                    if artist_str is not None or artist_str != '':
                        artists = [Artists.create_Artist(artist_str)]
                        if additional_artists is None:
                            artist_particles = None
                        else:
                            artist_particles = []
                            for artist_info in additional_artists:
                                particle = artist_info['additional_artist_particle'].data.strip()
                                particle = massage_particle(particle)
                                additional_artist_str = artist_info['additional_artist'].data.strip()
                                if additional_artist_str is None or additional_artist_str == '':
                                    continue
                                artist_particles.append(particle)
                                additional_artist = Artists.create_Artist(additional_artist_str)
                                artists.append(additional_artist)
                    else:
                        artists = None
                        artist_particles = None
                    if mixer_str is not None and mixer_str != '':
                        mixer = Artists.create_Artist(mixer_str)
                    else:
                        mixer = None

                    # Handle addition of up to two classical composers
                    classical_composers = []
                    if classical_composer_1_str is not None and classical_composer_1_str != '':
                        classical_composers.append(Artists.create_Artist(classical_composer_1_str))
                    if classical_composer_2_str is not None and classical_composer_2_str != '':
                        classical_composers.append(Artists.create_Artist(classical_composer_2_str))
                    if classical_composers == []:
                        classical_composers = None

                    new_item = musicmedia_library.create(media_type=media_type,
                                                         title=title,
                                                         artists=artists,
                                                         year=year,
                                                         mixer=mixer,
                                                         classical_composers=classical_composers,
                                                         artist_particles=artist_particles)
                    return redirect(url_for('.add_' + pythonic_musicmedia_str + '_track', media_type=media_type, id=new_item.index, track_id=0))
        except FormValidateException:
            pass
        except Exception as e:
            raise e

    return render_template('add_new_musicmedia_item.html', media_str=musicmedia_str, form=form, additional_artists=additional_artists)


def add_track(media_type, id, track_id):
    """ Add a new track to the Music Media item """
    musicmedia_library = get_macmedia_library(media_type)
    musicmedia_str = media_type.value
    pythonic_musicmedia_str = musicmedia_str.replace('-', '_')

    track_songs = [{'song_title': ''}] * 30
    track_songs_additional_artists = [{'song_additional_artist': ''}] * 3
    track_song_classical_composers = [{'song_classical_composer': ''}] * 2
    form = NewMusicMediaTrackForm()

    if request.method == "GET":
        form.track_num = track_id
        form.track_name.data = ''
        form.track_mixer.data = ''

    if request.method == 'POST':
        if form.cancel.data:
            return redirect(url_for('.index'))

        if form.validate:
            item = musicmedia_library.find_by_index(id)
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
                song_main_artist_sequel = song_field['song_main_artist_sequel'].data
                song_country = field_value_or_none(song_field, 'song_country')

                # Cleanly handle year of song which could be invalid
                song_year = field_value_or_none(song_field, 'song_year')
                if song_year is not None:
                    try:
                        song_year = int(song_year)
                    except ValueError:
                        flash('Error: Year in Song #{} is not an integer.'.format(song_num + 1))
                        return render_template('add_musicmedia_track.html', media_str=musicmedia_str, form=form,
                                               track_songs=track_songs,
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
                elif item.artists != []:
                    main_artist = item.artists[0]
                else:
                    main_artist = None

                song = Song(title=song_title_str,
                            main_artist=main_artist,
                            exp_main_artist=list_main_artist,
                            main_artist_sequel=song_main_artist_sequel,
                            album=item.title,
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
            item.add_track(tracklist)

            # Add the LP to all Artists referenced on this track
            if all_song_artists != set():
                for artist in all_song_artists:
                    try:
                        artist.add_media(item)
                    except MediaException as e:
                        app.app.logger.warning('{} Exception {} ignored. Assumed to be associated with multiple songs'.format(musicmedia_str, e))

            if form.add_track.data:
                track_id += 1
                return redirect(url_for('.add_' + pythonic_musicmedia_str + '_track', id=id, track_id=track_id))

            return redirect(url_for('.index'))

    return render_template('add_musicmedia_track.html', media_str=musicmedia_str, form=form,
                           track_songs=track_songs,
                           track_songs_additional_artists=track_songs_additional_artists,
                           track_song_classical_composers=track_song_classical_composers)


def modify(media_type, id):
    """ Modify the data of a Music Media item """

    musicmedia_library = get_macmedia_library(media_type)
    musicmedia_str = media_type.value
    pythonic_musicmedia_str = musicmedia_str.replace('-', '_')

    additional_artists = []

    form = ModifyMusicMediaMetaForm()
    item = musicmedia_library.find_by_index(id)

    # Build up tuple of additional artists and artist particles for
    # future use
    artist_particles_tuple = tuple([item.artist_particles[x - 1] for x in range(1, len(item.artists))])
    additional_artists_name_tuple = tuple([item.artists[x].name for x in range(1, len(item.artists))])
    classical_composer_names_tuple = ()

    if request.method == 'GET':

        if len(item.artists) > 1:
            for x in range(len(additional_artists_name_tuple)):
                additional_artist = {'additional_artist_particle': artist_particles_tuple[x],
                                     'additional_artist': additional_artists_name_tuple[x]}
                additional_artists.append(additional_artist)
        form.process(additional_artists=additional_artists)
        form.title.data = item.title
        form.main_artist.data = item.artists[0].name
        form.mixer.data = name_value_or_blank(item.mixer)

        form.classical_composer_1.data = ''
        form.classical_composer_2.data = ''
        classical_composer_names_tuple = build_classical_composer_names_tuple(item.classical_composers)
        if item.classical_composers is not None:
            form.classical_composer_1.data = item.classical_composers[0].name
            if len(item.classical_composers) == 2:
                form.classical_composer_2.data = item.classical_composers[1].name

        form.year.data = item.year

    if request.method == 'POST':
        if form.cancel.data:
            return redirect(url_for('.index'))

        try:
            if form.validate:

                if form.modify_tracks.data:
                    return redirect(url_for('.modify_' + pythonic_musicmedia_str + '_track', id=item.index, track_id=0))

                if form.save.data or form.save_and_modify_tracks.data:
                    title = form['title'].data.strip()
                    artist_str = form['main_artist'].data.strip()
                    additional_artists = form['additional_artists']
                    mixer_str = form['mixer'].data.strip()
                    new_classical_composer_names = []
                    classical_composer_1_str = form['classical_composer_1'].data.strip()
                    if classical_composer_1_str is not None and classical_composer_1_str != '':
                        new_classical_composer_names.append(classical_composer_1_str)
                    classical_composer_2_str = form['classical_composer_2'].data.strip()
                    if classical_composer_2_str is not None and classical_composer_2_str != '':
                        new_classical_composer_names.append(classical_composer_2_str)
                    year = form['year'].data
                    if title is None or title == '':
                        flash('Error: A title is required for a {}.'.format(musicmedia_str))
                        raise FormValidateException
                    elif (artist_str is None or artist_str == '') and (mixer_str is None or mixer_str == ''):
                        flash('Error a Main Artist or Mixer is required for an {}.'.format(musicmedia_str))
                        raise FormValidateException

                    # See if any updates are required
                    changes = False

                    # Check title change
                    if title != item.title:
                        # Check LP does not already exist
                        results = musicmedia_library.find_by_title(title)
                        if len(results) > 0:
                            # Need to check hash id
                            new_item_hash = media_to_hash(media_type, title, artist_str)
                            for result in results:
                                if result._hash == new_item_hash:
                                    flash('{} already exists in music media library!'.format(musicmedia_str))
                                    raise FormValidateException
                        changes = True
                        item.title = title

                    # Check main artist change
                    if artist_str != item.artists[0].name:
                        changes = True

                        item.artists[0].delete_media(item)  # TO DO: perhaps they artist is still associated with a sone on the LP
                        if artist_str == '':
                            item.artists.remove(item.artists[0])
                        else:
                            new_artist = Artists.create_Artist(artist_str)
                            item.artists[0] = new_artist
                            try:
                                new_artist.add_media(item)
                            except MediaException as e:
                                # Could be an artist on a song of the Music Media item
                                app.app.logger.warning('Media Exception {} ignored. Assuming artist associated with other songs on the Music Media item'.format(e))
                            except Exception as e:
                                raise e

                    # Check mixer change
                    if (item.mixer is not None and mixer_str != item.mixer.name) or (item.mixer is None and mixer_str != ''):
                        changes = True
                        if mixer_str == '':
                            if item.mixer is not None:
                                item.mixer.delete_media(item)
                            item.mixer = None
                        else:
                            new_mixer = Artists.create_Artist(mixer_str)
                            item.mixer = new_mixer
                            try:
                                new_mixer.add_media(item)
                            except MediaException as e:
                                # Could be an artist on a song of the Music Media item
                                app.app.logger.warning('Media Exception {} ignored. Assuming artist associated with other songs on the Music Media item'.format(e))
                            except Exception as e:
                                raise e

                    # Check if classical composers change. If so, rebuild completely
                    if (set(classical_composer_names_tuple) != set(new_classical_composer_names)):
                        changes = True
                        if item.classical_composers is not None:
                            for classical_composer in item.classical_composers:
                                classical_composer.delete_media(item)

                        item.classical_composers = []
                        if len(new_classical_composer_names) == 0:
                            item.classical_composers = None
                        else:
                            item.classical_composers = append_new_artists(item.classical_composers, new_classical_composer_names, item)

                    # Check if year change
                    if year != item.year:
                        changes = True
                        item.year = year

                    # Check for changes in the additional artists fields. First get
                    # all the form data
                    artist_particle_list = []
                    additional_artists_name_list = []
                    for artist_info in additional_artists:
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
                                item.artists[index + 1].delete_media(item)  # Recall main artist at first entry

                        # Check we have additional artists and update appropriately
                        del item.artists[1:]
                        if set(additional_artists_name_list) == set(['']):
                            item.artist_particles = None
                        else:
                            item.artist_particles = artist_particle_list
                            item.artists = append_new_artists(item.artists, additional_artists_name_list, item)

                    if not changes:
                        flash('No changes made that need to be saved.')
                        raise FormValidateException

                    if form.save.data:
                        return redirect(url_for('.index'))

                    if form.save_and_modify_tracks.data:
                        return redirect(url_for('.modify_' + pythonic_musicmedia_str + '_track', id=item.index, track_id=0))

        except FormValidateException:
            pass
        except Exception as e:
            raise e

    return render_template('modify_musicmedia.html', media_str=musicmedia_str, form=form, additional_artists=additional_artists)


def modify_track(media_type, id, track_id):
    """ Modify the data of a Music Media track """

    musicmedia_library = get_macmedia_library(media_type)
    musicmedia_str = media_type.value
    pythonic_musicmedia_str = musicmedia_str.replace('-', '_')

    form = ModifyMusicMediaTrackForm()
    item = musicmedia_library.find_by_index(id)
    form.title = item.title

    if request.method == 'GET':
        if len(item.tracks) < track_id + 1:
            # Adding a new track
            form.track_name.data = ''
            form.track_mixer.data = ''
            form.track_num = 0
            form.new_track = True
        else:
            form.track_name.data = item.tracks[track_id].name
            form.track_mixer.data = item.tracks[track_id].side_mixer
            form.track_num = track_id
            form.new_track = False

    if request.method == 'POST':
        if form.cancel.data:
            return redirect(url_for('.modify_' + pythonic_musicmedia_str, id=id))

        if form.validate:
            track_name = form['track_name'].data.strip()
            track_mixer = form['track_mixer'].data.strip()

            if len(item.tracks) < track_id + 1:
                # Adding a new track
                if track_mixer == '':
                    track_mixer = None
                new_tracklist = TrackList(track_name, track_mixer)
                item.tracks.append(new_tracklist)
            else:
                if track_name != item.tracks[track_id].name:
                    item.tracks[track_id].name = track_name
                if track_mixer != item.tracks[track_id].side_mixer:
                    item.tracks[track_id].side_mixer = track_mixer

            if form.modify_next_track.data:
                return redirect(url_for('.modify_' + pythonic_musicmedia_str + '_track', id=id, track_id=track_id + 1))

            if form.modify_songs.data:
                return redirect(url_for('.modify_' + pythonic_musicmedia_str + '_track_song', media_type=media_type, id=id, track_id=track_id, song_id=0))

            if form.save.data:
                return redirect(url_for('.index'))

    return render_template('modify_musicmedia_track.html', media_str=musicmedia_str, form=form)


def modify_track_song(media_type, id, track_id, song_id):
    """ Modify the data of a Music Media item track song """

    musicmedia_library = get_macmedia_library(media_type)
    musicmedia_str = media_type.value
    pythonic_musicmedia_str = musicmedia_str.replace('-', '_')

    # Need a way to determine when we are inserting a new song at the beginning
    # of the track as -0 == 0. We use a sentinel value with the assumption we will
    # never have 1001 song entries on a tracklist.
    NEW_FIRST_SONG_SENTINEL = -1000

    form = ModifySongForm()
    item = musicmedia_library.find_by_index(id)
    title = item.title
    tracklist = item.tracks[track_id]
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
            form.song_main_artist_sequel = ''
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
            form.song_main_artist_sequel.data = '' if song_data.main_artist_sequel is None else song_data.main_artist_sequel
            form.song_country.data = song_data.country
            form.song_year.data = song_data.year
            form.song_mix.data = song_data.mix
            if song_data.parts is None:
                form.song_parts.data = ''
            else:
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
            return redirect(url_for('.modify_' + pythonic_musicmedia_str + '_track_song', id=id, track_id=track_id, song_id=new_display_song_id))

        if form.insert_song.data:
            if song_id == 0:
                new_song_insertion_id = NEW_FIRST_SONG_SENTINEL
            else:
                new_song_insertion_id = -1 * song_id
            return redirect(url_for('.modify_' + pythonic_musicmedia_str + '_track_song', id=id, track_id=track_id, song_id=new_song_insertion_id))

        if form.append_new_song.data:
            new_song_insertion_id = -1 * (song_id + 1)
            return redirect(url_for('.modify_' + pythonic_musicmedia_str + '_track_song', id=id, track_id=track_id, song_id=new_song_insertion_id))

        if form.delete_song.data:
            # Delete the current song
            if song_id + 1 == len(tracklist.song_list):
                # Move back a song to display
                new_display_song_id = song_id - 1
            else:
                new_display_song_id = song_id
            del tracklist.song_list[song_id]  # TODP: Handle removal of LP from song artists
            return redirect(url_for('.modify_' + pythonic_musicmedia_str + '_track_song', id=id, track_id=track_id, song_id=new_display_song_id))

        if form.next_song.data:
            if song_id == NEW_FIRST_SONG_SENTINEL:
                new_display_song_id = 0
            elif song_id < 0:
                new_display_song_id = -1 * song_id
            else:
                new_display_song_id = song_id + 1
            return redirect(url_for('.modify_' + pythonic_musicmedia_str + '_track_song', id=id, track_id=track_id, song_id=new_display_song_id))

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
                song_main_artist_sequel = form['song_main_artist_sequel'].data
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
                    classical_composers = append_new_artists(classical_composers, classical_composers_name_list, item)

                    additional_artists = []
                    additional_artists = append_new_additional_artists(additional_artists,
                                                                       additional_artists_name_list,
                                                                       additional_artists_prequel_list,
                                                                       additional_artists_sequel_list,
                                                                       item)

                    new_song = Song(title=song_title_str,
                                    main_artist=item.artists[0],
                                    exp_main_artist=list_main_artist,
                                    main_artist_sequel=song_main_artist_sequel,
                                    album=item.title,
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
                            song_data.main_artist = item.artists[0]
                    if song_data.main_artist_sequel != song_main_artist_sequel:
                        song_data.main_artist_sequel = song_main_artist_sequel

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
                                song_data.classical_composers[index].delete_media(item)
                        new_composers = []
                        new_composers = append_new_artists(new_composers, classical_composers_name_list, item)
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
                                song_data.additional_artists[index].artist.delete_media(item)

                        song_data.additional_artists = []
                        song_data.additional_artists = append_new_additional_artists(song_data.additional_artists,
                                                                                     additional_artists_name_list,
                                                                                     additional_artists_prequel_list,
                                                                                     additional_artists_sequel_list,
                                                                                     item)

                return redirect(url_for('.index'))

            except FormValidateException:
               pass
            except Exception as e:
                raise e

    return render_template('modify_musicmedia_track_song.html',
                           media_str=musicmedia_str,
                           form=form,
                           song_additional_artists=song_additional_artists,
                           title=title,
                           song_id=template_song_id,
                           template_new_song=template_new_song,
                           template_last_song=template_last_song,
                           track_name=track_name)