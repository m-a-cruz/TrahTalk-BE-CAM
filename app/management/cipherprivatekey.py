import os

class CiperPrivateKey:
    REGISTRATION_KEY = os.environ.get("REGISTRATION_KEY")
    SECRET_KEY = os.environ.get("SECRET_KEY")
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")