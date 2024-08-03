"""
Definition of all the objects required for a list of music media:
    + Music media can be one of an LP, CD, mini-CD or ELP
    + There can only be one instance, defined by the "title"
      of a each type of media object
    + Each media type has a singleton holding all that particular media's
      objects
    + A Media object has a type, title string, Artist object, list of Track
      objects and an optional mixer Artist object
    + An Artist object has a name string, and a set of each type of media
      objects associated with that artist
    + A set of Artists is a singleton holding a set of all Artist objects
    + A Track object has an option side string and a list of Song objects
    + A Song object has a title string, an option main Artist object,
      an optional list of Additional Artist objects and an option mix
      string
    + a Additional Artist object which is essential a tuple of
      a prequel string, artist object and sequel string which
      is used to compose appropriate formatting where songs are
      done in a collaboration

Media objects can be deleted from the set of Media which will also remove that
media from the set of Media objects referenced by the media artist.

It is possible for an Artist object to not reference any media either due to
there last media being deleted or they are only associated with a song(s) on
a media tracklist.
"""

from enum import Enum
from hashlib import md5
from html import escape
from typing import List, Optional, Set

from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag


class MediaTypeException(Exception):
    """ Indicates an error using a Media Type definition. """
    pass


class MediaException(Exception):
    """ Indicates an error using a Media object. """


class LPException(MediaException):
    """ Indicates an error using an LP object. """
    pass


class CDException(MediaException):
    """ Indicates an error using a CD object. """
    pass


class MiniCDException(MediaException):
    """ Indicates an error using an mini-CD object. """
    pass


class ELPException(MediaException):
    """ Indicates an error using an ELP object. """
    pass


class ArtistException(Exception):
    """ Indicates an error using and Artist object. """
    pass


class SongException(Exception):
    """ Indicates an error using a Song object. """
    pass


class AdditionalArtistException(Exception):
    """ Indicates an error using and Additional_Artist object. """
    pass


class TrackListException(Exception):
    """ Indicates an error using a TrackList object. """
    pass


class MediaType(Enum):
    LP = 'lp'
    CD = 'cd'
    ELP = 'elp'
    MINI_CD = 'mini-cd'


