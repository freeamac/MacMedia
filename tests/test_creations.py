import unittest

import pytest

from app import create_app, db
from app.creations import db_create_dvd
from app.exceptions import UniqueNameError
from app.demo_helpers import load_demo_data
from app.models import DEFAULT_DVD_MEDIA_TYPE
from app.queries import dvd_exists, get_all_dvds, get_dvd_by_id


class CreationTestCase(unittest.TestCase):
    """ This class tests the creation functionality used by the POST routes and administrator forms. """

    valid_new_dvd = {'title': 'The Test DVD',
                     'series': None,
                     'year': 2021,
                     'set': None,
                     'media_type': 'dvd',
                     'music_type': False,
                     'artist': None}
    valid_existing_dvd = {'title': 'The Chronicles Of Riddick',
                          'year': 2004,
                          'series': 'Riddick',
                          'set': None,
                          'media_type': DEFAULT_DVD_MEDIA_TYPE}

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
        self.db.session.commit()

    def setUp(self):
        # Just need to get access to the database instance here
        # and push the context
        self.app = create_app('creation_test')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.testing = True
        self.client = self.app.test_client(use_cookies=True)
        self.db = db
        self._populate_db()

    def tearDown(self):
        self.db.drop_all()
        self.app_context.pop()

    def _dvd_data_equal(self, new_dvd, existing_dvd, skip_id=False):
        """ Compare DVD data dictionaries are equal. Skip the id when it is data to be inserted. """
        for key in new_dvd.keys():
            if key == 'music_type':
                # Music type can be a string of values 'Yes' or 'No' which
                # corresponds to a bool of values 'True' or 'False'.
                if isinstance(new_dvd['music_type'], str):
                    if new_dvd['music_type'] == 'Yes':
                        self.assertIn(existing_dvd['music_type'], ['Yes', True])
                    else:
                        self.assertIn(existing_dvd['music_type'], ['No', False])
                else:
                    if new_dvd['music_type']:
                        self.assertIn(existing_dvd['music_type'], ['Yes', True])
                    else:
                        self.assertIn(existing_dvd['music_type'], ['No', False])
            elif key == 'id':
                if not skip_id:
                    self.assertEqual(new_dvd['id'], existing_dvd['id'])
            else:
                self.assertEqual(new_dvd[key], existing_dvd[key])

    def test_db_create_dvd(self):
        """ Test creating an new DVD """

        dvd_cnt = len(get_all_dvds(self.db))

        # Test adding a valid DVD
        new_dvd = db_create_dvd(self.db, self.valid_new_dvd)
        new_dvd_dict = new_dvd.to_dict()
        self._dvd_data_equal(new_dvd_dict, self.valid_new_dvd, skip_id=True)
        self.assertTrue(dvd_exists(self.db, **self.valid_new_dvd))
        self.assertEqual(dvd_cnt + 1, len(get_all_dvds(self.db)))

        # Test getting the added DVD from the dictionary by id
        model_new_dvd = get_dvd_by_id(self.db, new_dvd_dict['id'], model=True)
        self._dvd_data_equal(new_dvd_dict, model_new_dvd.to_dict(), skip_id=False)
        new_dvd = get_dvd_by_id(self.db, new_dvd_dict['id'], model=False)
        self._dvd_data_equal(new_dvd, self.valid_new_dvd, skip_id=True)

        # Test we cannot add an existing DVD
        with pytest.raises(UniqueNameError):
            new_dvd = db_create_dvd(self.db, self.valid_existing_dvd)