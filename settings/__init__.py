import os.path
from os.path import dirname

SECRET_KEY = '1312412341'

root = dirname(dirname(os.path.abspath(__file__)))
DATABASE_LOCATION = os.path.join(root, 'payment.db')
