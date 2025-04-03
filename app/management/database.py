from pymongo import MongoClient
import os

client = MongoClient(os.environ.get("MONGO_URI"))
db = client[os.environ.get("DB_CLIENT")]

class database:
    users_collection = db[f"{os.environ.get('USER_COLLECTION')}"]
    gas_collection = db[f"{os.environ.get('GAS_RECORDS')}"]
    notification_collection = db[f"{os.environ.get('NOTIFICATION_COLLECTION')}"]
    chart_collection = db[f"{os.environ.get('CHART_COLLECTION')}"]