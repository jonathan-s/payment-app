import unittest

from playhouse.test_utils import test_database
from peewee import SqliteDatabase
from mock import MagicMock

from models.models import Account, Transaction
from models.models import TransferException

test_db = SqliteDatabase(':memory:')


class AccountModelTest(unittest.TestCase):

    def setUp(self):
        Account.objects._sender = MagicMock()

    def create_testdata(self):
        for number in xrange(10):
            Account.create(name='account-{}'.format(number),
                           email='bogus@email.com',
                           balance=200)

    def test_listing_accounts(self):
        with test_database(test_db, (Account,)):
            self.create_testdata()

            accounts = Account.objects.get_accounts()
            self.assertEqual(len(accounts), 10)

    def test_get_single_account(self):
        with test_database(test_db, (Account,)):
            self.create_testdata()
            account = Account.objects.get_account(id=1)
            self.assertEqual(account.name, 'account-0')

    def test_update_balance(self):
        with test_database(test_db, (Account,)):
            self.create_testdata()

            Account.objects._update_balance(1, -30)
            account = Account.get(Account.id == 1)
            self.assertEqual(account.balance, 170)

    def test_transfer_between_account(self):
        with test_database(test_db, (Account, Transaction)):
            self.create_testdata()

            Account.objects.transfer(1, 2, 100)

            account1 = Account.get(Account.id == 1)
            account2 = Account.get(Account.id == 2)

            self.assertEqual(account1.balance, 100)
            self.assertEqual(account2.balance, 300)

    def test_transfer_creates_two_transactions(self):
        with test_database(test_db, (Account, Transaction)):
            self.create_testdata()

            Account.objects.transfer(1, 2, 50)

            transactions = Transaction.select().execute()
            transactions = [txn for txn in transactions]
            self.assertEqual(len(transactions), 2)
            self.assertEqual(transactions[0].amount, -50)
            self.assertEqual(transactions[1].amount, 50)

    def test_get_transactions_for_account(self):
        with test_database(test_db, (Account, Transaction)):
            self.create_testdata()
            Transaction.create(account=1, amount=50)
            Transaction.create(account=2, amount=100)

            txns = Transaction.objects.transactions_for_account(1)
            transactions = [txn for txn in txns]

            self.assertEqual(len(transactions), 1)
            self.assertEqual(transactions[0].amount, 50)

    def test_transfer_negative_amount(self):
        with test_database(test_db, (Account,)):
            self.create_testdata()
            with self.assertRaises(TransferException):
                Account.objects.transfer(1, 2, -100)

    def test_transfer_not_enough_funds(self):
        with test_database(test_db, (Account,)):
            self.create_testdata()
            with self.assertRaises(TransferException):
                Account.objects.transfer(1, 2, 300)

