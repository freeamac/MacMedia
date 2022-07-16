import unittest

import pytest

from app import create_app, db
from app.exceptions import ModelNotFound
from app.models import load_initial_users
from app.queries import get_user
from app.updates import db_update_user_password


class UserOperationsTestCase(unittest.TestCase):
    """ This class tests the functionality used to operate on Users. """

    valid_user1 = 'Andy'
    valid_user2 = 'Tomomi'
    invalid_user = 'andy'
    valid_user1_password = 'pbkdf2:sha256:260000$s4wuv5pHJy7TwTYL$e52ee054fc1364bd00a069b2d9301ac70813f174cca00bc95a3c0e233782935e'
    valid_user2_password = 'pbkdf2:sha256:260000$s4wuv5pHJy7TwTYL$e52ee054fc1364bd00a069b2d9301ac70813f174cca00bc95a3c0e233782935e'
    new_password = 'pbkdf2:sha256:260000$s4wuv5pHJy7TwTYL$e52ee054fc1364bd00a069b2d9301ac70813f174cca00bc95a3c0e233782934e'

    def _db_reset(self):
        """ Drop all tables and re-create them """
        self.db.drop_all()
        self.db.create_all()

    def _populate_db(self):
        """ Populate a fresh database with test data """
        self._db_reset()
        self.db.session.commit()

        # Populate with test data
        load_initial_users(self.db)
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

    def test_db_query_user(self):
        """ Test querying Users """

        user1 = get_user(self.db, self.valid_user1)
        self.assertEqual(user1.username, self.valid_user1)
        self.assertEqual(user1.password, self.valid_user1_password)

        user2 = get_user(self.db, self.valid_user2)
        self.assertEqual(user2.username, self.valid_user2)
        self.assertEqual(user2.password, self.valid_user2_password)

        invalid_user = get_user(self.db, self.invalid_user)
        self.assertIsNone(invalid_user)

    def test_db_update_user_password(self):
        """ Test updating User passwords """

        # Set new password which since encoded should not match input
        db_update_user_password(self.db, self.valid_user1, self.new_password)
        user = get_user(self.db, self.valid_user1)
        self.assertEqual(user.username, self.valid_user1)
        self.assertNotEqual(user.password, self.new_password)

        with pytest.raises(ModelNotFound):
            db_update_user_password(self.db, self.invalid_user, self.new_password)
