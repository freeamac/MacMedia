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
from typing import List, Optional, Set


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
            raise LPException('{} already in list of LPs for {}'.format(lp.name, self.name))
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

    def update_name(self, new_name: str) -> None:
        """ Update the name of the artist.

            :param new_name:  The new name of the artist
            :type new_name:   str
        """
        self._name = new_name

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name


class Artists():
    """ A singleton set of all music artists. """
    _instance = None
    _artists = set()

    @property
    def artists(self) -> Set[_Artist]:
        """ Set of all artists. """
        return self._artists

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Artists, cls).__new__(cls)
        return cls._instance

    def _clean_artists(self):
        """ Private method to remove all artists from the collection. Useful in testing. """
        self._artists = set()

    def create_Artist(self, name: str, skip_adding_to_artists_set: bool = False) -> _Artist:
        """ Return the named artist if they exist or create a new artist.

            By default a new artist is added to the set of all artists.

            :param name:                          The name of the new artist
            :type name:                           str

            :param skip_addiing_to_artists_set:  If true, do not add new artist to artists set
            :type skip_adding_to_artists_set:    bool

            :raises ArtistException:              If there is no passed name

            :returns:                             The located or newly created artist
            :rtype:                               :class:`_Artist`
        """
        if name is None or '':
            raise ArtistException('An artist must have a name')
        result = self.find_artist(name)
        if result is not None:
            return result
        new_artist = _Artist(name)
        if not skip_adding_to_artists_set:
            self.add_artist(new_artist)
        return new_artist

    def add_artist(self, artist: _Artist) -> None:
        """ Add an artist to the set of all artists.

            :param artist:            The artist to add
            :type artist:             :class:`_Artist`

            :raises ArtistException:  If a :class:`_Artist` is not passed or the artist
                                      already exists in the set
        """
        if type(artist) is not _Artist:
            raise ArtistException('{} is not an Artist object'.format(artist))
        if artist in self.artists or self.find_artist(artist.name) is not None:
            raise ArtistException('Artist {} already exists'.format(artist))
        self._artists.add(artist)

    def delete_artist(self, artist: _Artist) -> None:
        """ Delete an artist from the set of all artists.

            :param artist:            The artist to delete
            :type artist:             :class:`_Artist`

            :raises ArtistException:  If artist does not exist in the set
        """
        if artist not in self.artists:
            raise ArtistException('Artist {} does not exist'.format(artist))
        else:
            self._artists.remove(artist)

    def artist_exists(self, artist: _Artist) -> bool:
        """ True if the artist is in the set of artists.

            :param artist:  The artist to add
            :type artist:   :class:`_Artist`

            :returns:       True if the artist exists in the set of all artists
            :rtype:         bool
        """
        return artist in self.artists

    def find_artist(self, artist_name: str) -> Optional[_Artist]:
        """ Returns the artist if an artist of that name exists in the set of all artists.

            :param artist_name:  Name of the artist to find
            :type artist_name:   str

            :returns:            The artist if an artist of that name is found. Otherwise None
            :rtype:              :class:`_Artist` if found, otherwise None
        """
        for artist in self._artists:
            if artist.name == artist_name:
                return artist

    def __str__(self) -> str:
        string = ''
        for artist in self.artists:
            string += '{}\n'.format(artist)
            string += '  Albums\n'
            string += '  ------\n'
            for lp in artist.lps:
                string += '  {}\n'.format(lp.title)
            string += '\n'
        return string


class Additional_Artist():
    """ Formatting structure used for additional artists associated with a :class:`Song`. """

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
        self.artist = artist
        self.prequel = prequel
        self.sequel = sequel

    def __str__(self) -> str:
        if self.prequel is not None:
            string = '{}{}'.format(self.prequel, self.artist)
        else:
            string = '{}'.format(self.artist)
        if self.sequel is not None:
            string += self.sequel
        return string


class Song():
    """ A song found on an album. """

    def __init__(self, title: str, main_artist: Optional[_Artist] = None, additional_artists: List[_Artist] = [], mix: Optional[str] = None) -> None:
        """ Creates a song found on an album.

            :param title:               The title of the song
            :type title:                str

            :param main_artist:         The main artist of the song. If the album is by a single artitst, this
                                        is typically not given unless it is included in the song description
                                        on the album
            :type main_artist:          :class:`_Artist`

            :param additional_artists:  Optional list of additional artists associated with the song
            :type additional_artists:   list(:class:`Additional_Artist`)

            :param mix:                 Optional song mix
            :type mix                   str

            :raises ArtistException:    If main artist is not None or :class:`_Artist`

            :raises AdditionalArtistException:  If pass list of additional artists are not all of type
                                                :class:`Additional_Artist`
            """
        self.title = title
        if main_artist is not None and type(main_artist) is not _Artist:
            raise ArtistException('{} is not an Artist object'.format(main_artist))
        self.main_artist = main_artist
        for artist in additional_artists:
            if type(artist) is not Additional_Artist:
                raise AdditionalArtistException('{} is not an Additional_Artist'.format(artist))
        self.additional_artists = additional_artists
        self.mix = mix

    def __str__(self) -> str:
        string = '{}\n'.format(self.title)
        if self.main_artist is not None:
            string += '{}\n'.format(self.main_artist)
        if self.additional_artists != []:
            for additional_artist in self.additional_artists:
                string += '{}'.format(additional_artist)
            string += '\n'
        if self.mix is not None:
            string += '({})\n'.format(self.mix)
        return string


