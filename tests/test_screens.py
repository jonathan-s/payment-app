import os
import time
import unittest

from playhouse.test_utils import test_database
from peewee import SqliteDatabase
from flask_webtest import TestApp

from app import app
from models.models import Account, Transaction

test_db = SqliteDatabase(':memory:')


class ScreensTest(unittest.TestCase):

    def setUp(self):
        Account._meta.database = test_db
        self.app = app
        self.testapp = TestApp(self.app)

        self.params = {
                'to_account': 1,
                'from_account': 2,
                'amount': 10
            }

    def create_testdata(self):
        for number in xrange(1, 11):
            Account.create(name='account-{}'.format(number),
                           email='bogus@email.com',
                           balance=200)

    def test_account_view(self):
        with test_database(test_db, (Account, Transaction)):
            self.create_testdata()
            Transaction.create(account=1, amount=50)
            resp = self.testapp.get('/account/1')
            self.assertEqual(len(resp.context['transactions']), 1)
            self.assertEqual(resp.context['account'].name, 'account-1')

    def test_account_view_errors(self):
        with test_database(test_db, (Account,)):
            resp = self.testapp.get('/account/11', expect_errors=True)
            self.assertEqual(resp.status_code, 404)

    def test_accounts_list(self):
        with test_database(test_db, (Account,)):
            self.create_testdata()
            resp = self.testapp.get('/accounts')

            self.assertEqual(resp.context['accounts'].count, 10)

    def test_payment_post(self):
        with test_database(test_db, (Account, Transaction)):
            self.create_testdata()

            resp = self.testapp.get('/payment')
            resp = self.testapp.post('/payment', params=self.params)
            self.assertEqual(resp.status_code, 302)

    def test_payment_post_fails(self):
        with test_database(test_db, (Account, Transaction)):
            self.create_testdata()
            resp = self.testapp.get('/payment')
            self.params['amount'] = 300
            resp = self.testapp.post('/payment', params=self.params)

            self.assertEqual(resp.status_code, 200)

