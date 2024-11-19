from http import HTTPStatus
import unittest
from unittest.mock import patch

from flask_login import FlaskLoginClient

from app.app import app as muscimedia_app
from app.app import db
from app.demo_helpers import load_demo_data
from app.models import User
from app.musicmedia.musicmedia_objects import Artists, LPs, MEDIA


class MusicMediaRoutesTestCase(unittest.TestCase):
    """ Test the Musicmedia routes (views).

        We only test the LP routes as they are similar(?). For all
        music media types.

        *Note* that exceptions cannot be tested. There seems to be no way
        to check if a message has been flashed on screen which occurs
        during error paths.

        *Note* that the test database is setup for login credentials.
    """

    testuser = 'testuser'
    testuser_password = 'testuser_password'  # nosec

    full_data_lp = {'title': 'Full Data LP',
                    'main_artist': 'Main Man',
                    'additional_artists-0-additional_artist': '',
                    'year': 1984,
                    'mixer': 'DJ',
                    'classical_composer_1': 'Bach',
                    'classical_composer_2': 'Bach Jr',
                    'finish': True}

    summary_data_track = {'track_name': 'Side A',
                          'track_mixer': 'DJ jr',
                          'track_songs-0-song_title': '',
                          'save': True}

    summary_data_first_track = {'track_name': 'Side A',
                                'add_track': True}

    summary_data_second_track = {'track_name': 'Side A',
                                 'save': True}

    full_data_track = {'track_name': 'Side A',
                       'track_mixer': 'DJ jr',
                       'track_songs-0-song_title': 'First Song',
                       'track_songs-0-song_mix': 'DJ version',
                       'track_songs-0-song_featured_in': 'Movies',
                       'track_songs-0-song_classical_composer_1': 'Amadeus',
                       'track_songs-0-song_classical_composer_2': 'Amadeus Jr',
                       'track_songs-0-song_classical_work': 'Night Moves',
                       'track_songs-0-song_country': 'USA',
                       'track_songs-0-song_year': 1980,
                       'track_songs-0-song_parts': 'Intro\nOutro',
                       'track_songs-0-song_additional_artists-0-additional_artist': '',
                       'save': True}

    full_data_track_2_songs = {'track_name': 'Side A',
                               'track_mixer': 'DJ jr',
                               'track_songs-0-song_title': 'First Song',
                               'track_songs-0-song_mix': 'DJ version',
                               'track_songs-0-song_featured_in': 'Movies',
                               'track_songs-0-song_classical_composer_1': 'Amadeus',
                               'track_songs-0-song_classical_composer_2': 'Amadeus Jr',
                               'track_songs-0-song_classical_work': 'Night Moves',
                               'track_songs-0-song_country': 'USA',
                               'track_songs-0-song_year': 1980,
                               'track_songs-0-song_parts': 'Intro\nOutro',
                               'track_songs-0-song_additional_artists-0-additional_artist': '',
                               'track_songs-1-song_title': 'Second Song',
                               'save': True}

    lp_cancel_delete_data = {'cancel': True}

    lp_delete_data = {'submit': True}

    lp_cancel_modify_data = {'cancel': True}

    lp_modify_data = {'title': 'Full Data LP',
                      'main_artist': 'Main Man',
                      'additional_artists-0-additional_artist': '',
                      'year': 1984,
                      'mixer': 'DJ jr',
                      'classical_composer_1': 'Bach',
                      'classical_composer_2': 'Bach Jr',
                      'save': True}

    track_cancel_modify_data = {'cancel': True}

    lp_modify_data_go_to_track = {'title': 'Full Data LP',
                                  'main_artist': 'Main Man',
                                  'additional_artists-0-additional_artist': '',
                                  'year': 1984,
                                  'mixer': 'DJ jr',
                                  'classical_composer_1': '',
                                  'classical_composer_2': '',
                                  'save_and_modify_tracks': True}

    track_modify_data = {'track_name': 'First Side',
                         'modify_next_track': True}

    new_track_data = {'track_name': 'Side B',
                      'save': True}

    modify_song_data = {'song_title': 'Uno Song',
                        'save_and_finish': True}

    delete_song_data = {'delete_song': True}

    def _db_reset(self):
        """ Drop all tables and re-create them """
        self.db.drop_all()
        self.db.create_all()

    def _populate_db(self):
        """ Populate a fresh database with test data """
        self._db_reset()
        self.db.session.commit()

        # Populate with test data
        load_demo_data(self.db)
        self.db.session.add(self.new_testuser)
        self.db.session.commit()

    def setUp(self):
        # Just need to get access to the database instance here
        # and push the context
        self.app = muscimedia_app
        self.app_context = self.app.test_request_context()
        self.app_context.push()
        self.db = db
        self.new_testuser = User(username=self.testuser, password=self.testuser_password)
        self._populate_db()
        self.testing = True
        self.app.test_client_class = FlaskLoginClient
        self.client = self.app.test_client(user=self.new_testuser)
        # Ensure no LPs and Artists exist
        all_lps = LPs()
        all_lps._clean_lps()
        self.assertEqual([], all_lps.lps)
        all_artists = Artists()
        all_artists._clean_artists()
        self.assertEqual(set(), all_artists.artists)

    def tearDown(self):
        self.db.drop_all()
        self.app_context.pop()

    def _check_add_lp_form(self, response):
        # Check have all the fields in a standard full DVD form
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(b'Add A New LP To The Music Media Library', response.data)
        self.assertIn(b'Title:', response.data)
        self.assertIn(b'Main Artist:', response.data)
        self.assertIn(b'Particle:', response.data)
        self.assertIn(b'Additional Artist:', response.data)
        self.assertIn(b'Mixer:', response.data)
        self.assertIn(b'Classical Comp. 1:', response.data)
        self.assertIn(b'Classical Comp. 2:', response.data)
        self.assertIn(b'Add Tracks', response.data)
        self.assertIn(b'Cancel', response.data)

    def _check_add_track_form(self, response):
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(b'Add Tracks To A LP', response.data)
        self.assertIn(b'Track Name', response.data)
        self.assertIn(b'Track Mixer', response.data)
        self.assertIn(b'Song #1', response.data)
        self.assertIn(b'Song Title', response.data)
        self.assertIn(b'Feat. In', response.data)
        self.assertIn(b'List Main Artist?', response.data)
        self.assertIn(b'Main Artist Sequel', response.data)
        self.assertIn(b'Classical Comp. 1', response.data)
        self.assertIn(b'Classical Comp. 2', response.data)
        self.assertIn(b'Classical Work', response.data)
        self.assertIn(b'Country', response.data)
        self.assertIn(b'Release Year', response.data)
        self.assertIn(b'Mix', response.data)
        self.assertIn(b'Song Parts', response.data)

    def _track_1_ids(self, response_request):
        """ Split initial track response request into the lp and track ids """
        # Determine the lp id and track id from the request url which looks like:
        #   <Request 'http://localhost/lps/add_track/0/0?media_type=MediaType.LP' [GET]>
        request_str = str(response_request)
        track_id = request_str.split()[1].split('?')[0].split('/')[-1]
        lp_id = request_str.split()[1].split('?')[0].split('/')[-2]
        return lp_id, track_id

    def _track_n_ids(self, response_request):
        """ Subsequent (> 1) track response requests into the lp and track ids """
        # Determine the lp id and track id from the request url which looks like:
        #   <Request 'http://localhost/lps/add_track/0/1' [GET]>
        request_str = str(response_request)
        track_id = request_str.split()[1].split("'")[1].split('/')[-1]
        lp_id = request_str.split()[1].split("'")[1].split('/')[-2]
        return lp_id, track_id

    def test_index(self):
        """ Check the main index page response """

        response = self.client.get('/lps/', follow_redirects=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        # Note we cannot check the contents as the is produced through an Ajax api call
        self.assertIn(b'Music Media Library LPs Main Page', response.data)
        self.assertIn(b'Add New LP To Music Media Library', response.data)

    def test_add_lp(self):
        """ Check we can add an LP to the list of LPs """

        response = self.client.get('/lps/add', follow_redirects=True)
        self._check_add_lp_form(response)

        # Check we can post a new LP
        response = self.client.post('/lps/add', follow_redirects=True, data=self.full_data_lp)

        # Should have added lp and redirected to "Add Tracks" page
        self._check_add_track_form(response)

        # Check we have the new LP in the list
        all_lps = LPs()
        self.assertEqual([self.full_data_lp['title']], [lp.title for lp in all_lps.find_by_title(self.full_data_lp['title'])])
        self.assertEqual([self.full_data_lp['year']], [lp.year for lp in all_lps.find_by_year(self.full_data_lp['year'])])
        the_lp = all_lps.find_by_title(self.full_data_lp['title'])[0]
        self.assertEqual(the_lp.mixer.name, self.full_data_lp['mixer'])
        classical_composers = set([classical_composer.name for classical_composer in the_lp.classical_composers])
        full_data_lp_classical_composers = set([self.full_data_lp['classical_composer_1'], self.full_data_lp['classical_composer_2']])
        self.assertEqual(classical_composers, full_data_lp_classical_composers)

        # Check that the Artist has been added
        all_artists = Artists()
        self.assertIn(self.full_data_lp['main_artist'], [artist.name for artist in all_artists.artists])

    def test_add_lp_cancel(self):
        """ Check cancelling while adding an LP functions correctly ("Cancel" button test) """

        response = self.client.get('/lps/add', follow_redirects=True)
        self._check_add_lp_form(response)

        # Check we can cancel posting a new LP and return to main page
        cancel_lp_data = self.full_data_lp.copy()
        del cancel_lp_data['finish']
        cancel_lp_data['cancel'] = True
        response = self.client.post('/lps/add', follow_redirects=True, data=cancel_lp_data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(b'Music Media Library LPs Main Page', response.data)
        self.assertIn(b'Add New LP To Music Media Library', response.data)

        # Should have no album or Artist data
        all_lps = LPs()
        self.assertEqual(0, all_lps.length)
        all_artists = Artists()
        self.assertEqual(0, len(all_artists.artists))

    def test_expand(self):
        """ Check we can expand and display the data of a newly added albun """

        # Post a new LP
        response = self.client.post('/lps/add', follow_redirects=True, data=self.full_data_lp)

        # Should have added lp and redirected to "Add Tracks" page
        self._check_add_track_form(response)

        # Get the expanded album data
        all_lps = LPs()
        the_lp = all_lps.find_by_title(self.full_data_lp['title'])[0]
        lp_id = the_lp.index
        expanded_lp_html = the_lp.to_html()
        response = self.client.get('lps/expand/{}'.format(lp_id))

        # Check response code and contents are correct
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(expanded_lp_html.encode(), response.data)

    def test_add_track(self):
        """ Check that we can add track information to a new LP """

        # Need to add a new LP to get to the add track page
        response = self.client.post('/lps/add', follow_redirects=True, data=self.full_data_lp)

        # Should have added lp and redirected to "Add Tracks" page
        self._check_add_track_form(response)

        # Determine the lp id and track id from the request url
        lp_id, track_id = self._track_1_ids(response.request)

        # Add track information
        response = self.client.post('lps/add_track/{}/{}?media_type=MediaType.LP'.format(lp_id, track_id), follow_redirects=True, data=self.summary_data_track)

        # Check we have been redirected to main LP page
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(b'Music Media Library LPs Main Page', response.data)
        self.assertIn(b'Add New LP To Music Media Library', response.data)

        # Ensure track information stored in library
        all_lps = LPs()
        lps = all_lps.find_by_title(self.full_data_lp['title'])
        self.assertEqual(1, len(lps))
        the_lp = lps[0]
        self.assertEqual(1, len(the_lp.tracks))
        the_track = the_lp.tracks[0]
        self.assertEqual(self.summary_data_track['track_name'], the_track.name)
        self.assertEqual(self.summary_data_track['track_mixer'], the_track.side_mixer.name)

    def test_add_2_tracks(self):
        """ Check we can add two tracks to an LP ("Add Another Track" button test) """

        # Need to add a new LP to get to the add track page
        response = self.client.post('/lps/add', follow_redirects=True, data=self.full_data_lp)

        # Should have added lp and redirected to "Add Tracks" page
        self._check_add_track_form(response)

        # Determine the lp id and track id from the request url
        lp_id, track_id = self._track_1_ids(response.request)

        # Add first track information
        response = self.client.post('lps/add_track/{}/{}?media_type=MediaType.LP'.format(lp_id, track_id), follow_redirects=True, data=self.summary_data_first_track)

        # This should jump to a new add track form with an incremented track id. The request url looks like:
        #   <Request 'http://localhost/lps/add_track/0/1' [GET]>
        self._check_add_track_form(response)
        lp_id, new_track_id = self._track_n_ids(response.request)
        self.assertEqual(int(track_id) + 1, int(new_track_id))
        response = self.client.post('lps/add_track/{}/{}'.format(lp_id, new_track_id), follow_redirects=True, data=self.summary_data_second_track)

        # Check we have been redirected to main LP page
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(b'Music Media Library LPs Main Page', response.data)
        self.assertIn(b'Add New LP To Music Media Library', response.data)

        # Ensure track information stored in library
        all_lps = LPs()
        lps = all_lps.find_by_title(self.full_data_lp['title'])
        self.assertEqual(1, len(lps))
        the_lp = lps[0]
        self.assertEqual(2, len(the_lp.tracks))
        track_1 = the_lp.tracks[0]
        self.assertEqual(self.summary_data_first_track['track_name'], track_1.name)
        track_2 = the_lp.tracks[1]
        self.assertEqual(self.summary_data_second_track['track_name'], track_2.name)

    def test_add_track_cancel(self):
        """ Check cancelling while adding a track to an LP functioning correctly ("Cancel" button test) """
        # Need to add a new LP to get to the add track page
        response = self.client.post('/lps/add', follow_redirects=True, data=self.full_data_lp)

        # Should have added lp and redirected to "Add Tracks" page
        self._check_add_track_form(response)

        # Determine the lp id and track id from the request url
        lp_id, track_id = self._track_1_ids(response.request)

        # Check we can cancel addomg track information and it takes us back to the main LP Page
        cancel_track_data = self.full_data_track.copy()
        del cancel_track_data['save']
        cancel_track_data['cancel'] = True
        response = self.client.post('lps/add_track/{}/{}?media_type=MediaType.LP'.format(lp_id, track_id), follow_redirects=True, data=cancel_track_data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(b'Music Media Library LPs Main Page', response.data)
        self.assertIn(b'Add New LP To Music Media Library', response.data)

        # Should have one LP with no track information
        all_lps = LPs()
        self.assertEqual(1, all_lps.length)
        the_lp = all_lps.find_by_title(self.full_data_lp['title'])[0]
        self.assertEqual(0, len(the_lp.tracks))

    def test_add_track_one_song(self):
        """ Check that we can one song to the track on a new LP """

        # Add a new LP so we can get to the track list page to add some song information
        response = self.client.post('/lps/add', follow_redirects=True, data=self.full_data_lp)
        lp_id, track_id = self._track_1_ids(response.request)

        # Add track and song information
        response = self.client.post('lps/add_track/{}/{}?media_type=MediaType.LP'.format(lp_id, track_id), follow_redirects=True, data=self.full_data_track)

        # Check we have been redirected to main LP page
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(b'Music Media Library LPs Main Page', response.data)
        self.assertIn(b'Add New LP To Music Media Library', response.data)

        # Ensure we have all the song data on the track
        all_lps = LPs()
        lps = all_lps.find_by_title(self.full_data_lp['title'])
        self.assertEqual(1, len(lps))
        the_lp = lps[0]
        self.assertEqual(1, len(the_lp.tracks))
        the_track = the_lp.tracks[0]
        the_songs = the_track.song_list
        self.assertEqual(1, len(the_songs))
        the_song = the_songs[0]
        self.assertEqual(self.full_data_track['track_songs-0-song_title'], the_song.title)
        self.assertEqual(self.full_data_track['track_songs-0-song_mix'], the_song.mix)
        self.assertEqual(self.full_data_track['track_songs-0-song_featured_in'], the_song.featured_in)
        self.assertEqual(self.full_data_track['track_songs-0-song_classical_work'], the_song.classical_work)
        classical_composers = [self.full_data_track['track_songs-0-song_classical_composer_1'], self.full_data_track['track_songs-0-song_classical_composer_2']]
        the_song_classical_composers = [classical_composer.name for classical_composer in the_song.classical_composers]
        self.assertEqual(set(classical_composers), set(the_song_classical_composers))
        self.assertEqual(self.full_data_track['track_songs-0-song_country'], the_song.country)
        self.assertEqual(self.full_data_track['track_songs-0-song_year'], the_song.year)
        self.assertEqual(set(self.full_data_track['track_songs-0-song_parts'].split('\n')), set(the_song.parts))

    def test_add_track_two_song(self):
        """ Check that we can two songs to the track on a new LP """

        # Add a new LP so we can get to the track list page to add some song information
        response = self.client.post('/lps/add', follow_redirects=True, data=self.full_data_lp)
        lp_id, track_id = self._track_1_ids(response.request)

        # Add track and song information
        response = self.client.post('lps/add_track/{}/{}?media_type=MediaType.LP'.format(lp_id, track_id), follow_redirects=True, data=self.full_data_track_2_songs)

        # Check we have been redirected to main LP page
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(b'Music Media Library LPs Main Page', response.data)
        self.assertIn(b'Add New LP To Music Media Library', response.data)

        # Ensure we have all the song data on the track
        all_lps = LPs()
        lps = all_lps.find_by_title(self.full_data_lp['title'])
        self.assertEqual(1, len(lps))
        the_lp = lps[0]
        self.assertEqual(1, len(the_lp.tracks))
        the_track = the_lp.tracks[0]
        the_songs = the_track.song_list
        self.assertEqual(2, len(the_songs))
        the_song = the_songs[1]
        self.assertEqual(self.full_data_track_2_songs['track_songs-1-song_title'], the_song.title)

    @patch.object(MEDIA, 'to_html_file')
    def test_delete_lp(self, fake_write):
        """ Test we can delete an LP """

        # Add a new LP so we can get to the track list page to add some song information
        response = self.client.post('/lps/add', follow_redirects=True, data=self.full_data_lp)
        lp_id, track_id = self._track_1_ids(response.request)

        # Add track and song information
        response = self.client.post('lps/add_track/{}/{}?media_type=MediaType.LP'.format(lp_id, track_id), follow_redirects=True, data=self.full_data_track)

        # Check we have been redirected to main LP page
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(b'Music Media Library LPs Main Page', response.data)
        self.assertIn(b'Add New LP To Music Media Library', response.data)

        # Ensure we have an lp
        all_lps = LPs()
        self.assertEqual(1, all_lps.length)

        # First check cancelling the delete of an LP
        response = self.client.post('lps/delete/{}'.format(lp_id), follow_redirects=True, data=self.lp_cancel_delete_data)

        # Check we have been redirected to main LP page and still have one LP
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(b'Music Media Library LPs Main Page', response.data)
        self.assertIn(b'Add New LP To Music Media Library', response.data)
        self.assertEqual(1, all_lps.length)

        # Delete lp and ensure it is deleted
        response = self.client.post('lps/delete/{}'.format(lp_id), follow_redirects=True, data=self.lp_delete_data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(b'Music Media Library LPs Main Page', response.data)
        self.assertIn(b'Add New LP To Music Media Library', response.data)
        self.assertEqual(0, all_lps.length)

    def test_modify_lp(self):
        """ Test we can modify an LP's data """
        # Add a new LP so we can get to the track list page to add some song information
        response = self.client.post('/lps/add', follow_redirects=True, data=self.full_data_lp)
        lp_id, track_id = self._track_1_ids(response.request)

        # Add track and song information
        response = self.client.post('lps/add_track/{}/{}?media_type=MediaType.LP'.format(lp_id, track_id), follow_redirects=True, data=self.full_data_track)

        # Check we have been redirected to main LP page
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(b'Music Media Library LPs Main Page', response.data)
        self.assertIn(b'Add New LP To Music Media Library', response.data)

        # Ensure we have the lp and the mixer is the original which will be later changed
        all_lps = LPs()
        self.assertEqual(1, len(all_lps.find_by_title(self.full_data_lp['title'])))
        the_lp = all_lps.find_by_title(self.full_data_lp['title'])[0]
        self.assertEqual(self.full_data_lp['mixer'], the_lp.mixer.name)

        # First check cancelling the modification
        response = self.client.post('lps/modify/{}'.format(lp_id), follow_redirects=True, data=self.lp_cancel_modify_data)

        # Check we have been redirected to main LP page and no changes to the mixer name
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(b'Music Media Library LPs Main Page', response.data)
        self.assertIn(b'Add New LP To Music Media Library', response.data)
        the_lp = all_lps.find_by_title(self.full_data_lp['title'])[0]
        self.assertEqual(self.full_data_lp['mixer'], the_lp.mixer.name)

        # Make lp mixer modification. Note that the modify form has all the data so we must supply the same
        response = self.client.post('lps/modify/{}'.format(lp_id), follow_redirects=True, data=self.lp_modify_data)

        # Check we have been redirected to main LP page and the mixer name has changed
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(b'Music Media Library LPs Main Page', response.data)
        self.assertIn(b'Add New LP To Music Media Library', response.data)
        the_lp = all_lps.find_by_title(self.full_data_lp['title'])[0]
        self.assertEqual(self.lp_modify_data['mixer'], the_lp.mixer.name)
        self.assertEqual(1, all_lps.length)
        artists = Artists()
        mixer = artists.find_artist(self.lp_modify_data['mixer'])
        self.assertIsNotNone(mixer)

    def test_modify_and_add_new_track(self):
        """ Test modifying and adding a new track through modification of the LP """

        # Need to add a new LP to get to the add track page
        response = self.client.post('/lps/add', follow_redirects=True, data=self.full_data_lp)

        # Should have added lp and redirected to "Add Tracks" page
        self._check_add_track_form(response)

        # Determine the lp id and track id from the request url
        lp_id, track_id = self._track_1_ids(response.request)

        # Add track information
        response = self.client.post('lps/add_track/{}/{}?media_type=MediaType.LP'.format(lp_id, track_id), follow_redirects=True, data=self.summary_data_track)

        # Check we have been redirected to main LP page
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(b'Music Media Library LPs Main Page', response.data)
        self.assertIn(b'Add New LP To Music Media Library', response.data)

        # Make lp mixer modification and move to tracks. Note that the modify form has all the data so we must supply the same
        response = self.client.post('lps/modify/{}'.format(lp_id), follow_redirects=True, data=self.lp_modify_data_go_to_track)

        # Check we are on new track modification page
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('Modify Track #{} on "<b>{}</b>" Information'.format(int(track_id) + 1, self.lp_modify_data_go_to_track['title']).encode(),
                      response.data)

        # Update track info and move onto next/new track
        lp_id, track_id = self._track_n_ids(response.request)
        response = self.client.post('lps/modify_track/{}/{}'.format(lp_id, track_id), follow_redirects=True, data=self.track_modify_data)

        # Check we are on the correct page and the mods to the track name were made
        self.assertIn(b'Adding New Track To LP:', response.data)
        all_lps = LPs()
        the_lp = all_lps.find_by_title(self.lp_modify_data_go_to_track['title'])[0]
        self.assertEqual(self.track_modify_data['track_name'], the_lp.tracks[0].name)

        # Add new track info
        lp_id, track_id = self._track_n_ids(response.request)
        response = self.client.post('lps/modify_track/{}/{}'.format(lp_id, track_id), follow_redirects=True, data=self.new_track_data)

        # Check we have been redirected to main LP page
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(b'Music Media Library LPs Main Page', response.data)
        self.assertIn(b'Add New LP To Music Media Library', response.data)

        # Check modifications to the track have been made
        the_lp = all_lps.find_by_title(self.lp_modify_data_go_to_track['title'])[0]
        self.assertEqual(2, len(the_lp.tracks))
        self.assertEqual(self.track_modify_data['track_name'], the_lp.tracks[0].name)
        self.assertEqual(self.new_track_data['track_name'], the_lp.tracks[1].name)

    def test_modify_and_delete_song(self):
        """ Test modifying a song on an LP and then delete it """

        # Add a new LP so we can get to the track list page to add some song information
        response = self.client.post('/lps/add', follow_redirects=True, data=self.full_data_lp)
        lp_id, track_id = self._track_1_ids(response.request)

        # Add track and song information
        response = self.client.post('lps/add_track/{}/{}?media_type=MediaType.LP'.format(lp_id, track_id), follow_redirects=True, data=self.full_data_track)

        # Check we have been redirected to main LP page
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(b'Music Media Library LPs Main Page', response.data)
        self.assertIn(b'Add New LP To Music Media Library', response.data)

        # Modify the song title
        response = self.client.post('lps/modify_track_song/{}/{}/0?media_type=MediaType.LP'.format(lp_id, track_id), follow_redirects=True, data=self.modify_song_data)

        # Confirm redirected to main LP page and changes are in place
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(b'Music Media Library LPs Main Page', response.data)
        self.assertIn(b'Add New LP To Music Media Library', response.data)
        all_lps = LPs()
        the_lp = all_lps.find_by_title(self.full_data_lp['title'])[0]
        the_lp_track = the_lp.tracks[0]
        self.assertEqual(1, len(the_lp_track.song_list))
        the_song = the_lp_track.song_list[0]
        self.assertEqual(self.modify_song_data['song_title'], the_song.title)

        # Delete the song
        response = self.client.post('lps/modify_track_song/{}/{}/0?media_type=MediaType.LP'.format(lp_id, track_id), follow_redirects=True, data=self.delete_song_data)

        # Confirm redirected to add song page and this will be a new song
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('Modify A Song On Track "<b>{}</b>" of LP "<b>{}</b>'.format(self.full_data_track['track_name'], self.full_data_lp['title']).encode(), response.data)
        self.assertIn(b'New Song:', response.data)
        all_lps = LPs()
        the_lp = all_lps.find_by_title(self.full_data_lp['title'])[0]
        the_lp_track = the_lp.tracks[0]
        self.assertEqual(0, len(the_lp_track.song_list))

    def test_delete_track(self):
        # Track deletion needs to be implemented (Issue #113)
        pass
