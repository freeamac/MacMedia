"""
Definition of all the objects required for a list of LPs:
    + A set of LPs is a singleton holding a set of all LP objects
    + An LP object has a title string, Artist object, list of Track objects
      and an optional mixer Artist object
    + An Artist object has a name string, a set of LP objects
    + A set of Artists is a singleton holding a set of all Artist objects
    + A Track object has an option side string and a list of Song objects
    + A Song object has a title string, an option main Artist object,
      an optional list of Additional Artist objects and an option mix
      string
    + a Additional Artist object which is essential a tuple of
      a prequel string, artist object and sequel string which
      is used to compose appropriate formatting where songs are
      done in a collaboration

LP objects can be deleted from the set of LPs which will also remove that
lp from the set of LP objects referenced by the lp artist.

It is possible for an Artist object to not reference any lps either due to
there last lp being deleted or they are only associated with a song(s) on
an lp.
"""

from hashlib import md5
from html import escape
from typing import List, Optional, Set

from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag


class LPException(Exception):
    """ Indicates an error using an LP object. """
    pass


class ArtistException(Exception):
    """ Indicates an error using and Artist object. """
    pass


class SongException(Exception):
    """ Indicates an error using a Song object. """
    pass


class AdditionalArtistException(Exception):
    """ Indicates an error using and Additional_Artist object """
    pass


class TrackListException(Exception):
    """ Indicates an error using a TrackList object. """
    pass


class _Artist():
    """ Defines a music artist. Should only be instantiated by calling :func:`Artists().create_Artists`. """

    @property
    def lps(self) -> set:
        return self._lps

    @property
    def name(self) -> str:
        return self._name

    def __init__(self, name: str) -> None:
        self._name = name
        self._lps = set()

    def add_lp(self, lp: '_LP') -> None:
        """ Add an album associated with the artist as the main artist or mixer of the album.

            :param lp:            The album to associate with the artist
            :type param_lp:       :class:`LP`

            :raises LPException:  If passed parameter is not an :class:`_LP` or the album already
                                  associated with the artist
        """
        if type(lp) is not _LP:
            raise LPException('{} is not an LP object'.format(lp))
        if lp in self._lps:
            raise LPException('{} already in list of LPs for {}'.format(lp.title, self.name))
        else:
            self._lps.add(lp)

    def delete_lp(self, lp: '_LP') -> None:
        """ Remove an album associated with an artist.

            :param lp:             The album to associate with the artist
            :type param_lp:       :class:`LP`

            :raises LPException:  If passed parameter is not an :class:`_LP`
        """
        if lp not in self._lps:
            raise LPException('{} not in list of LPs for {}'.format(lp.title, self.name))
        else:
            self._lps.remove(lp)

    def find_lp(self, lp_title: str) -> Optional['_LP']:
        """ Return the named album of the artist or None.

            :param lp_title   Name of the album to locate
            :type lp_title:   str

            :returns:         The album or None
            :rtype:           :class:`_LP` | None
        """
        for lp in self._lps:
            if lp.title == lp_title:
                return lp

    def update_name(self, new_name: str) -> None:
        """ Update the name of the artist.

            :param new_name:  The new name of the artist
            :type new_name:   str
        """
        self._name = new_name

    def to_html(self, song_artist=False):
        """ Return a html string representation of an artist.

            :param: song_artist:  If this is to represent a song artist instead of a media artist
            :type son_artist:     bool

            :returns:             Html representation of the artist
            :rtypr:               str
         """
        artist_tag = "artist"
        if song_artist:
            artist_tag = "song-artist"
        html_str = '<b><a rel="{artist_tag}">{name}</a></b>'.format(artist_tag=artist_tag, name=escape(self.name, quote=False))
        return html_str

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name


