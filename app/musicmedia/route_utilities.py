from app import app
from .musicmedia_objects import (
    Additional_Artist,
    Artists,
    CDs,
    ELPs,
    LPs,
    MediaException,
    MediaType,
    MINI_CDs,
)


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
    if form[field].data is None:
        return None
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
            additional_artists_sequels.append(additional_artist.sequel)
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


def append_new_artists(artists_list, new_artist_names, item_data):
    """ Create a new Artist and append them to the passed list of artists returning the updated list.

        Each new Artist will also be associated with the passed Music Media item

        :param artists_list:       The list of Artists to append to
        :type artisst_list:        list(:class:`_Artist`)

        :param new_artist_names:   The names of the new Artists to create
        :type new_artist_names:    list(str)

        :param item_data:          The Music Media item to associate with the new Artist
        :type item_data:           :class:`_Media`

        :returns:                  The updated list
        :rtype:                    list(:class:`_Artist`)

        :raises Exception:         Only class:`MediaException` is caught when adding the Music Media item to the
                                   new Artist under the assumption the Artist may have already be associated on
                                   another song or the Music Media item
    """
    for artist_name in new_artist_names:
        new_additional_artist = Artists.create_Artist(artist_name)
        artists_list.append(new_additional_artist)
        try:
            new_additional_artist.add_media(item_data)
        except MediaException as e:
            # Could be an artist of a song on the album
            app.app.logger.warning('Media Exception {} ignored. Assuming additional artist to be associated with other songs on the Music Media item'.format(e))
        except Exception as e:
            raise e
    return artists_list


def append_new_additional_artists(additional_artists_list,
                                  new_additional_artist_names,
                                  new_additional_artist_prequels,
                                  new_additional_artist_sequels,
                                  item_data):
    """ Create a new Additional Artist and append them to the passed list of additional artists returning the updated list.

        Each new Additional Artist will also be associated with the passed Music Media item

        :param additional_artists_list:         The list of Additional Artists to append to
        :type additional_artists_list:          list(:class:`Additional_Artist`)

        :param new_additional_artist_names:     The names of the new Additional Artists to create
        :type new_additional_artist_names:      list(str)

        :param new_additional_artist_prequels:  The prequels for the new Additional Artists
        :type new_additional_artist_prequels:   list(str)

        :param new_additional_artist_sequels:   The sequels for the new Additional Artists
        :type new_additional_artist_sequels:    list(str)

        :param item_data:                       The Music Media item to associate with the new Artist
        :type item_data:                        :class:`_Media`

        :returns:                               The new updated list
        :rtype:                                 list(:class:`Additional_Artist`)

        :raises Exception:                      Only class:`MediaException` is caught when adding the Music
                                                Media item to the new Artist under the assumption the Artist
                                                may have already be associated on another
    """
    if additional_artists_list is None:
        additional_artists_list = []
    for index, artist_name in enumerate(new_additional_artist_names):
        new_artist = Artists.create_Artist(artist_name)
        new_additional_artist = Additional_Artist(artist=new_artist,
                                                  prequel=new_additional_artist_prequels[index],
                                                  sequel=new_additional_artist_sequels[index])
        additional_artists_list.append(new_additional_artist)
        try:
            new_artist.add_media(item_data)
        except MediaException as e:
            # Could be an artist of a song on the album
            app.app.logger.warning('Media Exception {} ignored. Assuming artist associated with other songs or the Music Media item'.format(e))
        except Exception as e:
            raise e
    return additional_artists_list


def get_macmedia_library(media_type):
    """ Return library singleton based on the music media type  """
    if media_type == MediaType.LP:
        musicmedia_library = LPs
    elif media_type == MediaType.CD:
        musicmedia_library = CDs
    elif media_type == MediaType.ELP:
        musicmedia_library = ELPs
    elif media_type == MediaType.MINI_CD:
        musicmedia_library = MINI_CDs
    else:
        raise MediaException('Unknown Music Media Type: {}'.format(media_type))
    return musicmedia_library
