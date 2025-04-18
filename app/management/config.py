from pymongo import MongoClient
import os
import random
import string


class database:
    client = MongoClient(os.environ.get("MONGO_URI"))
    db = client[os.environ.get("DB_CLIENT")]
    users_collection = db[f"{os.environ.get('USER_COLLECTION')}"]
    gas_collection = db[f"{os.environ.get('GAS_RECORDS')}"]
    notification_collection = db[f"{os.environ.get('NOTIFICATION_COLLECTION')}"]
    chart_collection = db[f"{os.environ.get('CHART_COLLECTION')}"]
    prediction_collection = db[f"{os.environ.get('PREDICTION_COLLECTION')}"]
    image_collection = db[f"{os.environ.get('IMAGE_COLLECTION')}"]
    prediction_models_collection = db[f"{os.environ.get('PREDICTION_MODELS')}"]
    gas_trends_collection = db[f"{os.environ.get('GAS_TRENDS')}"]
    insight_collection = db[f"{os.environ.get('INSIGHT_COLLECTIONS')}"]
    
class cipher:
    REGISTRATION_KEY = os.environ.get("REGISTRATION_KEY")
    SECRET_KEY = os.environ.get("SECRET_KEY")
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    
class AppConfig:
    JWT_SECRET_KEY = cipher.SECRET_KEY
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_ACCESS_COOKIE_NAME = "access_token_cookie"
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_COOKIE_SECURE = False  # Set to True for production (HTTPS)
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = cipher.MAIL_USERNAME
    MAIL_PASSWORD = cipher.MAIL_PASSWORD

def generate_reset_token():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))