class Artists():
    """ A singleton set of all music artists. """
    _instance = None
    _artists = set()
    VARIOUS_ARTISTS = 'VARIOUS ARTISTS'

    @property
    def artists(self) -> Set[_Artist]:
        """ Set of all artists. """
        return self._artists

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Artists, cls).__new__(cls)
        return cls._instance

    @classmethod
    def _clean_artists(cls):
        """ Private method to remove all artists from the collection. Useful in testing. """
        cls._artists = set()

    @classmethod
    def create_Artist(cls, name: str, skip_adding_to_artists_set: bool = False) -> _Artist:
        """ Return the named artist if they exist or create a new artist.

            By default a new artist is added to the set of all artists.

            :param name:                          The name of the new artist
            :type name:                           str

            :param skip_adding_to_artists_set:    If true, do not add new artist to artists set
            :type skip_adding_to_artists_set:     bool

            :raises ArtistException:              If there is no passed name

            :returns:                             The located or newly created artist
            :rtype:                               :class:`_Artist`
        """
        if name is None or '':
            raise ArtistException('An artist must have a name')
        result = cls.find_artist(name)
        if result is not None:
            return result
        new_artist = _Artist(name)
        if not skip_adding_to_artists_set:
            cls.add_artist(new_artist)
        return new_artist

    @classmethod
    def add_artist(cls, artist: _Artist) -> None:
        """ Add an artist to the set of all artists.

            :param artist:            The artist to add
            :type artist:             :class:`_Artist`

            :raises ArtistException:  If a :class:`_Artist` is not passed or the artist
                                      already exists in the set
        """
        if type(artist) is not _Artist:
            raise ArtistException('{} is not an Artist object'.format(artist))
        if artist in cls._artists or cls.find_artist(artist.name) is not None:
            raise ArtistException('Artist {} already exists'.format(artist))
        cls._artists.add(artist)

    @classmethod
    def delete_artist(cls, artist: _Artist) -> None:
        """ Delete an artist from the set of all artists.

            :param artist:            The artist to delete
            :type artist:             :class:`_Artist`

            :raises ArtistException:  If artist does not exist in the set
        """
        if artist not in cls._artists:
            raise ArtistException('Artist {} does not exist'.format(artist))
        else:
            cls._artists.remove(artist)

    @classmethod
    def artist_exists(cls, artist: _Artist) -> bool:
        """ True if the artist is in the set of artists.

            :param artist:  The artist to add
            :type artist:   :class:`_Artist`

            :returns:       True if the artist exists in the set of all artists
            :rtype:         bool
        """
        return artist in cls._artists

    @classmethod
    def find_artist(cls, artist_name: str) -> Optional[_Artist]:
        """ Returns the artist if an artist of that name exists in the set of all artists.

            :param artist_name:  Name of the artist to find
            :type artist_name:   str

            :returns:            The artist if an artist of that name is found. Otherwise None
            :rtype:              :class:`_Artist` if found, otherwise None
        """
        for artist in cls._artists:
            if artist.name == artist_name:
                return artist

    @classmethod
    def __str__(cls) -> str:
        string = ''
        for artist in cls._artists:
            string += '{}\n'.format(artist)
            string += '  Albums\n'
            string += '  ------\n'
            for lp in artist.lps:
                string += '  {}\n'.format(lp.title)
            string += '\n'
        return string


class Additional_Artist():
    """ Formatting structure used for additional artists associated with a :class:`Song`. """

    @property
    def artist(self):
        return self._artist

    def __init__(self, artist: _Artist, prequel: Optional[str] = None, sequel: Optional[str] = None) -> None:
        """ Create formatting structure for an addition artist.

            An additional artist may have an optional prequel string and
            optional sequel string which is used when formatting their
            association with a song.

            For example, a song my have a tagline of "<main artist> with <additional artist> (backing vovals)"
            where the string "with" is the prequel and "(backing vocals)" the sequel.

            :param artist:            The additional artist
            :type artist:             :class:`_Artist`

            :param prequel:           The prequel string
            :type prequel:            str | None

            :param sequel:            The sequel string
            :type sequel:             str | None

            :raises ArtistException:  If the addition artist is not a :class:`_Artist`
        """
        if type(artist) is not _Artist:
            raise ArtistException('{} is not an Artist object'.format(artist))
        self._artist = artist
        self._prequel = prequel
        self._sequel = sequel

    def to_html(self):
        """ Html representation of an additional artist.

            :returns:   The html representation of an additonal artist
            :rtype:     str
        """
        html_str = '{prequel}<b><a rel="song-artist">{artist}</a></b>{sequel}'.format(prequel=escape(self._prequel, quote=False),
                                                                                      artist=escape(self._artist.name, quote=False),
                                                                                      sequel=escape(self._sequel, quote=False))
        return html_str

    def __str__(self) -> str:
        if self._prequel is not None:
            string = '{}{}'.format(self._prequel, self._artist)
        else:
            string = '{}'.format(self._artist)
        if self._sequel is not None:
            string += self._sequel
        return string


