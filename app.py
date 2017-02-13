import os
from subprocess import call

from flask import Flask
from flask import g

from models.models import db, Account, Transaction
from views.screens import (AccountView,
                           AccountListView,
                           PaymentView,
                           IndexView)

app = Flask(__name__)
app.config.from_pyfile('settings/__init__.py')
app.config.from_pyfile('settings/{}.py'.format(
    os.environ.get('environment', 'development')), silent=True)


def init_db():
    """Initializes the database."""
    call(['rm', 'payment.db'])
    db.connect()
    db.create_tables([Account, Transaction], safe=True)
    for x in xrange(1, 11):
        Account.create(name='Account-{}'.format(x),
                       email='bogus@email.com',
                       balance=200)


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


@app.cli.command('tests')
def testcases():
    """Calls the unittests."""
    call(['python', '-B', '-m', 'unittest', 'discover'])

@app.before_request
def connect_db():
    if not hasattr(g, 'db'):
        g.db = db
        g.db.connect()

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()

routes = [
    ('/account/<int:id>', AccountView.as_view('account_view', template_name='account.html')),
    ('/accounts', AccountListView.as_view('account_list', template_name='account_list.html')),
    ('/payment', PaymentView.as_view('payment', template_name='payment.html')),
    ('/', IndexView.as_view('index', template_name='index.html'))
]

for url, view in routes:
    app.add_url_rule(url, view_func=view)


if __name__ == "__main__":
    # import pdb; pdb.set_trace()
    app.run()
