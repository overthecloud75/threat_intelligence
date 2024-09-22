from pymongo import MongoClient
from configs import MONGO_URL, logger

mongoClient = MongoClient(MONGO_URL)
db = mongoClient['report']

db.ti_description.create_index([('timestamp', 1), ('id', 1)])
db.ti_indicator.create_index([('id', 1), ('indicator', 1)])

def post_description_to_db(result):
    collection = db['ti_description'] 
    try:
        collection.update_one({'id': result['id']}, {'$set': result}, upsert=True)
    except Exception as e:
        logger.error(e)

def post_indicator_to_db(result):
    collection = db['ti_indicator'] 
    try:
        collection.update_one({'id': result['id'], 'indicator': result['indicator']}, {'$set': result}, upsert=True)
    except Exception as e:
        logger.error(e)