class _Artist():
    """ Defines a music artist. Should only be instantiated by calling :func:`Artists().create_Artists`. """

    @property
    def index(self) -> int:
        return self._index

    @property
    def cds(self) -> set:
        return self._cds

    @property
    def lps(self) -> set:
        return self._lps

    @property
    def elps(self) -> set:
        return self._elps

    @property
    def mini_cds(self) -> set:
        return self._mini_cds

    @property
    def name(self) -> str:
        return self._name

    def __init__(self, name: str, index: int) -> None:
        self._name = name
        self._lps = set()
        self._cds = set()
        self._elps = set()
        self._mini_cds = set()
        self._index = index

    def add_media(self, media: '_MEDIA') -> None:
        """ Add a media object associated with the artist as the main artist or mixer of the album.

            :param media:             The album to associate with the artist.
            :type media:              :class:`_Media`

            :raises MediaException:   If passed parameter is not an :class:`_Media`.
            :raises LPException:      The album already associated with the artist.
            :raises CDException:      The CD already associated with the artist.
            :raises ELPException:     The ELP already associated with the artist.
            :raises MiniCDException:  The mini CD is already associated with the artist.
        """
        if type(media) is _CD:
            if media in self._cds:
                raise CDException('{} already in list of CDs for {}'.format(media.title, self.name))
            else:
                self._cds.add(media)
        elif type(media) is _LP:
            if media in self._lps:
                raise LPException('{} already in list of LPs for {}'.format(media.title, self.name))
            else:
                self._lps.add(media)
        elif type(media) is _ELP:
            if media in self._elps:
                raise ELPException('{} already in list of ELPs for {}'.format(media.title, self.name))
            else:
                self._elps.add(media)
        elif type(media) is _MINI_CD:
            if media in self._mini_cds:
                raise MiniCDException('{} already in list of Mini CDs for {}'.format(media.title, self.name))
            else:
                self._mini_cds.add(media)
        else:
            raise MediaException('{} is not an Media object'.format(media))

    def delete_media(self, media: '_MEDIA') -> None:
        """ Remove the media object associated with an artist.

            :param lp:                The media to remove from the artist.
            :type lp:                 :class:`LP`

            :raises LPException:      If the media object is an LP and not associated with the artist.
            :raises CDException:      If the media object is a CD and not associated with the artist.
            :raises ELPException:     If the media object is an ELP and not associated with the artist.
            :raises MiniCDException:  If the media object is an min CD and not associated with the artist.
            :raises MediaException:   If the passed paramater is not a media object.
        """
        if type(media) is _CD:
            if media not in self._cds:
                raise CDException('{} not in list of CDs for {}'.format(media.title, self.name))
            else:
                self._cds.remove(media)
        elif type(media) is _LP:
            if media not in self._lps:
                raise LPException('{} not in list of LPs for {}'.format(media.title, self.name))
            else:
                self._lps.remove(media)
        elif type(media) is _ELP:
            if media not in self._elps:
                raise ELPException('{} not in list of ELPs for {}'.format(media.title, self.name))
            else:
                self._elps.remove(media)
        elif type(media) is _MINI_CD:
            if media not in self._mini_cds:
                raise MiniCDException('{} not in list of mini CDs for {}'.format(media.title, self.name))
            else:
                self._mini_cds.remove(media)
        else:
            raise MediaException('Trying to remove a non Media object {} from {}'.format(media, self.name))

    def find_cd(self, cd_title: str) -> Optional['_CD']:
        """ Return the named cd of the artist or None.

            :param cd_title   Name of the cd to locate
            :type cd_title:   str

            :returns:         The CD or None
            :rtype:           :class:`_CD` | None
        """
        for cd in self._cds:
            if cd.title == cd_title:
                return cd

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

    def find_elp(self, elp_title: str) -> Optional['_ELP']:
        """ Return the named ELP of the artist or None.

            :param elp_title   Name of the ELP to locate
            :type elp_title:   str

            :returns:          The ELP or None
            :rtype:            :class:`_ELP` | None
        """
        for elp in self._elps:
            if elp.title == elp_title:
                return elp

    def find_mini_cd(self, mini_cd_title: str) -> Optional['_MINI_CD']:
        """ Return the named mini CD of the artist or None.

            :param mini_cd_title   Name of the mini CD to locate
            :type mini_cd_title:   str

            :returns:              The mini CD or None
            :rtype:                :class:`_MINI_CD` | None
        """
        for mini_cd in self._mini_cds:
            if mini_cd.title == mini_cd_title:
                return mini_cd

    def find_media(self, title: str) -> Optional[List['_MEDIA']]:
        """ Return a list of media with the named title of the artist or None.

            :param title:  Title of the media to locate
            :type title:   str

            :returns:      A list of media with that title or None
            :rtype:        list(:class:`_MEDIA`) | None
        """
        pass

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
    _max_index = 0
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
        cls._max_index = 0

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
        new_artist = _Artist(name, cls._max_index)
        cls._max_index += 1
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

    @property
    def prequel(self):
        return self._prequel

    @property
    def sequel(self):
        return self._sequel

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
        self._prequel = '' if prequel is None else prequel
        self._sequel = '' if sequel is None else sequel

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
        string = '{}{}{}'.format(self._prequel, self._artist, self._sequel)
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
    def exp_main_artist(self) -> bool:
        return self._exp_main_artist

    @exp_main_artist.setter
    def exp_main_artist(self, value) -> None:
        self._exp_main_artist = value

    @property
    def additional_artists(self) -> List[_Artist]:
        return self._additional_artists

    @additional_artists.setter
    def additional_artists(self, new_artists) -> None:
        for artist in new_artists:
            if type(artist) is not Additional_Artist:
                raise AdditionalArtistException('{} is not an Additional_Artist'.format(artist))
        self._additional_artists = None if new_artists == [] else new_artists

    @property
    def album(self) -> str:
        return self._album

    @album.setter
    def album(self, new_album) -> None:
        self._album = new_album

    @property
    def classical_composers(self) -> Optional[List[_Artist]]:
        return self._classical_composers

    @classical_composers.setter
    def classical_composers(self, new_composers) -> None:
        for composer in new_composers:
            if composer is not None and type(composer) is not _Artist:
                raise ArtistException('{} is not an Artist object'.format(composer))
        self._classical_composers = None if new_composers == [] else new_composers

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
    def featured_in(self) -> str:
        return self._featured_in

    @featured_in.setter
    def featured_in(self, new_featured_in) -> None:
        self._featured_in = new_featured_in

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
                 classical_composers: List[Optional[_Artist]] = None,
                 classical_work: Optional[str] = None,
                 country: Optional[str] = None,
                 year: Optional[int] = None,
                 mix: Optional[str] = None,
                 featured_in: Optional[str] = None,
                 parts: Optional[List[str]] = None) -> None:
        """ Creates a song found on an album.

            :param title:               The title of this song
            :type title:                str

            :param main_artist:         The main artist of this song. If the album is by a single artist, this
                                        is typically not given unless it is included in the song description
                                        on the album
            :type main_artist:          :class:`_Artist`

            :param exp_main_artist:     Used to know if the main artist should appear in exports
            :type exp_main_artist:      bool

            :param additional_artists:  Optional list of additional artists associated with the song
            :type additional_artists:   list(:class:`Additional_Artist`) | None

            :param album:               Name of the album this song is taken from
            :type album:                str

            :param classical_composers: The composer of this classical song
            :type classical_composers:  list(:class:`_Artist`) | None

            :param classical_work:      The classical work this song comes from
            :type classical_work:       str

            :param country:             The country this song is from
            :type country:              str

            :param year:                The year of this song
            :type year:                 str

            :param mix:                 Optional song mix
            :type mix:                  str

            :param featured_in:         Optional movie or show the song was featured in
            :type featured_in:          str

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
                if not isinstance(artist, Additional_Artist):
                    raise AdditionalArtistException('{} is not an Additional_Artist'.format(artist))
        if classical_composers is not None:
            for classical_composer in classical_composers:
                if not isinstance(classical_composer, _Artist):
                    raise ArtistException('{} is not an Artist object'.format(classical_composer))

        self._title = title
        self._main_artist = main_artist
        self._exp_main_artist = exp_main_artist
        self._additional_artists = None if additional_artists == [] else additional_artists
        self._album = album
        self._classical_composers = None if classical_composers == [] else classical_composers
        self._classical_work = classical_work
        self._country = country
        if year is not None and not isinstance(year, int):
            raise SongException('{} is not a valid integer year'.format(year))
        self._year = year
        self._mix = mix
        self._featured_in = featured_in
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
        if self.exp_main_artist:
            html_str += '<br>'
            html_str += '\n' + spaceit('{artist}'.format(artist=self.main_artist.to_html(song_artist=True)), 6)
        if self.additional_artists is not None:
            if not self.exp_main_artist:
                html_str += '<br>'
            for additional_artist in self.additional_artists:
                # html_str += '\n      {}'.format(additional_artist.to_html())
                html_str += '\n' + spaceit('{artist}'.format(artist=additional_artist.to_html()), 6)
        if self.mix is not None:
            html_str += '<br>\n      (<a rel="song-mix">{mix}</a>)'.format(mix=escape(self.mix, quote=False))
        if self.classical_work is not None:
            # must appear before the composer
            html_str += '<br>\n      from <i><a rel="song-classical-work">{work}</a></i>'.format(work=escape(self.classical_work, quote=False))
        if self.classical_composers is not None:
            html_str += '<br>\n      by '
            for index, classical_composer in enumerate(self.classical_composers):
                html_str += '<b><a rel="song-classical-composer">{composer}</a></b>'.format(composer=escape(classical_composer.name, quote=False))
                if index < len(self.classical_composers) - 1:
                    html_str += ' and\n      '
        if self.year is not None:
            html_str += '<br>\n      - <a rel="song-date">{date}</a>'.format(date=self.year)
        if self.country is not None:
            html_str += '<br>\n      - <a rel="song-country">{country}</a>'.format(country=self.country)
        if self.featured_in is not None:
            html_str += '<br>\n      (featured in <a rel="song-featured-in">{movie_or_show}</a>)'.format(movie_or_show=escape(self.featured_in, quote=False))
        if self.parts is not None and self.parts != []:
            html_str += '\n'
            html_str += spaceit('<ol type=I>\n', 4)
            for song_part in self.parts:
                html_str += spaceit('<li><a rel="song-part">{part}</a></li>\n'.format(part=escape(song_part, quote=False)), 6)
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
        if self.classical_composers is not None:
            for composer in self.classical_composers:
                string += '({})\n'.format(composer)
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
    def name(self) -> Optional[str]:
        return self._name

    @name.setter
    def name(self, side_name) -> None:
        self._name = side_name

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
        self._name = side_name
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
        html_str = ''
        if self.name is not None:
            html_str += '<a rel="side">\n'
            html_str += '<h4><blockquote>{side_title}</blockquote></h4>\n'.format(side_title=escape(self.name, quote=False))
        if self.side_mixer is not None:
            html_str += '<h4>Mixed By <a rel="side-mixer">{mixer_name}</a></h4>\n'.format(mixer_name=self.side_mixer)
        html_str += '<ol>\n'
        if self.song_list is not None:
            for song in self.song_list:
             html_str += song.to_html()
        html_str += '</ol>\n'
        if self.name is not None:
            html_str += '</a>\n'
        return html_str

    def __str__(self) -> str:
        if self._name is not None:
            string = '{}'.format(self._name)
        else:
            string = ''
        if self._side_mixer is not None:
            string += 'mixed by {}'.format(self._side_mixer)
        string += '\n'
        if self._song_list is not None:
            for counter, song in enumerate(self._song_list):
                string += '{:2d}. {}'.format(counter + 1, song)
        return string


def media_to_hash(media_type: MediaType, title: str, artist_name: str) -> str:
    """ Create a hash for the media object based on title and artist_name.

        :param media_type:   The media type of the album
        :type media_type:    :class:`MediaType`

        :param title:        The album title
        :type title:         str

        :param artist_name:  The name of the artist of the album
        :type artist_name:   str

        :returns:            md5 hash string
        :rtype:              str
    """
    return md5(bytes(media_type.value + title + artist_name, 'utf-8')).hexdigest()  # nosec


class _MEDIA():
    """ Defines a music media object.

        Note: Should only be instantiated by calling media type object contructor:

              - :func:`LPs().create`
              - :func:`LPs().create`
              - :func:`ELPs().create`
              - :func:`MINI_CDs().create`
    """

    @property
    def index(self) -> int:
        return self._index

    @property
    def hash(self) -> str:
        return self._hash

    @property
    def media_type(self) -> MediaType:
        return self._media_type

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value) -> None:
        self._title = value

    @property
    def artists(self) -> List[_Artist]:
        return self._artists

    @property
    def artist_particles(self) -> Optional[List[str]]:
        return self._artist_particles

    @artist_particles.setter
    def artist_particles(self, particle_list) -> None:
        self._artist_particles = particle_list

    @property
    def artists_text(self) -> str:
        if self.artist_particles is None:
            text = str(self.artists[0].name)
        else:
            text = str(self.artists[0].name)
            for i, particle in enumerate(self.artist_particles):
                text += particle + str(self.artists[i + 1].name)
        return text

    @property
    def year(self) -> int:
        return self._year

    @year.setter
    def year(self, value) -> None:
        self._year = value

    @property
    def mixer(self) -> Optional[_Artist]:
        return self._mixer

    @mixer.setter
    def mixer(self, value) -> None:
        self._mixer = value

    @property
    def classical_composers(self) -> Optional[_Artist]:
        return self._classical_composers

    @classical_composers.setter
    def classical_composers(self, value) -> None:
        self._classical_composers = value

    @property
    def tracks(self) -> List[TrackList]:
        return self._tracks

    def __init__(self,
                 media_type: MediaType,
                 title: str,
                 artists: List[_Artist],
                 year: int,
                 index: int,
                 mixer: Optional[_Artist] = None,
                 classical_composers: Optional[_Artist] = None,
                 artist_particles: Optional[List[str]] = None) -> None:
        if not isinstance(media_type, MediaType):
            raise MediaTypeException('{} is not a valid MediaType'.format(media_type))
        self._media_type = media_type
        self._title = title
        if not isinstance(artists, list):
            raise ArtistException('{} is not a list of Artist objects'.format(artists))
        for artist in artists:
            if not isinstance(artist, _Artist):
                raise ArtistException('{} is not an Artist object'.format(artist))
        self._artists = artists
        if artist_particles is None:
            self._artist_particles = []
        else:
            self._artist_particles = artist_particles
        if not isinstance(year, int):
            raise TypeError('Year must be an int value')
        self._year = year
        if mixer is not None and type(mixer) is not _Artist:
            raise ArtistException('{} is not an Artist object'.format(mixer))
        self._mixer = mixer
        if classical_composers is not None:
            if not isinstance(classical_composers, list):
                raise ArtistException('{} is not a list of Artist objects'.format(classical_composers))
            for classical_composer in classical_composers:
                if type(classical_composer) is not _Artist:
                    raise ArtistException('{} is not an Artist object'.format(classical_composer))
        self._classical_composers = classical_composers
        # Create id hash based on first artist and title
        self._hash = media_to_hash(media_type, title, artists[0].name)
        self._index = index

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
        if isinstance(track, TrackList):
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
        html_str += '<a rel="{media_type}">\n'.format(media_type=self.media_type.value)
        html_str += '<h3><a rel="title">{title}</a></h3>\n'.format(title=escape(self.title, quote=False))
        html_str += '<h3>'
        for index, artist in enumerate(self.artists):
            html_str += '<a rel="artist">{artist}</a>'.format(artist=escape(artist.name, quote=False))
            if self._artist_particles is not None and index < len(self._artist_particles):
                html_str += escape(self._artist_particles[index], quote=False)
        html_str += '</h3>\n'
        if self.classical_composers is not None:
            html_str += '<h3><a rel="classical-composer">{composer}</a>'.format(composer=escape(self.classical_composers[0].name, quote=False))
            if len(self.classical_composers) == 2:
                html_str += ' and <a rel="classical-composer">{composer}</a></h3>\n'.format(composer=escape(self.classical_composers[1].name, quote=False))
            else:
                html_str += '</h3>\n'
        if self.mixer is not None:
            html_str += '<h3>Mixed By <a rel="mixer">{mixer_name}</a></h3>\n'.format(mixer_name=self.mixer)
        html_str += '<h3><a rel="date">{year}</a></h3>\n'.format(year=self.year)
        for track in self.tracks:
            html_str += track.to_html()
        html_str += '</a>\n'
        html_str += '</p>\n'
        return html_str

    def __str__(self) -> str:
        string = '{}\n'.format(self.media_type.value)
        string += '{}\n'.format(self.title)
        string += '{}\n'.format(','.join([artist.name for artist in self.artists]))
        if self.mixer is not None:
            string += 'Mixed by {}\n'.format(self.mixer)
        string += '{}'.format(self.year)
        for track in self.tracks:
            string += str(track)
        string += '\n'
        return string


class _CD(_MEDIA):
    pass


class _LP(_MEDIA):
    pass


class _ELP(_MEDIA):
    pass


class _MINI_CD(_MEDIA):
    pass


class MEDIA():
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

        def get_media_metadata(media_element: Tag) -> (str, List[_Artist], List[str], List[_Artist], List[_Artist], str):
            """ Parse the album tag for the album specific metadata.

                The music media metadata is the title, list of artists, list of composers,
                list of mixers and the year the music media was produced. The composer and mixer list
                may be optional.

                :param media_element:   The Tag node for an music media.
                :type media_element:    :class:`bs2.element.Tag`

                :returns:               A tuple of the album metadata: title, artists, artist particles,
                                        composers, mixers and production year
                :rtype:                 tuple(str, list(:class:`_Artist`), list(str), list(:class:`_Artist`), list(:class:`_Artist`), str)
            """
            media_title = None
            media_artists = []
            media_artist_particles = []
            media_classical_composers = []
            media_mixers = []
            media_date = None
            all_h3_elements = media_element.find_all('h3')
            for h3_element in all_h3_elements:
                # The first content is going to be the anchor tag
                anchor_tag = h3_element.contents[0]
                if isinstance(anchor_tag, Tag):
                    if 'rel' in anchor_tag.attrs.keys():
                        rel_value = anchor_tag['rel'][0]
                        if rel_value == 'title':
                            media_title = anchor_tag.text.strip()
                        elif rel_value == 'artist':
                            next_tag = anchor_tag
                            while next_tag is not None:
                                lp_artist_name = next_tag.text.strip()
                                media_artists.append(Artists.create_Artist(lp_artist_name))
                                if isinstance(next_tag.next_sibling, NavigableString):
                                    next_tag = next_tag.next_sibling
                                    media_artist_particles.append(next_tag.text)
                                next_tag = next_tag.next_sibling
                        elif rel_value == 'classical-composer':
                            media_classical_composer_elements = h3_element.find_all('a', rel='classical-composer')
                            for media_classical_composer_element in media_classical_composer_elements:
                                media_classical_composer_name = media_classical_composer_element.text.strip()
                                media_classical_composer = Artists.create_Artist(media_classical_composer_name)
                                media_classical_composers.append(media_classical_composer)
                        elif rel_value == 'date':
                            media_date = anchor_tag.text.strip()
                elif isinstance(anchor_tag, NavigableString):
                    # Mixer entry starts as "Mixed By"
                    media_mixer_elements = h3_element.find_all('a', rel='mixer')
                    for media_mixer_element in media_mixer_elements:
                        media_mixer_name = media_mixer_element.text.strip()
                        media_mixers.append(Artists.create_Artist(media_mixer_name))

            # Track down albums with more than two classical composer credits
            if len(media_classical_composers) > 2:
                print('Title: {}'.format(media_title))
                assert (len(media_classical_composers) <= 2)  # nosec

            # Track down albums with more than one mixer credit
            if len(media_mixers) > 1:
                print('Title: {}'.format(media_title))
                assert (len(media_mixers) == 1)  # nosec

            return media_title, media_artists, media_artist_particles, media_classical_composers, media_mixers, media_date

        def get_song_additional_artists(song_block: Tag, media_artist: _Artist) -> (_Artist, List[Additional_Artist]):
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

                :param media_artist:        The artist of the music media which is the main song artist
                                            except on a Various Artists music media
                :type media_artist:         :class:`_Artist`

                :returns:                   Main song artist if they exists and a list of additional
                                            song artists. Main artist should only occur on "Various
                                            Artist" music media
                :rtype:                     tuple(_Artist | None, list(Additional_Artist))
            """
            main_artist = media_artist
            other_artists = []
            exp_main_artist = False
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
                            first_block = False
                            prequel = sequel = ''
                            artist_name = artist_name_block.text.strip()
                            song_artist = Artists.create_Artist(artist_name)
                            if artist_block == all_artist_blocks[0]:
                                # Special handling of first block for the prequel and main artist
                                first_block = True
                                prequel = first_prequel
                                if media_artist.name.upper() == Artists.VARIOUS_ARTISTS:
                                    main_artist = song_artist
                                elif song_artist.name.upper() == media_artist.name.upper():
                                    exp_main_artist = True

                            if isinstance(artist_block.next_sibling, NavigableString):
                                sequel = artist_block.next_sibling.text.split('\n')[0]

                            # Do not add to the additional artists list if dealing with an exported
                            # album main artist
                            if (first_block and not exp_main_artist) or not first_block:
                                other_artists.append(Additional_Artist(song_artist, prequel=prequel, sequel=sequel))

            return main_artist, other_artists, exp_main_artist

        with open(filepath, 'r') as fp:
            # Parse the formatted file for LPs
            html = fp.read()
            parsed_html = BeautifulSoup(html, features="html.parser")

            # Parse out all the LPs which start with <p> tags
            all_p_elements = parsed_html.find_all('p')
            for p_element in all_p_elements:

                # Now get the <a> tag which encloses all the rest of
                # the information we want to get
                media_element = p_element.contents[1]  # Skipping new line after <p> tag
                media_type = MediaType(media_element['rel'][0])
                media_title, media_artists, media_artist_particles, media_classical_composers, media_mixers, media_date = get_media_metadata(media_element)
                media_song_artists = []

                # Process each side of the lp
                media_tracklist = []
                all_side_elements = media_element.find_all('a', rel='side')
                if len(all_side_elements) == 0:
                    # No labelled side like CD
                    all_side_elements = [media_element.find('ol')]

                for side_element in all_side_elements:
                    side_title = None
                    side_mixer = None
                    any_additional_side_metadata = side_element.find('h4') is not None
                    if any_additional_side_metadata:
                        side_title = side_element.find('h4').text.strip()
                        side_mixer_name = rel_element_text(side_element, 'side-mixer')
                        if side_mixer_name is not None:
                            side_mixer = Artists.create_Artist(side_mixer_name)
                            media_song_artists.append(side_mixer)

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
                        main_artist = media_artists[0]
                        additional_artists = None
                        exp_main_artist = False

                        # Determine main song, additional song artists with prequel and sequel information.
                        # and if main artist should be exposed.
                        song_main_artist, song_additional_artists, exp_main_artist = get_song_additional_artists(song_block, media_artists[0])
                        if song_main_artist is not None:
                            main_artist = song_main_artist
                        if song_additional_artists != []:
                            for additional_artist in song_additional_artists:
                                media_song_artists.append(additional_artist.artist)
                            additional_artists = song_additional_artists

                        song_classical_composer_nodes = song_block.find_all('a', rel='song-classical-composer')
                        song_classical_composers = []
                        if song_classical_composer_nodes is not None:
                            for song_classical_composer_node in song_classical_composer_nodes:
                                song_classical_composer = Artists.create_Artist(song_classical_composer_node.text.strip())
                                song_classical_composers.append(song_classical_composer)
                                media_song_artists.append(song_classical_composer)
                        if song_classical_composers == []:
                            # Set to None if we find no classical composers
                            song_classical_composers = None

                        song_classical_work = rel_element_text(song_block, 'song-classical-work')
                        song_country = rel_element_text(song_block, 'song-country')
                        song_date = rel_element_text(song_block, 'song-date')
                        if song_date is not None:
                            song_date = int(song_date)
                        song_mix = rel_element_text(song_block, 'song-mix')
                        song_featured_in = rel_element_text(song_block, 'song-featured-in')

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
                                               classical_composers=song_classical_composers,
                                               classical_work=song_classical_work,
                                               country=song_country,
                                               year=song_date,
                                               mix=song_mix,
                                               featured_in=song_featured_in,
                                               parts=song_parts))
                    side_tracklist = TrackList(side_name=side_title, side_mixer_artist=side_mixer, songs=side_Songs)
                    media_tracklist.append(side_tracklist)

                # Create the LP and add it to all the artists found
                # TODO: Handle artists vs composers vs mixers
                if media_mixers == []:
                    media_mixer = None
                else:
                    media_mixer = media_mixers[0]
                if media_classical_composers == []:
                    media_classical_composers = None

                # This is a bit awkward but to keep the integrity of the
                # media type singletons, we farm out the data creation and
                # updates to each individual media singleton. Perhaps
                # we could use inheritance from a "MEDIAs" superclass?

                # Handle LP music media
                if media_type == MediaType.CD:
                    new_Media = CDs.create(media_type=media_type,
                                           title=media_title,
                                           artists=media_artists,
                                           year=int(media_date),
                                           mixer=media_mixer,
                                           classical_composers=media_classical_composers,
                                           artist_particles=media_artist_particles)

                # Handle CD music media
                elif media_type == MediaType.LP:
                    new_Media = LPs.create(media_type=media_type,
                                           title=media_title,
                                           artists=media_artists,
                                           year=int(media_date),
                                           mixer=media_mixer,
                                           classical_composers=media_classical_composers,
                                           artist_particles=media_artist_particles)

                # Handle ELP music media
                elif media_type == MediaType.ELP:
                    new_Media = ELPs.create(media_type=media_type,
                                            title=media_title,
                                            artists=media_artists,
                                            year=int(media_date),
                                            mixer=media_mixer,
                                            classical_composers=media_classical_composers,
                                            artist_particles=media_artist_particles)

                # Handle mini CD music media
                elif media_type == MediaType.MINI_CD:
                    new_Media = MINI_CDs.create(media_type=media_type,
                                                title=media_title,
                                                artists=media_artists,
                                                year=int(media_date),
                                                mixer=media_mixer,
                                                classical_composers=media_classical_composers,
                                                artist_particles=media_artist_particles)
                for tracklist in media_tracklist:
                    new_Media.add_track(tracklist)

                # Add LP to all song artists found once we dedupe them
                for artist in set(media_song_artists):
                    # Need to skip any that are also album artists since they have
                    # already been added
                    if artist not in media_artists:
                        artist.add_media(new_Media)

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
        """ Return an html representation of all music media

            :returns:  An html representation of all music media
            :rtype:    str
        """
        HTML_HEADER = """<!DOCTYPE PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html lang="en">
<head>
<title>Music List</title>
</head>
<body>
<h2>Audio Media</h2>
"""
        HTML_CLOSER = """</body>
</html>
"""
        html_str = HTML_HEADER
        html_str += CDs.to_html()
        html_str += LPs.to_html()
        html_str += ELPs.to_html()
        html_str += MINI_CDs.to_html()
        html_str += HTML_CLOSER
        return html_str