class Song():
    """ A song found on an album. """

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, new_title) -> None:
        self._title = new_title

    @property
    def main_artist(self) -> _Artist:
        return self._main_artist

    @main_artist.setter
    def main_artist(self, new_artist) -> None:
        if new_artist is not None and type(new_artist) is not _Artist:
            raise ArtistException('{} is not an Artist object'.format(new_artist))
        self._main_artist = new_artist

    @property
    def additional_artists(self) -> List[_Artist]:
        return self._additional_artists

    @additional_artists.setter
    def additional_artists(self, new_artists) -> None:
        for artist in new_artists:
            if type(artist) is not Additional_Artist:
                raise AdditionalArtistException('{} is not an Additional_Artist'.format(artist))
        self._additional_artists = new_artists

    @property
    def album(self) -> str:
        return self._album

    @album.setter
    def album(self, new_album) -> None:
        self._album = new_album

    @property
    def classical_composer(self) -> Optional[_Artist]:
        return self._classical_composer

    @classical_composer.setter
    def classical_composer(self, composer) -> None:
        if composer is not None and type(composer) is not _Artist:
            raise ArtistException('{} is not an Artist object'.format(composer))
        self.classical_composer = composer

    @property
    def classical_work(self) -> str:
        return self._classical_work

    @classical_work.setter
    def classical_work(self, new_classical_work) -> None:
        self._classical_work = new_classical_work

    @property
    def country(self) -> str:
        return self._country

    @country.setter
    def country(self, new_country) -> None:
        self._country = new_country

    @property
    def year(self) -> int:
        return self._year

    @year.setter
    def year(self, new_year) -> None:
        self._year = new_year

    @property
    def mix(self) -> str:
        return self._mix

    @mix.setter
    def mix(self, new_mix) -> None:
        self._mix = new_mix

    @property
    def parts(self) -> List[str]:
        return self._parts

    @parts.setter
    def parts(self, new_parts) -> None:
        self._parts = new_parts

    def __init__(self,
                 title: str,
                 main_artist: Optional[_Artist] = None,
                 exp_main_artist: Optional[bool] = False,
                 additional_artists: Optional[List[_Artist]] = None,
                 album: Optional[str] = None,
                 classical_composer: Optional[_Artist] = None,
                 classical_work: Optional[str] = None,
                 country: Optional[str] = None,
                 year: Optional[int] = None,
                 mix: Optional[str] = None,
                 parts: Optional[List[str]] = None) -> None:
        """ Creates a song found on an album.

            :param title:               The title of this song
            :type title:                str

            :param main_artist:         The main artist of this song. If the album is by a single artitst, this
                                        is typically not given unless it is included in the song description
                                        on the album
            :type main_artist:          :class:`_Artist`

            :param exp_main_artist:     Used to know if the main artist should appear in exports
            :type exp_main_artist:      bool

            :param additional_artists:  Optional list of additional artists associated with the song
            :type additional_artists:   list(:class:`Additional_Artist`) | None

            :param album:               Name of the album this song is taken from
            :type album:                str

            :param classical_composer:  The composer of this classical song
            :type classical_composer:   :class:`_Artist`

            :param classical_work:      The classical work this song comes from
            :type classical_work:       str

            :param country:             The country this song is from
            :type country:              str

            :param year:                The year of this song
            :type year:                 str

            :param mix:                 Optional song mix
            :type mix                   str

            :param parts:               A list of parts this song is divided into
            :type parts:                list(str) | None

            :raises ArtistException:    If main artist or classical composer is not None or :class:`_Artist`

            :raises AdditionalArtistException:  If pass list of additional artists are not all of type
                                                :class:`Additional_Artist`
            """
        if main_artist is not None and type(main_artist) is not _Artist:
            raise ArtistException('{} is not an Artist object'.format(main_artist))
        if additional_artists is not None:
            for artist in additional_artists:
                if type(artist) is not Additional_Artist:
                    raise AdditionalArtistException('{} is not an Additional_Artist'.format(artist))
        if classical_composer is not None and type(classical_composer) is not _Artist:
            raise ArtistException('{} is not an Artist object'.format(classical_composer))

        self._title = title
        self._main_artist = main_artist
        self._exp_main_artist = exp_main_artist
        self._additional_artists = additional_artists
        self._album = album
        self._classical_composer = classical_composer
        self._classical_work = classical_work
        self._country = country
        if year is not None and not isinstance(year, int):
            raise SongException('{} is not a valid integer year'.format(year))
        self._year = year
        self._mix = mix
        self._parts = parts

    def delete_additional_artist(self, additional_artist) -> Optional[_Artist]:
        """ Delete the artist from the additional artist list """
        pass

    def add_additional_artist(self, additional_artist) -> None:
        """ Add the artist from the additional artist list """
        pass

    def delete_part(self, part_name) -> Optional[str]:
        """ Delete the part from the song parts list """
        pass

    def add_part(self, part_name) -> None:
        """ Add the part from the song parts list """
        pass

    def to_html(self):
        """ Return an html representation of a song.

            :returns:    An html representation of a song
            :rtype:      str
        """
        def spaceit(line: str, spaces: int) -> str:
            """ Ensure an indentation of the specified number of spaces. """
            spaced_line = ' ' * spaces + line.lstrip()
            return spaced_line

        if self.title is None:
            html_str = '  <li>'
        else:
            html_str = '  <li><a rel="song">{title}</a>'.format(title=escape(self.title, quote=False))
        if self.additional_artists is not None:
            html_str += '<br>'
            for additional_artist in self.additional_artists:
                # html_str += '\n      {}'.format(additional_artist.to_html())
                html_str += '\n' + spaceit('{}'.format(additional_artist.to_html()), 6)
        if self.mix is not None:
            html_str += '<br>\n      (<a rel="song-mix">{}</a>)'.format(escape(self.mix, quote=False))
        if self.classical_composer is not None:
            html_str += '<br>\n      by <b><a rel="song-classical-composer">{}</a></b>'.format(escape(self.classical_composer.name, quote=False))
        if self.year is not None:
            html_str += '<br>\n       - <a rel="song-date">{}</a>'.format(self.year)
        if self.parts is not None and self.parts != []:
            html_str += '\n'
            html_str += spaceit('<ol type=I>\n', 4)
            for song_part in self.parts:
                html_str += spaceit('<li><a rel="song-part">{}</a></li>\n'.format(escape(song_part, quote=False)), 6)
            html_str += spaceit('</ol>\n', 4)
            html_str += spaceit('</li>\n', 4)
        else:
            html_str += '</li>\n'
        return html_str

    def __str__(self) -> str:
        string = '{}\n'.format(self.title)
        if self.main_artist is not None:
            string += '{}\n'.format(self.main_artist)
        if self.additional_artists is not None:
            for additional_artist in self.additional_artists:
                string += '{}'.format(additional_artist)
            string += '\n'
        if self.album is not None:
            string += '({})\n'.format(self.album)
        if self.classical_composer is not None:
            string += '({})\n'.format(self.classical_composer)
        if self.classical_work is not None:
            string += '({})\n'.format(self.classical_work)
        if self.country is not None:
            string += '({})\n'.format(self.country)
        if self.year is not None:
            string += '({})\n'.format(self.year)
        if self.mix is not None:
            string += '({})\n'.format(self.mix)
        if self.parts is not None:
            for part in self.parts:
                string += '({})\n'.format(part)
        return string


