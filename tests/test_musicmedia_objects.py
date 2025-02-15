import os
import unittest

import pytest

from app.musicmedia.musicmedia_objects import (
    AdditionalArtist,
    ArtistException,
    Artists,
    CASSETTEs,
    CDs,
    ELPs,
    LPs,
    LPException,
    MEDIA,
    MediaType,
    MINI_CDs,
    Song,
    SongException,
    TrackList,
    TrackListException
)


class MEDIATestCase(unittest.TestCase):
    """
    The LP specific tests cases are the most inclusive as all media types share the similar class functions.
    (ie. barring a typo, the should pass as well)
    """

    DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')
    MUSIC_HTML_FILE = os.path.join(DATA_DIR, 'test_music.html')
    SORTED_MUSIC_HTML_FILE = os.path.join(DATA_DIR, 'sorted_test_music.html')  # Inorder by music type

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
        artist_3 = Artists().create_Artist('Joe Cocker', skip_adding_to_artists_set=True)
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
        additional_artist = AdditionalArtist(artist, prequel=' and ')
        self.assertEqual(' and Disco D', str(additional_artist))
        additional_artist = AdditionalArtist(artist, sequel=' (mixer)')
        self.assertEqual('Disco D (mixer)', str(additional_artist))
        additional_artist = AdditionalArtist(artist, prequel=' vs ', sequel=' (mixer)')
        self.assertEqual(' vs Disco D (mixer)', str(additional_artist))

        # Test can only add valid artists
        with pytest.raises(ArtistException):
            _ = AdditionalArtist('Hello')

    def test_song(self):
        song = Song('Wait A Minute')
        self.assertEqual('Wait A Minute\n', str(song))
        artist = Artists().create_Artist('DJ Nasty')
        song = Song('Wait A Minute', main_artist=artist)
        self.assertEqual('Wait A Minute\nDJ Nasty\n', str(song))
        song = Song('Wait A Minute', main_artist=artist, mix='Red Box remix')
        self.assertEqual('Wait A Minute\nDJ Nasty\n(Red Box remix)\n', str(song))
        additional_artist_1 = AdditionalArtist(Artists().create_Artist('DJ Nasty'))
        additional_artist_2 = AdditionalArtist(Artists().create_Artist('Disco D'), prequel=' vs ', sequel=' (mixer)')
        song = Song('Wait A Minute', additional_artists=[additional_artist_1, additional_artist_2], mix='Red Box remix')
        self.assertEqual('Wait A Minute\nDJ Nasty vs Disco D (mixer)\n(Red Box remix)\n', str(song))

    def test_tracklist(self):
        song_1 = Song('Jump To The Beat', Artists().create_Artist('Dannii Minogue'), mix='12" Mix')
        song_2 = Song('Jump!', Artists().create_Artist('The Movement'), mix='Everybody Mix')
        song_3 = Song('Pull Our Love Together', Artists().create_Artist('Pandella'), mix='Komix Club Mix')
        track = TrackList(side_name='Side 1')

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
        track = TrackList(side_name='Side 1')
        track.add_song(song_1)
        track.add_song(song_2)
        track.add_song(song_3)

        album_artist = Artists().create_Artist('Various Artists')
        album_mixer = Artists().create_Artist('DJ Funk')
        album = LPs().create(MediaType.LP, 'Club Cutz Volume 3', artists=[album_artist], year=1992, mixer=album_mixer)
        album.add_track(track=track)

        # Test properties creation
        self.assertEqual('Club Cutz Volume 3', album.title)
        self.assertEqual([album_artist], album.artists)
        self.assertEqual(1992, album.year)
        self.assertEqual(album_mixer, album.mixer)

        # Test song searching
        self.assertTrue(album.has_song(song_2), song_2)
        self.assertFalse(album.has_song(song_4))
        self.assertEqual(album.get_song_from_title('Pull Our Love Together'), song_3)
        self.assertIsNone(album.get_song_from_title('Jump'))

        # Test error conditions
        with pytest.raises(TypeError):
            album = LPs().create(MediaType.LP, 'Club Cutz Volume 9', [album_artist], '1992')
        with pytest.raises(ArtistException):
            album = LPs().create(MediaType.LP, 'Club Cutz Volume 9', 'DC Magnet', 1992)
        with pytest.raises(ArtistException):
            album = LPs().create(MediaType.LP, 'Club Cutz Volume 9', ['DC Magnet'], 1992)
        with pytest.raises(TrackListException):
            album.add_track('Hello')
        with pytest.raises(ArtistException):
            album = LPs().create(MediaType.LP, 'Club Cutz Volume 9', artists=[album_artist], year=1992, mixer='Hello')

        # Test string output
        expected_string = 'lp\n'
        expected_string += 'Club Cutz Volume 3\n'
        expected_string += 'Various Artists\n'
        expected_string += 'Mixed by DJ Funk\n'
        expected_string += '1992\n'
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

        self.assertEqual([], all_lps.find_by_title('Club Cutz Volume 3'))
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

        album_1 = LPs().create(MediaType.LP, 'Club Cutz Volume 3', artists=[artist_1], year=1992)
        album_1.add_track(track=track_1)

        song_4 = Song('He\'s All I Want', artist_5, mix='Cappery Mix')
        song_5 = Song('Push Upstaires', artist_6, mix='Roger\'s Blue Plastic People Mix')
        song_6 = Song('Freakin\' You', artist_7, mix='Caribbean Sunshine Remix By The Buffalo Bunch')
        track_2 = TrackList()
        track_2.add_song(song_4)
        track_2.add_song(song_5)
        track_2.add_song(song_6)
        album_2_artist = Artists().create_Artist('Various Artists')
        album_2 = LPs().create(media_type=MediaType.LP, title='Various: 01 Dance Music: Modernlife', artists=[album_2_artist], year=2000)
        album_2.add_track(track_2)

        # Test Singleton
        all_lps_2 = LPs()
        self.assertEqual(all_lps, all_lps_2)

        # Test existence
        self.assertTrue(all_lps.exists(album_2))
        missing_album = LPs().create(media_type=MediaType.LP,
                                     title='Missing Gold',
                                     artists=[Artists().create_Artist('The Gold Diggers', skip_adding_to_artists_set=True)],
                                     year=1920,
                                     skip_adding_to_lp_list=True)
        self.assertFalse(all_lps.exists(missing_album))

        # Test we can only add valid albums
        with pytest.raises(LPException):
            all_lps.add('Hello')

        # Test adding an album
        all_lps.add(missing_album)
        self.assertTrue(all_lps.exists(missing_album))

        # Test deleting an album
        all_lps.delete(missing_album)
        self.assertFalse(all_lps.exists(missing_album))

        # Test finding an album by title
        self.assertEqual([], all_lps.find_by_title('Missing Gold'))
        search_results = all_lps.find_by_title('Club Cutz Volume 3')
        self.assertEqual(1, len(search_results))
        self.assertEqual(album_1, search_results[0])

        # Test string output. Since the albums are in a set, the output
        # can come in one of two permutations
        album_string_1 = 'lp\n'
        album_string_1 += 'Club Cutz Volume 3\n'
        album_string_1 += 'Various Artists\n'
        album_string_1 += '1992\n'
        album_string_1 += ' 1. Jump To The Beat\nDannii Minogue\n(12" Mix)\n'
        album_string_1 += ' 2. Jump!\nThe Movement\n(Everybody Mix)\n'
        album_string_1 += ' 3. Pull Our Love Together\nPandella\n(Komix Club Mix)\n\n'
        album_string_2 = 'lp\n'
        album_string_2 += 'Various: 01 Dance Music: Modernlife\n'
        album_string_2 += 'Various Artists\n'
        album_string_2 += '2000\n'
        album_string_2 += ' 1. He\'s All I Want\nAngelmoon\n(Cappery Mix)\n'
        album_string_2 += ' 2. Push Upstaires\nUnderworld\n(Roger\'s Blue Plastic People Mix)\n'
        album_string_2 += ' 3. Freakin\' You\nJungle Brothers\n(Caribbean Sunshine Remix By The Buffalo Bunch)\n\n'
        album_perm_1 = album_string_1 + album_string_2
        album_perm_2 = album_string_2 + album_string_1
        all_lps_string = str(all_lps)
        print(f'{all_lps_string=}')
        self.assertTrue((album_perm_1 == all_lps_string) or (album_perm_2 == all_lps_string))

        # Test that we correctly create a new album when the title matches an
        # existing album
        new_album = LPs().create(media_type=MediaType.LP, title='Club Cutz Volume 3', artists=[artist_2], year=1992)
        self.assertNotEqual(album_1, new_album)
        search_results = all_lps.find_by_title('Club Cutz Volume 3')
        self.assertEqual(2, len(search_results))

        # Now we have some artist data collected as collateral to creating albums, test that
        self.assertEqual(7, len(artists.artists))
        self.assertTrue(artist_6, artists.artist_exists(artist_6))
        self.assertEqual(1, len(artist_2.lps))  # Club Cutz Volume 3 created directly above
        self.assertEqual(2, len(artist_1.lps))
        self.assertIsNotNone(artists.find_artist('The Movement'))
        self.assertEqual(artist_2, artists.find_artist('Dannii Minogue'))

    def test_read_lps_html(self):
        # Test the reading of a music html file to extract all the LPs
        all_artists = Artists()
        all_artists._clean_artists()
        all_lps = LPs()
        all_lps._clean_lps()
        MEDIA.from_html_file(self.MUSIC_HTML_FILE)
        print('Number of artists found: {}'.format(len(all_artists.artists)))
        print('Number of lps found: {}'.format(len(all_lps.lps)))

        puppini_sisters = all_artists.find_artist('The Puppini Sisters')
        puppini_sisters_albums = puppini_sisters.lps
        self.assertEqual(1, len(puppini_sisters_albums))
        puppini_sisters_christmas_album = puppini_sisters.find_lp('Christmas')
        self.assertIsNotNone(puppini_sisters_christmas_album)

        buble = all_artists.find_artist('Michael Buble')
        buble_albums = buble.lps
        self.assertEqual(1, len(buble_albums))
        buble_christmas_album = buble.find_lp('Christmas')
        self.assertIsNotNone(buble_christmas_album)

        self.assertEqual(puppini_sisters_christmas_album, buble_christmas_album)
        self.assertEqual(len(buble_christmas_album.tracks), 2)
        track1 = buble_christmas_album.tracks[0]
        self.assertEqual(track1.name, 'Side A')
        track1_song_list = track1.song_list
        self.assertEqual(len(track1_song_list), 8)
        jingle_bells_song = track1.get_song_from_title('Jingle Bells')
        self.assertEqual(jingle_bells_song.title, 'Jingle Bells')
        self.assertEqual(buble, jingle_bells_song.main_artist)
        self.assertEqual(puppini_sisters, jingle_bells_song.additional_artists[0].artist)

        williams = all_artists.find_artist('John Williams')
        self.assertEqual(len(williams.lps), 1)
        track1 = williams.find_lp('Greatest Hits').tracks[0]
        self.assertEqual(track1.name, 'Side 1')
        bach_song_composer = track1.get_song_from_title('Gavotte From Fourth Lute Suite')
        self.assertEqual(bach_song_composer, track1.song_list[1])
        bach = all_artists.find_artist('Bach')
        self.assertEqual(len(bach.cds | bach.lps | bach.elps | bach.mini_cds), 3)
        self.assertEqual(bach, bach_song_composer.classical_composers[0])
        adagio_song = williams.find_lp('Greatest Hits').get_song_from_title('Adagio From Concierto de Aranjuez For Guitar And Orchestra')
        self.assertEqual('Rodrigo', adagio_song.classical_composers[0].name)
        adagio_song_additional_artists = set(['Eugene Ormandy', 'Members of the Philadelphia Orchestra'])
        additional_artists = set([additional_artist.artist.name for additional_artist in adagio_song.additional_artists])
        self.assertEqual(adagio_song_additional_artists, additional_artists)

        whos_zoo = all_lps.find_by_title('Who\'s Zoo')[0]
        self.assertEqual(len(whos_zoo.tracks), 4)
        im_the_face_song = whos_zoo.get_song_from_title('I\'m The Face')
        self.assertEqual(im_the_face_song.year, 1964)
        self.assertEqual(im_the_face_song.additional_artists[0].artist.name, 'The High Numbers')

        not_fragile = all_lps.find_by_title('Not Fragile')[0]
        moontan = all_lps.find_by_title('Moontan')[0]
        know_your_jazz = all_lps.find_by_title('Know Your Jazz')[0]

        self.assertListEqual(all_lps.find_by_year(1974), [whos_zoo, moontan, know_your_jazz, not_fragile])

    def test_read_cds_html(self):
        # Test the reading of a music html file to extract all the CDs
        all_artists = Artists()
        all_artists._clean_artists()
        all_cds = CDs()
        all_cds._clean_cds()
        MEDIA.from_html_file(self.MUSIC_HTML_FILE)
        print('Number of artists found: {}'.format(len(all_artists.artists)))
        print('Number of cds found: {}'.format(len(all_cds.cds)))

        self.assertEqual(8, len(all_cds.cds))

        jungle_brothers = all_artists.find_artist('Jungle Brothers')
        jungle_brothers_cds = jungle_brothers.cds
        self.assertEqual(1, len(jungle_brothers_cds))
        jungle_brothers_various_cd = jungle_brothers.find_cd('Various: 02 Dance Music: Modernlife')
        self.assertIsNotNone(jungle_brothers_various_cd)

        dj_geoffe = all_artists.find_artist('DJ Geoffe')
        dj_geoff_cds = dj_geoffe.cds
        self.assertEqual(1, len(dj_geoff_cds))
        dj_geoffe_mixed_cd = dj_geoffe.find_cd('Various: 02 Dance Music: Modernlife')
        self.assertIsNotNone(dj_geoffe_mixed_cd)

        self.assertEqual(jungle_brothers_various_cd, dj_geoffe_mixed_cd)
        self.assertEqual(len(dj_geoffe_mixed_cd.tracks), 1)
        track1 = dj_geoffe_mixed_cd.tracks[0]
        track1_song_list = track1.song_list
        self.assertEqual(len(track1_song_list), 10)

        freakin_you = track1.get_song_from_title('Freakin\' You')
        self.assertEqual(freakin_you.title, 'Freakin\' You')
        self.assertEqual(jungle_brothers, freakin_you.main_artist)

    def test_read_elps_html(self):
        # Test the reading of a music html file to extract all the ELPs
        all_artists = Artists()
        all_artists._clean_artists()
        all_elps = ELPs()
        all_elps._clean_elps()
        MEDIA.from_html_file(self.MUSIC_HTML_FILE)
        print('Number of artists found: {}'.format(len(all_artists.artists)))
        print('Number of ELPs found: {}'.format(len(all_elps.elps)))

        self.assertEqual(1, len(all_elps.elps))

        bryan_adams = all_artists.find_artist('Bryan Adams')
        bryan_adams_elps = bryan_adams.elps
        self.assertEqual(1, len(bryan_adams_elps))
        bryan_adams_elp = bryan_adams.find_elp('Run To You')
        self.assertIsNotNone(bryan_adams_elp)

        self.assertEqual(len(bryan_adams_elp.tracks), 2)
        track1 = bryan_adams_elp.tracks[0]
        track2 = bryan_adams_elp.tracks[1]

        self.assertEqual(len(track1.song_list), 1)
        self.assertEqual(len(track2.song_list), 2)

        cuts_like_a_knife = track2.get_song_from_title('Cuts Like A Knife')
        self.assertEqual(cuts_like_a_knife.title, 'Cuts Like A Knife')
        self.assertEqual(bryan_adams, cuts_like_a_knife.main_artist)

    def test_read_mini_cd_html(self):
        # Test the reading of a music html file to extract all the mini CDs
        all_artists = Artists()
        all_artists._clean_artists()
        all_mini_cds = MINI_CDs()
        all_mini_cds._clean_mini_cds()
        MEDIA.from_html_file(self.MUSIC_HTML_FILE)
        print('Number of artists found: {}'.format(len(all_artists.artists)))
        print('Number of mini CDs found: {}'.format(len(all_mini_cds.mini_cds)))

        self.assertEqual(1, len(all_mini_cds.mini_cds))

        guns_n_roses = all_artists.find_artist('Guns N\' Roses')
        guns_n_roses_mini_cds = guns_n_roses.mini_cds
        self.assertEqual(1, len(guns_n_roses_mini_cds))
        guns_n_roses_mini_cd = guns_n_roses.find_mini_cd('Since I Don\'t Have You')
        self.assertIsNotNone(guns_n_roses_mini_cd)

        self.assertEqual(len(guns_n_roses_mini_cd.tracks), 1)
        track1 = guns_n_roses_mini_cd.tracks[0]

        self.assertEqual(len(track1.song_list), 3)

        human_being = track1.get_song_from_title('Human Being')
        self.assertEqual(human_being.title, 'Human Being')
        self.assertEqual(guns_n_roses, human_being.main_artist)
        self.assertEqual(human_being.mix, 'LP version')

    def test_html_export(self):
        # Test the html created by all lps is the same as the html contained
        # in the file read in
        all_artists = Artists()
        all_artists._clean_artists()
        all_cassettes = CASSETTEs()
        all_cassettes._clean_cassettes()
        all_cds = CDs()
        all_cds._clean_cds()
        all_lps = LPs()
        all_lps._clean_lps()
        all_elps = ELPs()
        all_elps._clean_elps()
        all_mini_cds = MINI_CDs()
        all_mini_cds._clean_mini_cds()
        media = MEDIA()
        media.from_html_file(self.MUSIC_HTML_FILE)
        print('Number of Artists found: {}'.format(len(all_artists.artists)))
        print('Number of Cassettes found: {}'.format(len(all_cassettes.cassettes)))
        print('Number of CDs found: {}'.format(len(all_cds.cds)))
        print('Number of LPs found: {}'.format(len(all_lps.lps)))
        print('Number of ELPs found: {}'.format(len(all_elps.elps)))
        print('Number of mini CDs found: {}'.format(len(all_mini_cds.mini_cds)))

        with open(self.SORTED_MUSIC_HTML_FILE, 'r') as fp:
            file_html = fp.read()
        html_representation = media.to_html()

        # Used to track down error locations
        debug = os.getenv('TEST_MEDIA_HTML_EXPORT_DEBUG', 'False')
        if debug.lower() == 'true':
            file_html_list = file_html.split('\n')
            html_representation_list = html_representation.split('\n')
            for i in range(len(html_representation_list)):
                if html_representation_list[i] != file_html_list[i]:
                    print(html_representation_list[i - 3:i + 3])
                    print(file_html_list[i - 3:i + 3])
                    print(":".join("{:02x}".format(ord(c)) for c in html_representation_list[i]))
                    print(":".join("{:02x}".format(ord(c)) for c in file_html_list[i]))
                    print("Line #{}".format(i))
                    break
            self.assertEqual(len(file_html_list), len(html_representation_list))

        self.maxDiff = None
        self.assertEqual(file_html, html_representation)

        # assert (False)  # nosec