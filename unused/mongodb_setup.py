import pymongo
import json


def connect():
    return pymongo.MongoClient()


def createDB(conn):
    return conn['BDT2022']


def createColl(db):
    return db['real_estate_data']


def populateDB(coll, to_insert):
    coll.insert_many(to_insert)