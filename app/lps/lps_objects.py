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

from typing import Optional


class LPException(Exception):
    pass


class ArtistException(Exception):
    pass


class SongException(Exception):
    pass


class TrackListException(Exception):
    pass


class _Artist():

    @property
    def lps(self) -> set:
        return self._lps

    @property
    def name(self) -> str:
        return self._name

    def __init__(self, name) -> None:
        self._name = name
        self._lps = set()

    def add_lp(self, lp) -> None:
        if type(lp) is not _LP:
            raise LPException('{} is not an LP object'.format(lp))
        if lp in self._lps:
            raise LPException('{} already in list of LPs for {}'.format(lp.name, self.name))
        else:
            self._lps.add(lp)

    def delete_lp(self, lp) -> None:
        if lp not in self._lps:
            raise LPException('{} not in list of LPs for {}'.format(lp.title, self.name))
        else:
            self._lps.remove(lp)

    def update_name(self, new_name) -> None:
        self._name = new_name

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name


class Artists():
    _instance = None
    _artists = set()

    @property
    def artists(self) -> list:
        return self._artists

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Artists, cls).__new__(cls)
        return cls._instance

    def _clean_artists(self):
        """ Private method to remove all artists from the collection. Useful in testing. """
        self._artists = set()

    def create_Artist(self, name, skip_adding_to_artists_list=False) -> _Artist:
        if name is None:
            raise ArtistException('An artist must have a name')
        result = self.find_artist(name)
        if result is not None:
            return result
        new_artist = _Artist(name)
        if not skip_adding_to_artists_list:
            self.add_artist(new_artist)
        return new_artist

    def add_artist(self, artist) -> None:
        if type(artist) is not _Artist:
            raise ArtistException('{} is not an Artist object'.format(artist))
        if artist in self.artists or self.find_artist(artist.name) is not None:
            raise ArtistException('Artist {} already exists'.format(artist))
        self._artists.add(artist)

    def delete_artist(self, artist) -> None:
        if artist not in self.artists:
            raise ArtistException('Artist {} does not exist'.format(artist))
        else:
            self._artists.remove(artist)

    def artist_exists(self, artist) -> bool:
        return artist in self.artists

    def find_artist(self, artist_name) -> Optional[_Artist]:
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

    def __init__(self, artist, prequel=None, sequel=None) -> None:
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

    def __init__(self, title, main_artist=None, additional_artists=[], mix=None) -> None:
        self.title = title
        if main_artist is not None and type(main_artist) is not _Artist:
            raise ArtistException('{} is not an Artist object'.format(main_artist))
        self.main_artist = main_artist

        # TODO: ensure a the passed list contains only additional_artists elements
        self.additional_artists = additional_artists
        self.mix = mix

        # TODO: Add artists to artist list if the do not already exist

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

    @property
    def side(self) -> Optional[str]:
        return self.side

    @property
    def side_mixer(self) -> Optional[str]:
        return self.side_mixer

    @ property
    def song_list(self) -> list:
        return self._song_list

    def __init__(self, side=None, side_mixer=None) -> None:
        self._side = side
        if side_mixer is not None and type(side_mixer) is not _Artist:
            raise ArtistException('{} is not an Artist object'.format(side_mixer))
        self._side_mixer = side_mixer
        self._song_list = []

    def add_song(self, song) -> None:
        """ Songs are appended to the end of the song list and thus an ordered list """
        if type(song) is Song:
            self._song_list.append(song)
        else:
            raise SongException('{} is not a song'.format(song))

    def remove_song(self, song) -> None:
        if song in self.song_list:
            self._song_list.remove(song)

    def has_song(self, song) -> bool:
        return song in self.song_list

    def get_song_from_title(self, song_title) -> Optional[Song]:
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
    def tracks(self) -> list:
        return self._tracks

    def __init__(self, title, artist, date, mixer) -> None:
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

        # Tracks must be set at this level or a reference will exist in the
        # singleton and keep being appended to through "add_track()". Ensure
        # starts empty with and instance level variable which can only be
        # updated through an instance level call to "add_track[]".
        self._tracks = []

    def add_track(self, track) -> None:
        if type(track) is TrackList:
            self._tracks.append(track)
        else:
            raise TrackListException('{} is not a track list'.format(track))

    def has_song(self, song) -> bool:
        for track in self._tracks:
            if track.has_song(song):
                return True
        return False

    def get_song_from_title(self, song_title) -> Optional[Song]:
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
    _instance = None
    _lps = list()

    @property
    def lps(self) -> list:
        return self._lps

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LPs, cls).__new__(cls)
        return cls._instance

    def _clean_lps(self):
        """ Private method to remove all albums from the collection. Useful in testing. """
        self._lps = list()

    def create_LP(self, title, artist, date, mixer=None, skip_adding_to_lp_list=False) -> _LP:
        result = self.find_lp_by_title(title)
        if result is not None:
            return result
        new_lp = _LP(title, artist, date, mixer)
        artist.add_lp(new_lp)
        if mixer is not None:
            mixer.add_lp(new_lp)
        if not skip_adding_to_lp_list:
            self.add_lp(new_lp)
        return new_lp

    def add_lp(self, lp) -> None:
        if type(lp) is not _LP:
            raise LPException('{} is not an LP object'.format(lp))
        if lp in self._lps:
            raise LPException('LP {} already exists'.format(lp))
        self._lps.append(lp)

    def delete_lp(self, lp) -> None:
        if lp in self.lps:
            lp.artist.delete_lp(lp)
            if lp.mixer is not None:
                lp.mixer.delete_lp(lp)
            self._lps.remove(lp)

    def lp_exists(self, lp) -> bool:
        return lp in self.lps

    def find_lp_by_title(self, title) -> Optional[_LP]:
        for lp in self.lps:
            if lp.title == title:
                return lp

    def __str__(self) -> str:
        string = ''
        for lp in self.lps:
            string += str(lp)
        return string