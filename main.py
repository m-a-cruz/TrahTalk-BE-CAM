from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from app.routes import auth, gas, camera, insight
from app.management.middleware import log_request, protected_route
from app.management.config import AppConfig
import sys
from os.path import abspath, dirname
from scheduler import start_scheduler

sys.path.append(abspath(dirname(__file__)))


# Initialize Flask app
app = Flask(__name__)

# Start the scheduler
start_scheduler()

# Load configurations from AppConfig
app.config["JWT_SECRET_KEY"] = AppConfig.JWT_SECRET_KEY
app.config["JWT_TOKEN_LOCATION"] = AppConfig.JWT_TOKEN_LOCATION
app.config["JWT_ACCESS_COOKIE_NAME"] = AppConfig.JWT_ACCESS_COOKIE_NAME
app.config["JWT_COOKIE_CSRF_PROTECT"] = AppConfig.JWT_COOKIE_CSRF_PROTECT
app.config["JWT_COOKIE_SECURE"] = AppConfig.JWT_COOKIE_SECURE
app.config["MAIL_SERVER"] = AppConfig.MAIL_SERVER
app.config["MAIL_PORT"] = AppConfig.MAIL_PORT
app.config["MAIL_USE_TLS"] = AppConfig.MAIL_USE_TLS
app.config["MAIL_USERNAME"] = AppConfig.MAIL_USERNAME
app.config["MAIL_PASSWORD"] = AppConfig.MAIL_PASSWORD

jwt = JWTManager(app)
mail = Mail(app)
CORS(app, supports_credentials=True)

@app.before_request
def before_request(): 
    log_request(request)

@app.route("/protected", methods=["GET"])
@protected_route
def protected():
    return jsonify({"message": "You have access to this route!"}), 200

app.register_blueprint(auth.auth_bp)
app.register_blueprint(gas.gas_bp)
app.register_blueprint(camera.camera_bp)
app.register_blueprint(insight.insight_bp)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
