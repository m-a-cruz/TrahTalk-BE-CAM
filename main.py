from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.routes import camera
from app.management.middleware import log_request, protected_route
import sys
from os.path import abspath, dirname

sys.path.append(abspath(dirname(__file__)))

# Initialize Flask app
app = Flask(__name__)

jwt = JWTManager(app)
CORS(app, supports_credentials=True)

@app.before_request
def before_request(): 
    log_request(request)

@app.route("/protected", methods=["GET"])
@protected_route
def protected():
    return jsonify({"message": "You have access to this route!"}), 200

app.register_blueprint(camera.camera_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
