__author__ = 'koba'
import os

DIR = os.path.dirname(os.path.realpath(__file__))

DB_URL = 'sqlite:///' + os.path.join(DIR, 'watcher.db')
PUSH_ID = '8714'
PUSH_KEY = '0f6949fd0f8d9922ed855da4dc45377b'
JOB_INTERVALS = {'hour': '0-2,12-23', 'minute': '01,16,31,46'}