C"""
Nose tests for memos

We cannot test for randomness here (no effective oracle),
but we can test that the elements in the returned string
are correct.
"""
import pymongo
from pymongo import MongoClient
import arrow
import sys
from dateutil import tz  # For interpreting local times
import config
import nose  # Testing framework
import logging
from db_trial import *

CONFIG = config.configuration(proxied=True)

logging.basicConfig(format='%(levelname)s:%(message)s',
                    level=logging.WARNING)
log = logging.getLogger(__name__)

MONGO_CLIENT_URL = "mongodb://{}:{}@{}:{}/{}".format(
    CONFIG.DB_USER,
    CONFIG.DB_USER_PW,
    CONFIG.DB_HOST,
    CONFIG.DB_PORT,
    CONFIG.DB)

print("Using URL '{}'".format(MONGO_CLIENT_URL))

try:
    dbclient = MongoClient(MONGO_CLIENT_URL)
    db = getattr(dbclient, CONFIG.DB)
    print("Got database")
    collection = db.dated
    print("Using sample collection")
except Exception as err:
    print("Failed")
    print(err)
    sys.exit(1)

# Note: I use for loop to test much test cases.
test_case = 10
init_number = collection.count()

def test_save_memos():
    assert len(collection.count()) == init_number
    for i in range(test_case):
        record = {"type": "dated_memo",
                  "date": arrow.utcnow().replace(days=+i).naive,
                  "text": "No." + str(i) + "This is a sample memo",
                  "token": i}
        collection.insert_one(record)
        assert len(collection.count()) == i + 1 + init_number


def test_list_memos():
    records = []
    assert len(records) == 0
    for record in collection.find({"type": "dated_memo"}):
        records.append(
            {"type": record['type'],
             "date": arrow.get(record['date']).to('local').isoformat(),
             "text": record['text'],
             "token": record['token']})

    assert len(records) == test_case


def test_delete_memos():
    assert len(collection.count()) == test_case + init_number
    for i in range(test_case):
        collection.delete_one({'token': i})
        assert len(collection.count()) == test_case + init_number - i - 1