class LPs():
    """ A singleton list of all music LPs. """
    _instance = None
    _lps = []
    _max_index = 0

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
        cls._max_index = 0

    @classmethod
    def create(cls,
               media_type: MediaType,
               title: str,
               artists: List[_Artist],
               year: int,
               mixer: Optional[_Artist] = None,
               classical_composers: Optional[_Artist] = None,
               artist_particles: List[str] = None,
               skip_adding_to_lp_list: bool = False) -> _LP:
        """ Return the named album if it exists or create a new album.

            By default a new album is added to the list of all albums.

            :param media_type:               The media type of the music album
            :type media_type:                :class:`MediaType`

            :param title:                    The title of the new album
            :type name:                      str

            :param artists:                  The list of album artists
            :type artists:                   list(:class:`_Artist`)

            :param year:                     The year the album was published
            :type year:                      int

            :param mixer:                   Optional album mixer
            :type mixer:                    :class:`_Artist` | None

            :param classical_composers:     Optional album classical composers
            :type classical_composers:      list(:class:`_Artist`) | None

            :param artist_particles:         Particle text linking artists
            :type artist_particles:          list(str) | None

            :param skip_addiing_to_lp_list:  If true, do not add new album to albums list
            :type skip_adding_to_lp_list:    bool

            :returns:                        The located or newly created album
            :rtype:                          :class:`_LP`
        """
        # We need to perform this check before searching for an existing album as we need a valid
        # artist name to search
        if not isinstance(artists, list):
            raise ArtistException('{} is not a list of artists'.format(artists))
        for artist in artists:
            if not isinstance(artist, _Artist):
                raise ArtistException('{} is not a an artist'.format(artist))

        results = cls.find_by_title(title)
        if len(results) > 0:
            # Need to check hash id
            new_album_hash = media_to_hash(media_type, title, artists[0].name)
            for result in results:
                if result._hash == new_album_hash:
                    return result
        # Create the new album
        new_lp = _LP(media_type, title, artists, year, cls._max_index, mixer, classical_composers, artist_particles)
        cls._max_index += 1
        for artist in artists:
            artist.add_media(new_lp)
        if mixer is not None:
            mixer.add_media(new_lp)
        if classical_composers is not None:
            for classical_composer in classical_composers:
                classical_composer.add_media(new_lp)
        if not skip_adding_to_lp_list:
            cls.add(new_lp)
        return new_lp

    @classmethod
    def add(cls, lp: _LP) -> None:
        """ Add an album to the list of all albums.

            :param lp:            The album to add
            :type lp:             :class:`_LP`

            :raises LPException:  If not passed a :class:`_LP` or the lp already exists in the list
        """
        if type(lp) is not _LP:
            raise LPException('{} is not an LP object'.format(lp))
        if lp in cls._lps:
            raise LPException('LP {} already exists'.format(lp))
        cls._lps.append(lp)

    @classmethod
    def delete(cls, lp: _LP) -> None:
        """ Remove the album from the list of all albums.

            In actuality we pug the location in the list of
            all albums with None to preserve the increasing
            index scheme used in the list.

            Also remove the album from the list of all albums owned by
            the album artist and album mixer (if they exist)

            :param lp:  The album to add
            :type lp:   :class:`_LP`
        """
        if lp in cls._lps:
            for artist in lp.artists:
                artist.delete_media(lp)
            if lp.mixer is not None:
                lp.mixer.delete_media(lp)
            make_hole_index = lp.index
            cls._lps[make_hole_index] = None

    @classmethod
    def exists(cls, lp: _LP) -> bool:
        """ Returns true of the album exists in the list of albums.

            :param lp:  The album to add
            :type lp:   :class:`_LP`

            :returns:   True if the album exists in the list of all albums
            :rtype:     bool
        """
        return lp in cls._lps

    @classmethod
    def find_by_index(cls, index: int) -> Optional[_LP]:
        """ Return the album by its index or None if not found.

            :param index:   The index in the list of albums of the album to locate
            :type index:    int

            :returns:       The album or None
            :rtype:         class:`_LP` or None
        """
        lp = None
        try:
            lp = cls._lps[index]
        except IndexError:
            pass
        return lp

    @classmethod
    def find_by_title(cls, title: str) -> List[_LP]:
        """ Returns the albums in the list of all albums that matches the passed album title. Otherwise, empty list.

            :param title:  The album title to search for
            :type title:   str

            :returns:      The album if found. None, otherwise
            :rtype:        list(:class:`_LP` )
         """
        result = []
        for lp in cls._lps:
            if lp is not None:  # Skip holes in the list due to deletions
                if lp.title == title:
                    result.append(lp)
        return result

    @classmethod
    def find_by_year(cls, year: int) -> List[_LP]:
        """ Return a list of albums produced in the passed year.

            :param year:  Find albums produced in this year
            :type year:   int

            :returns:     A list of albums produced in that year
            :rtype:       list(:class:`_LP`) | None
        """
        lps_found = []
        for lp in cls._lps:
            if lp is not None:  # Skip holes in the list due to deletions
                if lp.year == year:
                    lps_found.append(lp)
        if lps_found == []:
            return None
        return lps_found

    @classmethod
    def to_html(cls):
        """ Return an html representation of all albums

            :returns:  An html representation of all albums
            :rtype:    str
        """
        html_str = ''
        for lp in cls._lps:
            if lp is not None:  # Skip holes in the list due to deletions
                html_str += lp.to_html()
        return html_str

    def __str__(self) -> str:
        string = ''
        for lp in self.lps:
            if lp is not None:  # Skip holes in the list due to deletions
                string += str(lp)
        return string


