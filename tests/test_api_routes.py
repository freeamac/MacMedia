from http import HTTPStatus
import os
import unittest

from flask_login import FlaskLoginClient

from app.app import app, db
from app.demo_helpers import DVDs_data, load_demo_data
from app.musicmedia.musicmedia_objects import Artists, CASSETTEs, CDs, ELPs, LPs, MEDIA, MediaType, MINI_CDs
from app.models import User


class ApiDVDRoutesTestCase(unittest.TestCase):
    """ Test the DVD routes (views).

        *Note* that exceptions cannot be tested. There seems to be no way
        to check if a message has been flashed on screen which occurs
        during error paths.
    """

    testuser = 'testuser'
    testuser_password = 'testuser_password'  # nosec

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
        self.app = app
        self.app_context = self.app.test_request_context()
        self.app_context.push()
        self.db = db
        self.new_testuser = User(username=self.testuser, password=self.testuser_password)
        self._populate_db()
        self.testing = True
        self.app.test_client_class = FlaskLoginClient
        self.client = self.app.test_client(user=self.new_testuser)

    def tearDown(self):
        self.db.drop_all()
        self.app_context.pop()

    def test_dvds(self):
        """ Check the DVD download api"""
        response = self.client.get('/api/v1/dvds', follow_redirects=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(response.mimetype, 'application/json')
        json_response = response.json
        dvds_in_response = json_response['data']
        self.assertEqual(len(dvds_in_response), len(DVDs_data))
        dvd_titles_in_response_set = set([dvd['title'] for dvd in dvds_in_response])
        dvd_titles_in_db = set([dvd['title'] for dvd in DVDs_data])
        self.assertEqual(dvd_titles_in_response_set, dvd_titles_in_db)


class ApiMusicMediaRoutesTestCase(unittest.TestCase):
    """ Test Music Media api routes (views). """

    testuser = 'testuser'
    testuser_password = 'testuser_password'  # nosec

    DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')
    MUSIC_HTML_FILE = os.path.join(DATA_DIR, 'test_music.html')

    def setUp(self):
        # Set up Flask test environment and push the context
        self.app = app
        self.app_context = self.app.test_request_context()
        self.app_context.push()
        self.new_testuser = User(username=self.testuser, password=self.testuser_password)
        self.testing = True
        self.app.test_client_class = FlaskLoginClient
        self.client = self.app.test_client(user=self.new_testuser)

        # Clean out any debris in the music media lists
        Artists()._clean_artists()
        CDs()._clean_cds()
        ELPs()._clean_elps()
        LPs()._clean_lps()
        MINI_CDs()._clean_mini_cds()
        CASSETTEs()._clean_cassettes()

        # Now read in all the music media test samples
        MEDIA.from_html_file(self.MUSIC_HTML_FILE)

    def tearDown(self):
        Artists()._clean_artists()
        CDs()._clean_cds()
        ELPs()._clean_elps()
        LPs()._clean_lps()
        MINI_CDs()._clean_mini_cds()
        self.app_context.pop()

    def test_lps(self):
        # Load in all the data
        all_artists = Artists()
        all_lps = LPs()

        print('Number of artists found: {}'.format(len(all_artists.artists)))
        print('Number of lps found: {}'.format(len(all_lps.lps)))

        # Grab all LP information from the api call
        response = self.client.get('/api/v1/musicmedia_data/' + MediaType.LP.value, follow_redirects=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(response.mimetype, 'application/json')

        json_response = response.json
        lps_in_response = json_response['data']
        self.assertEqual(len(lps_in_response), 9)

        lp_titles_in_response_set = set([lp['title'] for lp in lps_in_response])
        lp_titles_in_list = set([lp.title for lp in LPs().lps])
        self.assertEqual(lp_titles_in_response_set, lp_titles_in_list)

        lp_years_in_response_set = set([lp['year'] for lp in lps_in_response])
        lp_years_in_list = set([lp.year for lp in LPs().lps])
        self.assertEqual(lp_years_in_response_set, lp_years_in_list)

        lp_artists_in_response_set = set([lp['artists'] for lp in lps_in_response])
        self.assertIn('Michael Buble', lp_artists_in_response_set)

    def test_cds(self):
        # Load in all the data
        all_artists = Artists()
        all_cds = CDs()

        print('Number of artists found: {}'.format(len(all_artists.artists)))
        print('Number of cds found: {}'.format(len(all_cds.cds)))

        # Grab all LP information from the api call
        response = self.client.get('/api/v1/musicmedia_data/' + MediaType.CD.value, follow_redirects=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(response.mimetype, 'application/json')

        json_response = response.json
        cds_in_response = json_response['data']
        self.assertEqual(len(cds_in_response), 8)

        cd_titles_in_response_set = set([cd['title'] for cd in cds_in_response])
        cd_titles_in_list = set([cd.title for cd in CDs().cds])
        self.assertEqual(cd_titles_in_response_set, cd_titles_in_list)

        cd_years_in_response_set = set([cd['year'] for cd in cds_in_response])
        cd_years_in_list = set([cd.year for cd in CDs().cds])
        self.assertEqual(cd_years_in_response_set, cd_years_in_list)

        cd_artists_in_response_set = set([cd['artists'] for cd in cds_in_response])
        self.assertIn('Elton John', cd_artists_in_response_set)

    def test_mini_cds(self):
        # Load in all the data
        all_artists = Artists()
        all_mini_cds = MINI_CDs()

        print('Number of artists found: {}'.format(len(all_artists.artists)))
        print('Number of mini cds found: {}'.format(len(all_mini_cds.mini_cds)))

        # Grab all LP information from the api call
        response = self.client.get('/api/v1/musicmedia_data/' + MediaType.MINI_CD.value, follow_redirects=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(response.mimetype, 'application/json')

        json_response = response.json
        mini_cds_in_response = json_response['data']
        self.assertEqual(len(mini_cds_in_response), 1)

        mini_cd_titles_in_response_set = set([mini_cd['title'] for mini_cd in mini_cds_in_response])
        mini_cd_titles_in_list = set([mini_cd.title for mini_cd in MINI_CDs().mini_cds])
        self.assertEqual(mini_cd_titles_in_response_set, mini_cd_titles_in_list)

        mini_cd_years_in_response_set = set([mini_cd['year'] for mini_cd in mini_cds_in_response])
        mini_cd_years_in_list = set([mini_cd.year for mini_cd in MINI_CDs().mini_cds])
        self.assertEqual(mini_cd_years_in_response_set, mini_cd_years_in_list)

        mini_cd_artists_in_response_set = set([mini_cd['artists'] for mini_cd in mini_cds_in_response])
        self.assertIn("Guns N' Roses", mini_cd_artists_in_response_set)

    def test_elps(self):
        # Load in all the data
        all_artists = Artists()
        all_elps = ELPs()

        print('Number of artists found: {}'.format(len(all_artists.artists)))
        print('Number of elps found: {}'.format(len(all_elps.elps)))

        # Grab all LP information from the api call
        response = self.client.get('/api/v1/musicmedia_data/' + MediaType.ELP.value, follow_redirects=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(response.mimetype, 'application/json')

        json_response = response.json
        elps_in_response = json_response['data']
        self.assertEqual(len(elps_in_response), 1)

        elps_titles_in_response_set = set([elps['title'] for elps in elps_in_response])
        elps_titles_in_list = set([elps.title for elps in ELPs().elps])
        self.assertEqual(elps_titles_in_response_set, elps_titles_in_list)

        elps_years_in_response_set = set([elps['year'] for elps in elps_in_response])
        elps_years_in_list = set([elps.year for elps in ELPs().elps])
        self.assertEqual(elps_years_in_response_set, elps_years_in_list)

        elps_artists_in_response_set = set([elps['artists'] for elps in elps_in_response])
        self.assertIn('Bryan Adams', elps_artists_in_response_set)

    def test_cassettes(self):
        # Load in all the data
        all_artists = Artists()
        all_cassettes = CASSETTEs()

        print('Number of artists found: {}'.format(len(all_artists.artists)))
        print('Number of cassettes found: {}'.format(len(all_cassettes.cassettes)))

        # Grab all LP information from the api call
        response = self.client.get('/api/v1/musicmedia_data/' + MediaType.CASSETTE.value, follow_redirects=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(response.mimetype, 'application/json')

        json_response = response.json
        cassettes_in_response = json_response['data']
        self.assertEqual(len(cassettes_in_response), 1)

        cassettes_titles_in_response_set = set([cassettes['title'] for cassettes in cassettes_in_response])
        cassettes_titles_in_list = set([cassettes.title for cassettes in CASSETTEs().cassettes])
        self.assertEqual(cassettes_titles_in_response_set, cassettes_titles_in_list)

        cassettes_years_in_response_set = set([cassettes['year'] for cassettes in cassettes_in_response])
        cassettes_years_in_list = set([cassettes.year for cassettes in CASSETTEs().cassettes])
        self.assertEqual(cassettes_years_in_response_set, cassettes_years_in_list)

        cassettes_artists_in_response_set = set([cassettes['artists'] for cassettes in cassettes_in_response])
        self.assertIn('Various Artists', cassettes_artists_in_response_set)