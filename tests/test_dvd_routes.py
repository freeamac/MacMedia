from http import HTTPStatus
import unittest

from flask_login import FlaskLoginClient

from app.app import app, db
from app.demo_helpers import load_demo_data
from app.models import User
from app.queries import dvd_exists, get_all_dvds


class DvdRoutesTestCase(unittest.TestCase):
    """ Test the DVD routes (views).

        *Note* that exceptions cannot be tested. There seems to be no way
        to check if a message has been flashed on screen which occurs
        during error paths.
    """

    testuser = 'testuser'
    testuser_password = 'testuser_password'  # nosec

    new_dvd = {'dvd_title': 'New Dvd',
               'dvd_series': 'New Series',
               'dvd_year': 2022,
               'dvd_set': 'New Set',
               'dvd_media_type': 'Dvd',
               'dvd_music_type': 'No',
               'dvd_music_artist': '',
               'submit': True}

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

    def _check_dvd_form(self, response):
        # Check have all the fields in a standard full DVD form
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(b'DVD Movie Title', response.data)
        self.assertIn(b'Movie Series', response.data)
        self.assertIn(b'Year Of Release', response.data)
        self.assertIn(b'From Set', response.data)
        self.assertIn(b'DVD Type?', response.data)
        self.assertIn(b'Music DVD?', response.data)
        self.assertIn(b'Music DVD Artist', response.data)

    def test_index(self):
        """ Check the DVD main index page response """

        response = self.client.get('/dvds/', follow_redirects=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        # Note we cannot check the contents as the is produced through an Ajax api call
        self.assertIn(b'DVDs Library Main Page', response.data)

    def test_add_dvd(self):
        """ Check the add DVD page response """

        # Check we have the proper form
        response = self.client.get('/dvds/add/', follow_redirects=True)
        self._check_dvd_form(response)

        # Check we can post a new DVD to the db
        response = self.client.post('/dvds/add/', follow_redirects=True, data=self.new_dvd)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        # Should have added dvd and redirected to DVD main index page
        self.assertIn(b'DVDs Library Main Page', response.data)
        self.assertTrue(dvd_exists(self.db, title=self.new_dvd['dvd_title'], series=self.new_dvd['dvd_series'],
                                   year=self.new_dvd['dvd_year'], set=self.new_dvd['dvd_set']))

    def test_delete_dvd(self):
        """ Check the delete DVD page response """

        # Get a DVD id to delete
        dvd_to_delete = get_all_dvds(self.db)[0]
        dvd_to_delete_id = int(dvd_to_delete['id'])

        # Dbl check the DVD exists
        self.assertTrue(dvd_exists(self.db, title=dvd_to_delete['title'], series=dvd_to_delete['series'],
                                   year=dvd_to_delete['year'], set=dvd_to_delete['set']))

        # Check we have the proper form
        response = self.client.get('/dvds/delete/{}'.format(dvd_to_delete_id), follow_redirects=True)
        self._check_dvd_form(response)

        # Post a delete of the DVD
        response = self.client.post('/dvds/delete/{}'.format(dvd_to_delete_id), follow_redirects=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        # Should have added dvd and redirected to DVD main index page
        self.assertIn(b'DVDs Library Main Page', response.data)

        # Check it has been deleted
        self.assertFalse(dvd_exists(self.db, title=dvd_to_delete['title'], series=dvd_to_delete['series'],
                                    year=dvd_to_delete['year'], set=dvd_to_delete['set']))

    def test_modify_dvd(self):
        """ Check the modify DVD page response """

        # Get a DVD id to modify
        dvd_to_modify = get_all_dvds(self.db)[0]
        dvd_to_modify_id = int(dvd_to_modify['id'])

        # Dbl check the DVD exists
        self.assertTrue(dvd_exists(self.db, title=dvd_to_modify['title'], series=dvd_to_modify['series'],
                                   year=dvd_to_modify['year'], set=dvd_to_modify['set']))

        # Check we have the proper form
        response = self.client.get('/dvds/modify/{}'.format(dvd_to_modify_id), follow_redirects=True)
        self._check_dvd_form(response)

        # Post a modify of the DVD
        if dvd_to_modify['artist'] is None:
            artist = ''
        else:
            artist = dvd_to_modify['artist']
        modify_data = {'dvd_title': 'New Title',
                       'dvd_series': dvd_to_modify['series'],
                       'dvd_year': int(dvd_to_modify['year']),
                       'dvd_set': dvd_to_modify['set'],
                       'dvd_media_type': dvd_to_modify['media_type'].capitalize(),
                       'dvd_music_type': dvd_to_modify['music_type'],
                       'dvd_music_artist': artist}
        response = self.client.post('/dvds/modify/{}'.format(dvd_to_modify_id), data=modify_data, follow_redirects=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        # Should have added dvd and redirected to DVD main index page
        self.assertIn(b'DVDs Library Main Page', response.data)

        # Check it has been modified
        self.assertTrue(dvd_exists(self.db, title='New Title', series=dvd_to_modify['series'],
                                   year=dvd_to_modify['year'], set=dvd_to_modify['set']))