class CDs():
    """ A singleton list of all music CDs. """
    _instance = None
    _cds = []
    _max_index = 0

    @property
    def cds(self) -> List[_CD]:
        return self._cds

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CDs, cls).__new__(cls)
        return cls._instance

    @classmethod
    def _clean_cds(cls):
        """ Private method to remove all albums from the collection. Useful in testing. """
        cls._cds = []
        cls._max_index = 0

    @classmethod
    def create(cls,
               media_type: MediaType,
               title: str,
               artists: List[_Artist],
               year: int,
               mixer: Optional[_Artist] = None,
               classical_composers: Optional[_Artist] = None,
               artist_particles: List[str] = None,
               skip_adding_to_cd_list: bool = False) -> _CD:
        """ Return the named cd if it exists or create a new cd.

            By default a new cd is added to the list of all cds.

            :param media_type:               The media type of the music cd
            :type media_type:                :class:`MediaType`

            :param title:                    The title of the new album
            :type name:                      str

            :param artists:                  The list of cd artists
            :type artists:                   list(:class:`_Artist`)

            :param year:                     The year the cd was published
            :type year:                      int

            :param mixer:                    Optional cd mixer
            :type mixer:                     :class:`_Artist` | None

            :param classical_composers:      Optional cd classical composers
            :type classical_composers:       list(:class:`_Artist`) | None

            :param artist_particles:         Particle text linking artists
            :type artist_particles:          list(str) | None

            :param skip_addiing_to_cd_list:  If true, do not add new cd to cd list
            :type skip_adding_to_cd_list:    bool

            :returns:                        The located or newly created cd
            :rtype:                          :class:`_CD`
        """
        # We need to perform this check before searching for an existing cd as we need a valid
        # artist name to search
        if not isinstance(artists, list):
            raise ArtistException('{} is not a list of artists'.format(artists))
        for artist in artists:
            if not isinstance(artist, _Artist):
                raise ArtistException('{} is not a an artist'.format(artist))

        results = cls.find_by_title(title)
        if len(results) > 0:
            # Need to check hash id
            new_cd_hash = media_to_hash(media_type, title, artists[0].name)
            for result in results:
                if result._hash == new_cd_hash:
                    return result
        # Create the new album
        new_cd = _CD(media_type, title, artists, year, cls._max_index, mixer, classical_composers, artist_particles)
        cls._max_index += 1
        for artist in artists:
            artist.add_media(new_cd)
        if mixer is not None:
            mixer.add_media(new_cd)
        if classical_composers is not None:
            for classical_composer in classical_composers:
                classical_composer.add_media(new_cd)

        if not skip_adding_to_cd_list:
            cls.add(new_cd)
        return new_cd

    @classmethod
    def add(cls, cd: _CD) -> None:
        """ Add a cd to the list of all cds.

            :param cd:            The cd to add
            :type cd:             :class:`_CD`

            :raises CDException:  If not passed a :class:`_CD` or the cd already exists in the list
        """
        if type(cd) is not _CD:
            raise CDException('{} is not a CD object'.format(cd))
        if cd in cls._cds:
            raise CDException('CD {} already exists'.format(cd))
        cls._cds.append(cd)

    @classmethod
    def delete(cls, cd: _LP) -> None:
        """ Remove the cd from the list of all cd.

            In actuality we pug the location in the list of
            all CDs with None to preserve the increasing
            index scheme used in the list.

            Also remove the cd from the list of all cds owned by
            the cd artist and cd mixer (if they exist)

            :param cd:  The cd to add
            :type cd:   :class:`_CD`
        """
        if cd in cls._cds:
            for artist in cd.artists:
                artist.delete_media(cd)
            if cd.mixer is not None:
                cd.mixer.delete_media(cd)
            make_hole_index = cd.index
            cls._cds[make_hole_index] = None

    @classmethod
    def exists(cls, cd: _CD) -> bool:
        """ Returns true of the cd exists in the list of cds.

            :param cd:  The cd to add
            :type cd:   :class:`_CD`

            :returns:   True if the cd exists in the list of all cds
            :rtype:     bool
        """
        return cd in cls._cds

    @classmethod
    def find_by_index(cls, index: int) -> Optional[_CD]:
        """ Return the cd by its index or None if not found.

            :param index:   The index in the list of cds of the cd to locate
            :type index:    int

            :returns:       The cd or None
            :rtype:         class:`_CD` or None
        """
        cd = None
        try:
            cd = cls._cds[index]
        except IndexError:
            pass
        return cd

    @classmethod
    def find_by_title(cls, title: str) -> List[_CD]:
        """ Returns the cds in the list of all cds that matches the passed cd title. Otherwise, empty list.

            :param title:  The cd title to search for
            :type title:   str

            :returns:      The cd if found. None, otherwise
            :rtype:        list(:class:`_CD` )
         """
        result = []
        for cd in cls._cds:
            if cd is not None:  # Skip holes in the list due to deletions
                if cd.title == title:
                    result.append(cd)
        return result

    @classmethod
    def find_by_year(cls, year: int) -> List[_LP]:
        """ Return a list of cds produced in the passed year.

            :param year:  Find cds produced in this year
            :type year:   int

            :returns:     A list of cds produced in that year
            :rtype:       list(:class:`_CD`) | None
        """
        cds_found = []
        for cd in cls._cds:
            if cd is not None:  # Skip holes in the list due to deletions
                if cd.year == year:
                    cds_found.append(cd)
        if cds_found == []:
            return None
        return cds_found

    @classmethod
    def to_html(cls):
        """ Return an html representation of all cds

            :returns:  An html representation of all cds
            :rtype:    str
        """
        html_str = ''
        for cd in cls._cds:
            if cd is not None:  # Skip holes in the list due to deletions
                html_str += cd.to_html()
        return html_str

    def __str__(self) -> str:
        string = ''
        for cd in self.cds:
            if cd is not None:  # Skip holes in the list due to deletions
                string += str(cd)
        return string