class TrackList():
    """ A list of songs (tracklist) on one side of an album"""

    @property
    def side(self) -> Optional[str]:
        return self._side

    @side.setter
    def side(self, side_name) -> None:
        self._side = side_name

    @property
    def side_mixer(self) -> Optional[str]:
        return self._side_mixer

    @side_mixer.setter
    def side_mixer(self, side_mixer_name) -> None:
        self._side_mixer = side_mixer_name

    @property
    def song_list(self) -> List[Song]:
        return self._song_list

    def __init__(self, side_name: Optional[str] = None, side_mixer_artist: Optional[_Artist] = None, songs: Optional[List[Song]] = None) -> None:
        """ Create a tracklist for an album.

            :param side_name:          The name of the tracklist (eg. "Side A")
            :type side_name:           str | None

            :param side_mixer_Artist:  And optional mixer of the songs on this tracklist
            :type side_mixer_Artist:   :class:`_Artist`

            :parm songs:               A list of songs on the track
            :type songs:               list(:class:`Song`)

            :raises ArtistException:  If side_mixer is not a :class:`Artist`
        """
        self._side = side_name
        if side_mixer_artist is not None and type(side_mixer_artist) is not _Artist:
            raise ArtistException('{} is not an Artist object'.format(side_mixer_artist))
        self._side_mixer = side_mixer_artist
        self._song_list = songs

    def add_song(self, song: Song) -> None:
        """ Append a song to the end of the song list. Thus an ordered list.

            :param song:  The song to add to the end of the tracklist
            :type song:   :class:`Song`

            :raises SongException:  If you are not adding a :class:`Song`
        """
        if type(song) is Song:
            if self._song_list is None:
                self._song_list = [song]
            else:
                self._song_list.append(song)
        else:
            raise SongException('{} is not a song'.format(song))

    def remove_song(self, song: Song) -> None:
        """ Remove a song from the tracklist.

            :param song:  The song to remove
            :type song:   :class:`Song`
        """
        if song in self.song_list:
            self._song_list.remove(song)

    def has_song(self, song: Song) -> bool:
        """ True is the passed song can be found in the tracklist.

            :param song:  The song to remove
            :type song:   :class:`Song`

            :returns:     True if the song is found in the tracklist
            :rtype:       bool
        """
        return song in self.song_list

    def get_song_from_title(self, song_title: str) -> Optional[Song]:
        """ Returns the song if the title can be found in the tracklist. None otherwise.

            :param song_title:  The song title to find
            :type song_title:   str

            :returns:           The song if the title is found in the tracklist
            :rtype:             :class:`Song`
        """
        for song in self.song_list:
            if song.title == song_title:
                return song

    def to_html(self):
        """ Return an html representation of a tracklist.

            :returns:  An html representation of a tracklist
            :rtype:    str
        """
        html_str = '<a rel="side">\n'
        html_str += '<h4><blockquote>{side_title}</blockquote></h4>\n'.format(side_title=escape(self.side, quote=False))
        html_str += '<ol>\n'
        for song in self.song_list:
            html_str += song.to_html()
        html_str += '</ol>\n'
        html_str += '</a>\n'
        return html_str

    def __str__(self) -> str:
        if self._side is not None:
            string = '{}'.format(self._side)
        else:
            string = ''
        if self._side_mixer is not None:
            string += 'mixed by {}'.format(self._side_mixer)
        string += '\n'
        if self._song_list is not None:
            for counter, song in enumerate(self._song_list):
                string += '{:2d}. {}'.format(counter + 1, song)
        return string


