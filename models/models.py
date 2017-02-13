import datetime as dt

from peewee import (CharField,
                    DecimalField,
                    DateTimeField,
                    ForeignKeyField,
                    IntegerField,
                    Model)
from playhouse.sqlite_ext import SqliteExtDatabase
from settings import DATABASE_LOCATION

db = SqliteExtDatabase(DATABASE_LOCATION)


class TransferException(Exception):
    pass


class BaseModel(Model):

    class Meta:
        database = db

class EmailSender(object):

    def send_email(self, to_email):
        """Dummy side effect to show that email has been sent"""
        print "Sent fake email to {}!!!!".format(to_email)


class AccountManager(object):

    def __init__(self):
        self._sender = EmailSender()

    def send_email(self, to_email):
        self._sender.send_email(to_email)

    def get_accounts(self):
        accounts = Account.select().order_by(Account.name).execute()
        return accounts

    def get_account(self, id):
        account = Account.get(Account.id == id)
        return account

    def _update_balance(self, id, amount):
        with db.atomic() as txn:
            Account.update(balance=Account.balance + amount).where(
                Account.id == id).execute()

    def transfer(self, from_id, to_id, amount):
        with db.atomic() as txn:
            from_account = Account.get(Account.id == from_id)
            to_account = Account.get(Account.id == to_id)

            if from_account.balance < amount:
                raise TransferException('Not enough funds')

            if amount < 0:
                raise TransferException('Can\'t force someone to give you money')

            self._update_balance(from_id, -amount)
            self._update_balance(to_id, amount)

            Transaction.create(account=from_id,
                               amount=-amount)
            Transaction.create(account=to_id,
                               amount=amount)
        self.send_email(from_account.email)
        self.send_email(to_account.email)

class Account(BaseModel):

    name = CharField(max_length=50, null=False, index=True)
    email = CharField(max_length=50, null=False)
    balance = DecimalField(decimal_places=2, null=False)

    objects = AccountManager()


class TransactionManager(object):

    def transactions(self):
        return Transaction.select().order_by(Transaction.timestamp).execute()

    def transactions_for_account(self, account_id):
        txns = Transaction.select().where(Transaction.account == account_id).execute()
        return txns


class Transaction(BaseModel):

    account = ForeignKeyField(Account, related_name='transactions')
    amount = DecimalField(decimal_places=2, null=False)
    timestamp = DateTimeField(default=dt.datetime.now)

    objects = TransactionManager()
