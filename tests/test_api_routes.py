from http import HTTPStatus
import unittest

from flask_login import FlaskLoginClient

from app.app import app, db
from app.demo_helpers import DVDs_data, load_demo_data
from app.models import User


class ApiRoutesTestCase(unittest.TestCase):
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