class _LP():
    """ Defines a music album. Should only be instantiated by calling :func:`LPs().create_LP`. """

    @property
    def title(self) -> str:
        return self._title

    @property
    def artist(self) -> _Artist:
        return self._artist

    @property
    def year(self) -> int:
        return self._year

    @property
    def mixer(self) -> Optional[_Artist]:
        return self._mixer

    @property
    def classical_composer(self) -> Optional[_Artist]:
        return self._classical_composer

    @property
    def tracks(self) -> List[TrackList]:
        return self._tracks

    @staticmethod
    def to_hash(title: str, artist_name: str) -> str:
        """ Create a hash for the album based on title and artist_name.

            :param title:        The album title
            :type title:         str

            :param artist_name:  The name of the artist of the album
            :type artist_name:   str

            :returns:            md5 has string
            :rtype:              str
        """
        return md5(bytes(title + artist_name, 'utf-8')).hexdigest()  # nosec

    def __init__(self, title: str, artist: _Artist, year: int, mixer: Optional[_Artist] = None, classical_composer: Optional[_Artist] = None) -> None:
        self._title = title
        if type(artist) is not _Artist:
            raise ArtistException('{} is not an Artist object'.format(artist))
        self._artist = artist
        if not isinstance(year, int):
            raise TypeError('Year must be an int value')
        self._year = year
        if mixer is not None and type(mixer) is not _Artist:
            raise ArtistException('{} is not an Artist object'.format(mixer))
        self._mixer = mixer
        if classical_composer is not None and type(classical_composer) is not _Artist:
            raise ArtistException('{} is not an Artist object'.format(classical_composer))
        self._classical_composer = classical_composer
        self._id = self.to_hash(title, artist.name)
        self._id = self.to_hash(title, artist.name)

        # Tracks must be set at this level or a reference will exist in the
        # singleton and keep being appended to through "add_track()". Ensure
        # starts empty with and instance level variable which can only be
        # updated through an instance level call to "add_track[]".
        self._tracks = []

    def add_track(self, track: TrackList) -> None:
        """ Append a tracklist to the list of tracks on the album. Thus an ordered list.

            :param track:                The tracklist to append
            :type track:                 :class:`TrackList`

            :raises TrackListException:  If not passed a :class:`TrackList`
        """
        if type(track) is TrackList:
            self._tracks.append(track)
        else:
            raise TrackListException('{} is not a track list'.format(track))

    def has_song(self, song: Song) -> bool:
        """ True if the song is found in one of the tracklists on the album.

            :param song:            The song to search for
            :type song:             :class:`Song`

            :returns:               True if the song is found. False otherwise
            :rtype:                 bool

            :raises SongException:  If not passed a :class:`Song`
        """
        for track in self._tracks:
            if track.has_song(song):
                return True
        return False

    def get_song_from_title(self, song_title: str) -> Optional[Song]:
        """ Return the song if the song title is found in one of the tracklists on the album.

            :param song_title:  The song title to search for
            :type song_title:   str

            :returns:           The song is found. None otherwise
            :rtype:             :class:`Song` | None
        """
        for track in self._tracks:
            result = track.get_song_from_title(song_title)
            if result is not None:
                return result

    def to_html(self):
        """ Return an html representation of the album

            :returns:   An html representation of the album
            :rtype:     str
        """
        html_str = '<p>\n'
        html_str += '<a rel="lp">\n'
        html_str += '<h3><a rel="title">{title}</a></h3>\n'.format(title=escape(self.title, quote=False))
        html_str += '<h3><a rel="artist">{artist}</a></h3>\n'.format(artist=escape(self.artist.name, quote=False))
        if self.classical_composer is not None:
            html_str += '<h3><a rel="classical-composer">{composer}</a></h3>\n'.format(composer=escape(self.classical_composer.name, quote=False))
        html_str += '<h3><a rel="date">{year}</a></h3>\n'.format(year=self.year)
        for track in self.tracks:
            html_str += track.to_html()
        html_str += '</a>\n'
        return html_str

    def __str__(self) -> str:
        string = '{}\n{}\n'.format(self.title, self.artist)
        if self.mixer is not None:
            string += 'Mixed by {}\n'.format(self.mixer)
        string += '{}'.format(self.year)
        for track in self.tracks:
            string += str(track)
        string += '\n'
        return string