class TrackList():
    """ A list of songs (tracklist) on one side of an album"""

    @property
    def side(self) -> Optional[str]:
        return self.side

    @property
    def side_mixer(self) -> Optional[str]:
        return self.side_mixer

    @ property
    def song_list(self) -> List[Song]:
        return self._song_list

    def __init__(self, side: Optional[str] = None, side_mixer: Optional[_Artist] = None) -> None:
        """ Create a tracklist for an album.

            :param side:   The name of the tracklist (eg. "Side A")
            :type side:    str | None

            :param side_mixer:  And optional mixer of the songs on this tracklist
            :type side_mixer:   :class:`_Artist`

            :raises ArtistException:  If side_mixer is not a :class:`Artist`
        """
        self._side = side
        if side_mixer is not None and type(side_mixer) is not _Artist:
            raise ArtistException('{} is not an Artist object'.format(side_mixer))
        self._side_mixer = side_mixer
        self._song_list = []

    def add_song(self, song: Song) -> None:
        """ Append a song to the end of the song list. Thus an ordered list.

            :param song:  The song to add to the end of the tracklist
            :type song:   :class:`Song`

            :raises SongException:  If you are not adding a :class:`Song`
        """
        if type(song) is Song:
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

    def __str__(self) -> str:
        if self._side is not None:
            string = '{}'.format(self._side)
        else:
            string = ''
        if self._side_mixer is not None:
            string += 'mixed by {}'.format(self._side_mixer)
        string += '\n'
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
    def date(self) -> int:
        return self._date

    @property
    def mixer(self) -> Optional[_Artist]:
        return self._mixer

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
        return md5(bytes(title + artist_name, 'utf-8')).hexdigest()

    def __init__(self, title: str, artist: _Artist, date: int, mixer: Optional[_Artist]) -> None:
        self._title = title
        if type(artist) is not _Artist:
            raise ArtistException('{} is not an Artist object'.format(artist))
        self._artist = artist
        if type(date) is not int:
            raise TypeError('Date must be an int value')
        self._date = date
        if mixer is not None and type(mixer) is not _Artist:
            raise ArtistException('{} is not an Artist object'.format(mixer))
        self._mixer = mixer
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

    def __str__(self) -> str:
        string = '{}\n{}\n'.format(self.title, self.artist)
        if self.mixer is not None:
            string += 'Mixed by {}\n'.format(self.mixer)
        string += '{}'.format(self.date)
        for track in self.tracks:
            string += str(track)
        string += '\n'
        return string


class LPs():
    """ A singleton set of all music albums. """
    _instance = None
    _lps = set()

    @property
    def lps(self) -> Set[_LP]:
        return self._lps

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LPs, cls).__new__(cls)
        return cls._instance

    def _clean_lps(self):
        """ Private method to remove all albums from the collection. Useful in testing. """
        self._lps = set()

    def create_LP(self, title: str, artist: _Artist, date: int, mixer: Optional[_Artist] = None, skip_adding_to_lp_list: bool = False) -> _LP:
        """ Return the named album if it exists or create a new album.

            By default a new album is added to the set of all albums.

            :param title:                    The title of the new album
            :type name:                      str

            :param artist:                   The album artist
            :type artist:                    :class:`_Artist`

            :param date:                     The year the album was published
            :type date:                      int

            :param artist:                   Optional album mixer
            :type artist:                    :class:`_Artist`

            :param skip_addiing_to_lp_list:  If true, do not add new album to albums set
            :type skip_adding_to_lp_list:    bool

            :returns:                        The located or newly created album
            :rtype:                          :class:`_LP`
        """
        # We need to perform this check before searching for an existing album as we need a valid
        # artist name to search
        if type(artist) is not _Artist:
            raise ArtistException('{} is not an artist'.format(artist))

        results = self.find_lp_by_title(title)
        if len(results) > 0:
            # Need to check hash id
            new_album_id = _LP.to_hash(title, artist.name)
            for result in results:
                if result._id == new_album_id:
                    return result
        # Create the new album
        new_lp = _LP(title, artist, date, mixer)
        artist.add_lp(new_lp)
        if mixer is not None:
            mixer.add_lp(new_lp)
        if not skip_adding_to_lp_list:
            self.add_lp(new_lp)
        return new_lp

    def add_lp(self, lp: _LP) -> None:
        """ Add an album to the set of all albums.

            :param lp:            The album to add
            :type lp:             :class:`_LP`

            :raises LPException:  If not passed a :class:`_LP` or the lp already exists in the set
        """
        if type(lp) is not _LP:
            raise LPException('{} is not an LP object'.format(lp))
        if lp in self._lps:
            raise LPException('LP {} already exists'.format(lp))
        self._lps.add(lp)

    def delete_lp(self, lp: _LP) -> None:
        """ Remove the album from the set of all albums.

            Also remove the album from the set of all albums owned by
            the album artist and album mixer (if they exist)

            :param lp:  The album to add
            :type lp:   :class:`_LP`
        """
        if lp in self.lps:
            lp.artist.delete_lp(lp)
            if lp.mixer is not None:
                lp.mixer.delete_lp(lp)
            self._lps.remove(lp)

    def lp_exists(self, lp: _LP) -> bool:
        """ Returns true of the album exists in the set of albums.

            :param lp:  The album to add
            :type lp:   :class:`_LP`

            :returns:   True if the album exists in the set of all albums
            :rtype:     bool
        """
        return lp in self.lps

    def find_lp_by_title(self, title: str) -> List[_LP]:
        """ Returns the albums in the set of all albums that matches the passed album title. Otherwise, empty list.

            :param title:  The album title to search for
            :type title:   str

            :returns:      The album if found. None, otherwise
            :rtype:        list(:class:`_LP` )
         """
        # TODO: Return a list since titles might be repeated
        result = []
        for lp in self.lps:
            if lp.title == title:
                result.append(lp)
        return result

    def __str__(self) -> str:
        string = ''
        for lp in self.lps:
            string += str(lp)
        return string