class ELPs():
    """ A singleton list of all music ELPs. """
    _instance = None
    _elps = []
    _max_index = 0

    @property
    def elps(self) -> List[_ELP]:
        return self._elps

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ELPs, cls).__new__(cls)
        return cls._instance

    @classmethod
    def _clean_elps(cls):
        """ Private method to remove all elps from the collection. Useful in testing. """
        cls._elps = []
        cls._max_index = 0

    @classmethod
    def create(cls,
               media_type: MediaType,
               title: str,
               artists: List[_Artist],
               year: int,
               mixer: Optional[_Artist] = None,
               classical_composers: Optional[_Artist] = None,
               artist_particles: List[str] = None,
               skip_adding_to_elp_list: bool = False) -> _ELP:
        """ Return the named elp if it exists or create a new elp.

            By default a new elp is added to the list of all elps.

            :param media_type:                The media type of the music elp
            :type media_type:                 :class:`MediaType`

            :param title:                     The title of the new elp
            :type name:                       str

            :param artists:                   The list of elp artists
            :type artists:                    list(:class:`_Artist`)

            :param year:                      The year the elp was published
            :type year:                       int

            :param mixer:                     Optional elp mixer
            :type mixer:                      :class:`_Artist` | None

            :param classical_composers:       Optional elp classical composers
            :type classical_composers:        list(:class:`_Artist`) | None

            :param artist_particles:          Particle text linking artists
            :type artist_particles:           list(str) | NOne

            :param skip_addiing_to_elp_list:  If true, do not add new elp to elps list
            :type skip_adding_to_elp_list:    bool

            :returns:                         The located or newly created elp
            :rtype:                           :class:`_ELP`
        """
        # We need to perform this check before searching for an existing elp as we need a valid
        # artist name to search
        if not isinstance(artists, list):
            raise ArtistException('{} is not a list of artists'.format(artists))
        for artist in artists:
            if not isinstance(artist, _Artist):
                raise ArtistException('{} is not a an artist'.format(artist))

        results = cls.find_by_title(title)
        if len(results) > 0:
            # Need to check hash id
            new_elp_hash = media_to_hash(media_type, title, artists[0].name)
            for result in results:
                if result._hash == new_elp_hash:
                    return result
        # Create the new elp
        new_elp = _ELP(media_type, title, artists, year, cls._max_index, mixer, classical_composers, artist_particles)
        cls._max_index += 1
        for artist in artists:
            artist.add_media(new_elp)
        if mixer is not None:
            mixer.add_media(new_elp)
        if classical_composers is not None:
            for classical_composer in classical_composers:
                classical_composer.add_media(new_elp)

        if not skip_adding_to_elp_list:
            cls.add(new_elp)
        return new_elp

    @classmethod
    def add(cls, elp: _ELP) -> None:
        """ Add an elp to the list of all elps.

            :param elp:            The elp to add
            :type elp:             :class:`_ELP`

            :raises ELPException:  If not passed a :class:`_ELP` or the elp already exists in the list
        """
        if type(elp) is not _ELP:
            raise ELPException('{} is not an ELP object'.format(elp))
        if elp in cls._elps:
            raise ELPException('ELP {} already exists'.format(elp))
        cls._elps.append(elp)

    @classmethod
    def delete(cls, elp: _ELP) -> None:
        """ Remove the elp from the list of all elps.

            In actuality we pug the location in the list of
            all ELPs with None to preserve the increasing
            index scheme used in the list.

            Also remove the elp from the list of all elps owned by
            the elp artist and elp mixer (if they exist)

            :param elp:  The elp to add
            :type elp:   :class:`_ELP`
        """
        if elp in cls._elps:
            for artist in elp.artists:
                artist.delete_media(elp)
            if elp.mixer is not None:
                elp.mixer.delete_media(elp)
            make_hole_index = elp.index
            cls.elps[make_hole_index] = None

    @classmethod
    def exists(cls, elp: _ELP) -> bool:
        """ Returns true of the elp exists in the list of elps.

            :param elp:  The elp to add
            :type elp:   :class:`_ELP`

            :returns:    True if the elp exists in the list of all elps
            :rtype:      bool
        """
        return elp in cls._elps

    @classmethod
    def find_by_index(cls, index: int) -> Optional[_ELP]:
        """ Return the elp by its index or None if not found.

            :param index:   The index in the list of elps of the elp to locate
            :type index:    int

            :returns:       The elp or None
            :rtype:         class:`_ELP` or None
        """
        elp = None
        try:
            elp = cls._elps[index]
        except IndexError:
            pass
        return elp

    @classmethod
    def find_by_title(cls, title: str) -> List[_ELP]:
        """ Returns the elps in the list of all elps that matches the passed elp title. Otherwise, empty list.

            :param title:  The elp title to search for
            :type title:   str

            :returns:      The elp if found. None, otherwise
            :rtype:        list(:class:`_ELP` )
         """
        result = []
        for elp in cls._elps:
            if elp is not None:  # Skip holes in the list due to deletions
                if elp.title == title:
                    result.append(elp)
        return result

    @classmethod
    def find_by_year(cls, year: int) -> List[_ELP]:
        """ Return a list of elps produced in the passed year.

            :param year:  Find elps produced in this year
            :type year:   int

            :returns:     A list of elps produced in that year
            :rtype:       list(:class:`_ELP`) | None
        """
        elps_found = []
        for elp in cls._elps:
            if elp is not None:  # Skip holes in the list due to deletions
                if elp.year == year:
                    elps_found.append(elp)
        if elps_found == []:
            return None
        return elps_found

    @classmethod
    def to_html(cls):
        """ Return an html representation of all elps

            :returns:  An html representation of all elps
            :rtype:    str
        """
        html_str = ''
        for elp in cls._elps:
            if elp is not None:  # Skip holes in the list due to deletions
                html_str += elp.to_html()
        return html_str

    def __str__(self) -> str:
        string = ''
        for elp in self.elps:
            if elp is not None:  # Skip holes in the list due to deletions
                string += str(elp)
        return string