class LPs():
    """ A singleton set of all music albums. """
    _instance = None
    _lps = []

    @property
    def lps(self) -> List[_LP]:
        return self._lps

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LPs, cls).__new__(cls)
        return cls._instance

    @classmethod
    def _clean_lps(cls):
        """ Private method to remove all albums from the collection. Useful in testing. """
        cls._lps = []

    @classmethod
    def create_LP(cls,
                  title: str,
                  artist: _Artist,
                  year: int,
                  mixer: Optional[_Artist] = None,
                  classical_composer: Optional[_Artist] = None,
                  skip_adding_to_lp_list: bool = False) -> _LP:
        """ Return the named album if it exists or create a new album.

            By default a new album is added to the set of all albums.

            :param title:                    The title of the new album
            :type name:                      str

            :param artist:                   The album artist
            :type artist:                    :class:`_Artist`

            :param year:                     The year the album was published
            :type year:                      int

            :param mixer:                   Optional album mixer
            :type mixer:                    :class:`_Artist`

            :param classical_composer:      Optional album classical composer
            :type classical_composer:       :class:`_Artist`

            :param skip_addiing_to_lp_list:  If true, do not add new album to albums set
            :type skip_adding_to_lp_list:    bool

            :returns:                        The located or newly created album
            :rtype:                          :class:`_LP`
        """
        # We need to perform this check before searching for an existing album as we need a valid
        # artist name to search
        if type(artist) is not _Artist:
            raise ArtistException('{} is not an artist'.format(artist))

        results = cls.find_lp_by_title(title)
        if len(results) > 0:
            # Need to check hash id
            new_album_id = _LP.to_hash(title, artist.name)
            for result in results:
                if result._id == new_album_id:
                    return result
        # Create the new album
        new_lp = _LP(title, artist, year, mixer, classical_composer)
        artist.add_lp(new_lp)
        if mixer is not None:
            mixer.add_lp(new_lp)
        if not skip_adding_to_lp_list:
            cls.add_lp(new_lp)
        return new_lp

    @classmethod
    def add_lp(cls, lp: _LP) -> None:
        """ Add an album to the set of all albums.

            :param lp:            The album to add
            :type lp:             :class:`_LP`

            :raises LPException:  If not passed a :class:`_LP` or the lp already exists in the set
        """
        if type(lp) is not _LP:
            raise LPException('{} is not an LP object'.format(lp))
        if lp in cls._lps:
            raise LPException('LP {} already exists'.format(lp))
        cls._lps.append(lp)

    @classmethod
    def delete_lp(cls, lp: _LP) -> None:
        """ Remove the album from the set of all albums.

            Also remove the album from the set of all albums owned by
            the album artist and album mixer (if they exist)

            :param lp:  The album to add
            :type lp:   :class:`_LP`
        """
        if lp in cls._lps:
            lp.artist.delete_lp(lp)
            if lp.mixer is not None:
                lp.mixer.delete_lp(lp)
            cls._lps.remove(lp)

    @classmethod
    def lp_exists(cls, lp: _LP) -> bool:
        """ Returns true of the album exists in the set of albums.

            :param lp:  The album to add
            :type lp:   :class:`_LP`

            :returns:   True if the album exists in the set of all albums
            :rtype:     bool
        """
        return lp in cls._lps

    @classmethod
    def find_lp_by_title(cls, title: str) -> List[_LP]:
        """ Returns the albums in the set of all albums that matches the passed album title. Otherwise, empty list.

            :param title:  The album title to search for
            :type title:   str

            :returns:      The album if found. None, otherwise
            :rtype:        list(:class:`_LP` )
         """
        result = []
        for lp in cls._lps:
            if lp.title == title:
                result.append(lp)
        return result

    @classmethod
    def find_lps_by_year(cls, year: int) -> List[_LP]:
        """ Return a list of albums produced in the passed year.

            :param year:  Find albums produced in this year
            :type year:   int

            :returns:     A list of albums produced in that year
            :rtype:       list(:class:`_LP`) | None
        """
        lps_found = []
        for lp in cls._lps:
            if lp.year == year:
                lps_found.append(lp)
        if lps_found == []:
            return None
        return lps_found

    @classmethod
    def from_html_file(cls, filepath: str) -> None:
        """ Load the library from an html file.

            :param filepath:  The file path of the html file to load
            :type filepath:   str
        """
        def rel_element_text(head_node, rel_value) -> str:
            rel_text = None
            rel_node = head_node.find('a', rel=rel_value)
            if rel_node is not None:
                rel_text = rel_node.text.strip()
            return rel_text

        def get_lp_metadata(lp_element: Tag) -> (str, List[_Artist], List[_Artist], List[_Artist], str):
            """ Parse the album tag for the album specific metadata.

                The album metadata is the album title, list of album artists, list of album composers,
                list of album mixers and the year the LP was produced. The composer and mixer list
                may be optional.

                :param lp_element:   The Tag node for an album.
                :type lp_element:    :class:`bs2.element.Tag`

                :returns:            A tuple of the album metadata: title, artists, composers, mixers
                                     and production year
                :rtype:              tuple(str, list(:class:`_Artist`), list(:class:`_Artist`), list(:class:`_Artist`), str)
            """
            lp_title = rel_element_text(lp_element, 'title')

            lp_artists = []
            lp_artist_elements = lp_element.find_all('a', rel='artist')
            for lp_artist_element in lp_artist_elements:
                lp_artist_name = lp_artist_element.text.strip()
                lp_artists.append(Artists.create_Artist(lp_artist_name))

            # Track down albums with more than one artist credit
            if len(lp_artists) > 1:
                print('Title: {}'.format(lp_title))
                assert (len(lp_artists) == 1)  # nosec

            lp_classical_composers = []
            lp_classical_composer_elements = lp_element.find_all('a', rel='classical-composer')
            for lp_classical_composer_element in lp_classical_composer_elements:
                lp_classical_composer_name = lp_classical_composer_element.text.strip()
                lp_classical_composers.append(Artists.create_Artist(lp_classical_composer_name))

            # Track down albums with more than one classical composer credit
            if len(lp_classical_composers) > 1:
                print('Title: {}'.format(lp_title))
                assert (len(lp_classical_composers) == 1)  # nosec

            lp_mixers = []
            lp_mixer_elements = lp_element.find_all('a', rel='mixer')
            for lp_mixer_element in lp_mixer_elements:
                lp_mixer_name = lp_mixer_element.text.strip()
                lp_mixers.append(Artists.create_Artist(lp_mixer_name))

            # Track down albums with more than one mixer credit
            if len(lp_mixers) > 1:
                print('Title: {}'.format(lp_title))
                assert (len(lp_mixers) == 1)  # nosec

            lp_date = rel_element_text(lp_element, 'date')

            return lp_title, lp_artists, lp_classical_composers, lp_mixers, lp_date

        def get_song_additional_artists(song_block: Tag, lp_artist: _Artist) -> (_Artist, List[Additional_Artist]):
            """ Get the optional main artist and additional artists from the song artist block.

                We expect the song artists to reside in the <li></li> block which contains
                all the information about the song. The artists should come consecutively after
                the song name which is followed by a <br> tag so we begin our search after
                this tag. Each artist will be encased in <b></b> tags. This is easy enough
                to locate. The challenging aspect is collecting the text surrounding the
                artist names. Text may occur before the first artist so we need to
                trap the text after the <br> tag. For subsequent artists, we trap the
                text between two artists and associate it with the later artists.

                The main artist will be the album artist unless it is
                found on a "Various Artist" album. In this case, we want to ensure the
                main artist is the first song artist.

                :param song_block:          The Tag node for a song block containing all information
                                            about a song
                :type song_block:           :class:`bs2.element.Tag`

                :param lp_artist:           The artist of the LP which is the main song artist
                                            except on a Various Artists album
                :type lp_artist:            :class:`_Artist`

                :returns:                   Main song artist if they exists and a list of additional
                                            song artists. Main artist should only occur on "Various
                                            Artist" albums
                :rtype:                     tuple(_Artist | None, list(Additional_Artist))
            """
            main_artist = lp_artist
            other_artists = []
            first_prequel = ''
            song_metadata_block = song_block.find('br')
            if song_metadata_block is not None:
                if isinstance(song_metadata_block.next_sibling, NavigableString):
                    first_prequel = song_metadata_block.next_sibling.text.split('\n')[1]
                all_artist_blocks = song_block.find_all('b')
                if len(all_artist_blocks) > 0:
                    for artist_block in all_artist_blocks:
                        # Note that a <b> tag may contain other tags besides a song-artist
                        # but the consecutivity of the artists allows the following to work
                        artist_name_block = artist_block.find('a', rel="song-artist")
                        if artist_name_block is not None:
                            prequel = sequel = ''
                            artist_name = artist_name_block.text.strip()
                            song_artist = Artists.create_Artist(artist_name)
                            if artist_block == all_artist_blocks[0]:
                                prequel = first_prequel
                                # Special handling of first block for the prequel and main artist
                                if lp_artist.name.upper() == Artists.VARIOUS_ARTISTS:
                                    main_artist = song_artist

                            if isinstance(artist_block.next_sibling, NavigableString):
                                sequel = artist_block.next_sibling.text.split('\n')[0]

                            other_artists.append(Additional_Artist(song_artist, prequel=prequel, sequel=sequel))

            return main_artist, other_artists, exp_main_artist

        with open(filepath, 'r') as fp:
            # Parse the formatted file for LPs
            html = fp.read()
            parsed_html = BeautifulSoup(html, features="html.parser")

            # Parse out the LPs
            all_lp_elements = parsed_html.find_all('a', rel='lp')

            # Process each LP element
            for lp_element in all_lp_elements:

                lp_title, lp_artists, lp_classical_composers, lp_mixers, lp_date = get_lp_metadata(lp_element)
                lp_song_artists = []

                # Process each side of the lp
                lp_tracklist = []
                all_side_elements = lp_element.find_all('a', rel='side')
                for side_element in all_side_elements:
                    side_title = side_element.find('h4').text.strip()
                    side_mixer = rel_element_text(side_element, 'side-mixer')

                    # Process each song on the side
                    side_Songs = []
                    all_side_songs = side_element.find_all('li')
                    found_song_parts = False
                    song_parts_parent = None
                    for song_block in all_side_songs:
                        if found_song_parts:
                            # Song parts contain 'li' tags so we process
                            # the first such song and then skip until at the end
                            # of the parts in the song
                            if song_block.parent == song_parts_parent:
                                continue
                        song_title = rel_element_text(song_block, 'song')
                        song_album = rel_element_text(song_block, 'song-album')

                        # Song artist by default is only the album artist
                        main_artist = lp_artists[0]
                        additional_artists = None
                        exp_main_artist = False

                        # Determine main song, additional song artists with prequel and sequel information.
                        # and if main artist should be exposed.
                        song_main_artist, song_additional_artists, exp_main_artist = get_song_additional_artists(song_block, lp_artists[0])
                        if song_main_artist is not None:
                            main_artist = song_main_artist
                        if song_additional_artists != []:
                            for additional_artist in song_additional_artists:
                                lp_song_artists.append(additional_artist.artist)
                            additional_artists = song_additional_artists

                        song_classical_composer_node = song_block.find('a', rel='song-classical-composer')
                        song_classical_composer = None
                        if song_classical_composer_node is not None:
                            song_classical_composer = Artists.create_Artist(song_classical_composer_node.text.strip())
                            lp_song_artists.append(song_classical_composer)

                        song_classical_work = rel_element_text(song_block, 'song-classical-work')
                        song_country = rel_element_text(song_block, 'song-country')
                        song_date = rel_element_text(song_block, 'song-date')
                        if song_date is not None:
                            song_date = int(song_date)
                        song_mix = rel_element_text(song_block, 'song-mix')

                        song_parts = []
                        song_part_elements = song_block.find_all('a', rel='song-part')
                        if song_part_elements != []:
                            # If we have song parts, we need to mark the <ol> parent
                            # so we can skip 'li' tags which are song parts which
                            # we are processing now
                            song_parts_parent = song_part_elements[0].parent.parent
                            found_song_parts = True
                            for song_part_element in song_part_elements:
                                song_parts.append(song_part_element.text.strip())
                        else:
                            song_parts_parent = None
                            found_song_parts = False

                        side_Songs.append(Song(title=song_title,
                                               main_artist=main_artist,
                                               exp_main_artist=exp_main_artist,
                                               additional_artists=additional_artists,
                                               album=song_album,
                                               classical_composer=song_classical_composer,
                                               classical_work=song_classical_work,
                                               country=song_country,
                                               year=song_date,
                                               mix=song_mix,
                                               parts=song_parts))
                    side_tracklist = TrackList(side_name=side_title, side_mixer_artist=side_mixer, songs=side_Songs)
                    lp_tracklist.append(side_tracklist)

                # Create the LP and add it to all the artists found
                # TODO: Handle artists vs composers vs mixers
                if lp_mixers == []:
                    lp_mixer = None
                else:
                    lp_mixer = lp_mixers[0]
                if lp_classical_composers == []:
                    lp_classical_composer = None
                else:
                    lp_classical_composer = lp_classical_composers[0]
                new_LP = LPs.create_LP(title=lp_title, artist=lp_artists[0], year=int(lp_date), mixer=lp_mixer, classical_composer=lp_classical_composer)
                for tracklist in lp_tracklist:
                    new_LP.add_track(tracklist)

                # Add LP to all song artists found once we dedupe them
                for artist in set(lp_song_artists):
                    # Need to skip any that are also album artists since they have
                    # already been added
                    if artist not in lp_artists:
                        artist.add_lp(new_LP)

    @classmethod
    def to_html_file(cls, filepath: str) -> None:
        """ Write the library to an html file.

            :param filepath:  The file path of the html file to write to
            :type filepath:   str
        """
        # TODO:  Implement
        pass

    @classmethod
    def to_html(cls):
        """ Return an html representation of all albums

            :returns:  An html representation of all albums
            :rtype:    str
        """
        HTML_HEADER = """<!DOCTYPE PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html lang="en">
<head>
<title>Music List</title>
</head>
<body>
<p>
<h2>Audio Media</h2>
"""
        HTML_CLOSER = """</body>
</html>
"""
        html_str = HTML_HEADER
        for lp in cls._lps:
            html_str += lp.to_html()
        html_str += HTML_CLOSER
        return html_str

    def __str__(self) -> str:
        string = ''
        for lp in self.lps:
            string += str(lp)
        return string