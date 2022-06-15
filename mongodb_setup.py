import pymongo
import json


def connect():
    return pymongo.MongoClient()


def createDB(conn):
    return conn['BDT2022']


def createColl(db):
    return db['real_estate_data']


def populateDB(coll):
    with open('new_scraped_results.txt') as f:
        to_insert = json.loads(f.read())
    coll.insert_many(to_insert)


myconn = connect()
mydb = createDB(myconn)
mycoll = createColl(mydb)
populateDB(mycoll)
# test
print(mydb.real_estate_data.find_one({'city': 'Geneva'}))
