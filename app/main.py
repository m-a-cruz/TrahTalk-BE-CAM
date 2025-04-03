from flask import Flask, jsonify, request
from flask_cors import CORS
from application.auth.urls import auth_bp
from application.forgot.urls import reset_bp
from application.gas.urls import gas_bp
from management.middleware import log_request,protected_route
from management.cipherprivatekey import SECRET_KEY
from flask_jwt_extended import  JWTManager, jwt_required, get_jwt_identity
# from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
# app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.config["JWT_SECRET_KEY"] = SECRET_KEY
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_ACCESS_COOKIE_NAME"] = "access_token_cookie"
app.config["JWT_COOKIE_CSRF_PROTECT"] = False
app.config["JWT_COOKIE_SECURE"] = False  # Set to True in production for HTTPS

jwt = JWTManager(app)
CORS(app, supports_credentials=True)

@app.before_request
def before_request(): log_request(request)

@app.route("/protected", methods=["GET"])
def protected(): 
    protected_route(request)
    return jsonify({"message": "You have access to this route!"}), 200
    
app.register_blueprint(auth_bp)
app.register_blueprint(reset_bp)
app.register_blueprint(gas_bp)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000,debug=True)