class MINI_CDs():
    """ A singleton list of all music mini CDs. """
    _instance = None
    _mini_cds = []
    _max_index = 0

    @property
    def mini_cds(self) -> List[_MINI_CD]:
        return self._mini_cds

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MINI_CDs, cls).__new__(cls)
        return cls._instance

    @classmethod
    def _clean_mini_cds(cls):
        """ Private method to remove all mini CDs from the collection. Useful in testing. """
        cls._mini_cds = []
        cls._max_index = 0

    @classmethod
    def create(cls,
               media_type: MediaType,
               title: str,
               artists: List[_Artist],
               year: int,
               mixer: Optional[_Artist] = None,
               classical_composers: Optional[_Artist] = None,
               artist_particles: List[str] = None,
               skip_adding_to_mini_cd_list: bool = False) -> _MINI_CD:
        """ Return the named mini CD if it exists or create a new mini_cd.

            By default a new mini CD is added to the list of all mini CDs.

            :param media_type:                    The media type of the music mini CD
            :type media_type:                     :class:`MediaType`

            :param title:                         The title of the new mini CD
            :type name:                           str

            :param artists:                       The list of mini CD artists
            :type artists:                        list(:class:`_Artist`)

            :param year:                          The year the mini CD was published
            :type year:                           int

            :param mixer:                         Optional mini CD mixer
            :type mixer:                          :class:`_Artist` | None

            :param classical_composers:           Optional mini CD classical composers
            :type classical_composers:            list(:class:`_Artist`) | None

            :param artist_particles:              Particle text linking artists
            :type artist_particles:               list(str) | None

            :param skip_addiing_to_mini_cd_list:  If true, do not add new mini CD to mini_cds list
            :type skip_adding_to_mini_cd_list:    bool

            :returns:                             The located or newly created mini CD
            :rtype:                               :class:`_MINI_CD`
        """
        # We need to perform this check before searching for an existing mini CD as we need a valid
        # artist name to search
        if not isinstance(artists, list):
            raise ArtistException('{} is not a list of artists'.format(artists))
        for artist in artists:
            if not isinstance(artist, _Artist):
                raise ArtistException('{} is not a an artist'.format(artist))

        results = cls.find_by_title(title)
        if len(results) > 0:
            # Need to check hash id
            new_mini_cd_hash = media_to_hash(media_type, title, artists[0].name)
            for result in results:
                if result._hash == new_mini_cd_hash:
                    return result
        # Create the new mini CD
        new_mini_cd = _MINI_CD(media_type, title, artists, year, cls._max_index, mixer, classical_composers, artist_particles)
        cls._max_index += 1
        for artist in artists:
            artist.add_media(new_mini_cd)
        if mixer is not None:
            mixer.add_media(new_mini_cd)
        if classical_composers is not None:
            for classical_composer in classical_composers:
                classical_composer.add_media(new_mini_cd)

        if not skip_adding_to_mini_cd_list:
            cls.add(new_mini_cd)
        return new_mini_cd

    @classmethod
    def add(cls, mini_cd: _MINI_CD) -> None:
        """ Add an mini_cd to the list of all mini CDs.

            :param mini_cd:            The mini CD to add
            :type mini_cd:             :class:`_MINI_CD`

            :raises MINI_CDException:  If not passed a :class:`_MINI_CD` or the mini CD already exists in the list
        """
        if type(mini_cd) is not _MINI_CD:
            raise MiniCDException('{} is not an mini CD object'.format(mini_cd))
        if mini_cd in cls._mini_cds:
            raise MiniCDException('Mini CD {} already exists'.format(mini_cd))
        cls._mini_cds.append(mini_cd)

    @classmethod
    def delete(cls, mini_cd: _MINI_CD) -> None:
        """ Remove the mini CD from the list of all mini CDs.

            In actuality we pug the location in the list of
            all ELPs with None to preserve the increasing
            index scheme used in the list.

            Also remove the mini_cd from the list of all mini CDs owned by
            the mini CD artist and mini CD mixer (if they exist)

            :param mini_cd:  The mini CD to add
            :type mini_cd:   :class:`_MINI_CD`
        """
        if mini_cd in cls._mini_cds:
            for artist in mini_cd.artists:
                artist.delete_media(mini_cd)
            if mini_cd.mixer is not None:
                mini_cd.mixer.delete_media(mini_cd)
            make_hole_index = mini_cd.index
            cls._mini_cds[make_hole_index] = None

    @classmethod
    def exists(cls, mini_cd: _MINI_CD) -> bool:
        """ Returns true of the mini CD exists in the list of mini CDs.

            :param mini_cd:  The mini CD to add
            :type mini_cd:   :class:`_MINI_CD`

            :returns:        True if the mini CD exists in the list of all mini CDs
            :rtype:          bool
        """
        return mini_cd in cls._mini_cds

    @classmethod
    def find_by_index(cls, index: int) -> Optional[_MINI_CD]:
        """ Return the mini CD by its index or None if not found.

            :param index:   The index in the list of mini CDs of the mini CD to locate
            :type index:    int

            :returns:       The mini CD or None
            :rtype:         class:`_MINI_CD` or None
        """
        mini_cd = None
        try:
            mini_cd = cls._mini_cds[index]
        except IndexError:
            pass
        return mini_cd

    @classmethod
    def find_by_title(cls, title: str) -> List[_MINI_CD]:
        """ Returns the mini CDs in the list of all mini CDs that matches the passed mini CD title. Otherwise, empty list.

            :param title:  The mini CD title to search for
            :type title:   str

            :returns:      The mini CD if found. None, otherwise
            :rtype:        list(:class:`_MINI_CD` )
         """
        result = []
        for mini_cd in cls._mini_cds:
            if mini_cd is not None:  # Skip holes in the list due to deletions
                if mini_cd.title == title:
                    result.append(mini_cd)
        return result

    @classmethod
    def find__by_year(cls, year: int) -> List[_MINI_CD]:
        """ Return a list of mini CDs produced in the passed year.

            :param year:  Find mini CDs produced in this year
            :type year:   int

            :returns:     A list of mini CDs produced in that year
            :rtype:       list(:class:`_MINI_CD`) | None
        """
        mini_cds_found = []
        for mini_cd in cls._mini_cds:
            if mini_cd is not None:  # Skip holes in the list due to deletions
                if mini_cd.year == year:
                    mini_cds_found.append(mini_cd)
        if mini_cds_found == []:
            return None
        return mini_cds_found

    @classmethod
    def to_html(cls):
        """ Return an html representation of all mini CDs

            :returns:  An html representation of all mini CDs
            :rtype:    str
        """
        html_str = ''
        for mini_cd in cls._mini_cds:
            if mini_cd is not None:  # Skip holes in the list due to deletions
                html_str += mini_cd.to_html()
        return html_str

    def __str__(self) -> str:
        string = ''
        for mini_cd in self.mini_cds:
            if mini_cd is not None:  # Skip holes in the list due to deletions
                string += str(mini_cd)
        return string
