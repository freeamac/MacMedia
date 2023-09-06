import unittest

import pytest

from app.lps.lps_objects import (
    Additional_Artist,
    ArtistException,
    Artists,
    LPs,
    LPException,
    Song,
    SongException,
    TrackList,
    TrackListException
)


class LPTestCase(unittest.TestCase):

    def test_Artist(self):

        artist = Artists().create_Artist('VArious Artists')
        self.assertEqual('VArious Artists', artist.name)
        self.assertEqual(artist.lps, set())
        artist.update_name('Various Artists')
        self.assertNotEqual('VArious Artists', artist.name)
        self.assertEqual('Various Artists', artist.name)
        self.assertEqual(artist.lps, set())
        self.assertEqual('Various Artists', str(artist))

    def test_Artists(self):
        artist_1 = Artists().create_Artist('VArious Artists')
        artist_2 = Artists().create_Artist('Disco D')
        artist_3 = Artists().create_Artist('Joe Cocker', skip_adding_to_artists_list=True)
        artists_1 = Artists()
        artists_2 = Artists()

        # Test singleton
        self.assertIs(artists_1, artists_2)

        # Test existence of artists
        self.assertTrue(artists_1.artist_exists(artist_1))
        self.assertTrue(artists_2.artist_exists(artist_1))
        self.assertTrue(artists_2.artist_exists(artist_2))
        self.assertFalse(artists_1.artist_exists(artist_3))

        # Test we can only add valid artists
        with pytest.raises(ArtistException):
            artists_1.add_artist('Hello')

        # Change artist name and find it
        artist_1.update_name('Various Artists')
        self.assertTrue(artists_1.artist_exists(artist_1))

        # Test removing an artist
        artists_1.add_artist(artist_3)
        self.assertTrue(artists_1.artist_exists(artist_3))
        artists_1.delete_artist(artist_3)
        self.assertFalse(artists_1.artist_exists(artist_3))

        # Test finding artists by name
        self.assertTrue(artists_1.find_artist('Disco D'))
        self.assertTrue(artists_1.find_artist('Various Artists'))
        self.assertFalse(artists_1.find_artist('VArious Artists'))

        # Check string representation. Need to split into list as
        # set order is mutable over tests.
        self.assertSetEqual(set(['Disco D', 'Various Artists', '  Albums', '  ------', '']), set(str(artists_2).split('\n')))

    def test_additional_artist(self):
        artist = Artists().create_Artist('Disco D')
        additional_artist = Additional_Artist(artist, prequel=' and ')
        self.assertEqual(' and Disco D', str(additional_artist))
        additional_artist = Additional_Artist(artist, sequel=' (mixer)')
        self.assertEqual('Disco D (mixer)', str(additional_artist))
        additional_artist = Additional_Artist(artist, prequel=' vs ', sequel=' (mixer)')
        self.assertEqual(' vs Disco D (mixer)', str(additional_artist))

        # Test can only add valid artists
        with pytest.raises(ArtistException):
            additional_artist = Additional_Artist('Hello')

    def test_song(self):
        song = Song('Wait A Minute')
        self.assertEqual('Wait A Minute\n', str(song))
        artist = Artists().create_Artist('DJ Nasty')
        song = Song('Wait A Minute', main_artist=artist)
        self.assertEqual('Wait A Minute\nDJ Nasty\n', str(song))
        song = Song('Wait A Minute', main_artist=artist, mix='Red Box remix')
        self.assertEqual('Wait A Minute\nDJ Nasty\n(Red Box remix)\n', str(song))
        additional_artist_1 = Additional_Artist(Artists().create_Artist('DJ Nasty'))
        additional_artist_2 = Additional_Artist(Artists().create_Artist('Disco D'), prequel=' vs ', sequel=' (mixer)')
        song = Song('Wait A Minute', additional_artists=[additional_artist_1, additional_artist_2], mix='Red Box remix')
        self.assertEqual('Wait A Minute\nDJ Nasty vs Disco D (mixer)\n(Red Box remix)\n', str(song))

    def test_tracklist(self):
        song_1 = Song('Jump To The Beat', Artists().create_Artist('Dannii Minogue'), mix='12" Mix')
        song_2 = Song('Jump!', Artists().create_Artist('The Movement'), mix='Everybody Mix')
        song_3 = Song('Pull Our Love Together', Artists().create_Artist('Pandella'), mix='Komix Club Mix')
        track = TrackList(side='Side 1')

        # Test song addition
        track.add_song(song_1)
        track.add_song(song_2)
        self.assertTrue(track.has_song(song_1))
        self.assertFalse(track.has_song(song_3))

        # Test cannot add invalid song
        with pytest.raises(SongException):
            track.add_song('Hello')

        # Test song removal
        track.add_song(song_3)
        track.remove_song(song_1)
        track.remove_song(song_3)
        self.assertTrue(track.has_song(song_2))
        self.assertFalse(track.has_song(song_1))
        self.assertFalse(track.has_song(song_3))
        track.remove_song(song_2)
        self.assertFalse(track.has_song(song_2))

        # Test song title searching
        track.add_song(song_1)
        track.add_song(song_2)
        track.add_song(song_3)
        self.assertEqual(track.get_song_from_title('Jump!'), song_2)
        self.assertIsNone(track.get_song_from_title('Jump'))

        # Test string output
        expected_string = 'Side 1\n'
        expected_string += ' 1. Jump To The Beat\nDannii Minogue\n(12" Mix)\n'
        expected_string += ' 2. Jump!\nThe Movement\n(Everybody Mix)\n'
        expected_string += ' 3. Pull Our Love Together\nPandella\n(Komix Club Mix)\n'
        self.assertEqual(expected_string, str(track))

    def test_lp(self):
        song_1 = Song('Jump To The Beat', Artists().create_Artist('Dannii Minogue'), mix='12" Mix')
        song_2 = Song('Jump!', Artists().create_Artist('The Movement'), mix='Everybody Mix')
        song_3 = Song('Pull Our Love Together', Artists().create_Artist('Pandella'), mix='Komix Club Mix')
        song_4 = Song('Latino Mambo', Artists().create_Artist('Latin Side Od Soul'), mix='Dance Mix')
        track = TrackList(side='Side 1')
        track.add_song(song_1)
        track.add_song(song_2)
        track.add_song(song_3)

        album_artist = Artists().create_Artist('Various Artists')
        album_mixer = Artists().create_Artist('DJ Funk')
        album = LPs().create_LP('Club Cutz Volume 3', artist=album_artist, date=1992, mixer=album_mixer)
        album.add_track(track=track)

        # Test properties creation
        self.assertEqual('Club Cutz Volume 3', album.title)
        self.assertEqual(album_artist, album.artist)
        self.assertEqual(1992, album.date)
        self.assertEqual(album_mixer, album.mixer)

        # Test song searching
        self.assertTrue(album.has_song(song_2), song_2)
        self.assertFalse(album.has_song(song_4))
        self.assertEqual(album.get_song_from_title('Pull Our Love Together'), song_3)
        self.assertIsNone(album.get_song_from_title('Jump'))

        # Test error conditions
        with pytest.raises(TypeError):
            album = LPs().create_LP('Club Cutz Volume 9', album_artist, '1992')
        with pytest.raises(ArtistException):
            album = LPs().create_LP('Club Cutz Volume 9', 'DC Magnet', 1992)
        with pytest.raises(TrackListException):
            album.add_track('Hello')
        with pytest.raises(ArtistException):
            album = LPs().create_LP('Club Cutz Volume 9', artist=album_artist, date=1992, mixer='Hello')

        # Test string output
        expected_string = 'Club Cutz Volume 3\n'
        expected_string += 'Various Artists\n'
        expected_string += 'Mixed by DJ Funk\n'
        expected_string += '1992'
        expected_string += 'Side 1\n'
        expected_string += ' 1. Jump To The Beat\nDannii Minogue\n(12" Mix)\n'
        expected_string += ' 2. Jump!\nThe Movement\n(Everybody Mix)\n'
        expected_string += ' 3. Pull Our Love Together\nPandella\n(Komix Club Mix)\n\n'
        self.assertEqual(expected_string, str(album))

    def test_lps(self):

        # Clean any debris in the albums and artists list
        all_lps = LPs()
        all_lps._clean_lps()
        artists = Artists()
        artists._clean_artists()

        self.assertIsNone(all_lps.find_lp_by_title('Club Cutz Volume 3'))
        self.assertEqual(0, len(all_lps.lps))

        artist_1 = artists.create_Artist('Various Artists')
        artist_2 = artists.create_Artist('Dannii Minogue')
        artist_3 = artists.create_Artist('The Movement')
        artist_4 = artists.create_Artist('Pandella')
        artist_5 = artists.create_Artist('Angelmoon')
        artist_6 = artists.create_Artist('Underworld')
        artist_7 = artists.create_Artist('Jungle Brothers')

        song_1 = Song('Jump To The Beat', artist_2, mix='12" Mix')
        song_2 = Song('Jump!', artist_3, mix='Everybody Mix')
        song_3 = Song('Pull Our Love Together', artist_4, mix='Komix Club Mix')
        track_1 = TrackList()
        track_1.add_song(song_1)
        track_1.add_song(song_2)
        track_1.add_song(song_3)

        album_1 = LPs().create_LP('Club Cutz Volume 3', artist=artist_1, date=1992)
        album_1.add_track(track=track_1)

        song_4 = Song('He\'s All I Want', artist_5, mix='Cappery Mix')
        song_5 = Song('Push Upstaires', artist_6, mix='Roger\'s Blue Plastic People Mix')
        song_6 = Song('Freakin\' You', artist_7, mix='Caribbean Sunshine Remix By The Buffalo Bunch')
        track_2 = TrackList()
        track_2.add_song(song_4)
        track_2.add_song(song_5)
        track_2.add_song(song_6)
        album_2_artist = Artists().create_Artist('Various Artists')
        album_2 = LPs().create_LP('Various: 01 Dance Music: Modernlife', artist=album_2_artist, date=2000)
        album_2.add_track(track_2)

        # Test Singleton
        all_lps_2 = LPs()
        self.assertEqual(all_lps, all_lps_2)

        # Test existence
        self.assertTrue(all_lps.lp_exists(album_2))
        missing_album = LPs().create_LP('Missing Gold', artist=Artists().create_Artist('The Gold Diggers', skip_adding_to_artists_list=True), date=1920, skip_adding_to_lp_list=True)
        self.assertFalse(all_lps.lp_exists(missing_album))

        # Test we can only add valid albums
        with pytest.raises(LPException):
            all_lps.add_lp('Hello')

        # Test adding an album
        all_lps.add_lp(missing_album)
        self.assertTrue(all_lps.lp_exists(missing_album))

        # Test deleting an album
        all_lps.delete_lp(missing_album)
        self.assertFalse(all_lps.lp_exists(missing_album))

        # Test finding an album by title
        self.assertIsNone(all_lps.find_lp_by_title('Missing Gold'))
        self.assertEqual(album_1, all_lps.find_lp_by_title('Club Cutz Volume 3'))

        # Test string output
        expected_string = 'Club Cutz Volume 3\n'
        expected_string += 'Various Artists\n'
        expected_string += '1992\n'
        expected_string += ' 1. Jump To The Beat\nDannii Minogue\n(12" Mix)\n'
        expected_string += ' 2. Jump!\nThe Movement\n(Everybody Mix)\n'
        expected_string += ' 3. Pull Our Love Together\nPandella\n(Komix Club Mix)\n\n'
        expected_string += 'Various: 01 Dance Music: Modernlife\n'
        expected_string += 'Various Artists\n'
        expected_string += '2000\n'
        expected_string += ' 1. He\'s All I Want\nAngelmoon\n(Cappery Mix)\n'
        expected_string += ' 2. Push Upstaires\nUnderworld\n(Roger\'s Blue Plastic People Mix)\n'
        expected_string += ' 3. Freakin\' You\nJungle Brothers\n(Caribbean Sunshine Remix By The Buffalo Bunch)\n\n'
        self.assertEqual(expected_string, str(all_lps))

        # Now we have some artist data collected as collateral to creating albums, test that
        self.assertEqual(7, len(artists.artists))
        self.assertTrue(artist_6, artists.artist_exists(artist_6))
        self.assertEqual(0, len(artist_2.lps))
        self.assertEqual(2, len(artist_1.lps))
        self.assertIsNotNone(artists.find_artist('The Movement'))
        self.assertEqual(artist_2, artists.find_artist('Dannii Minogue'))