from flask import request, jsonify
from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
import re
import app.management.config as config

def log_request(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = request.json if request.is_json else None
        print(f"[LOG] {request.method} {request.path} - Data: {data}")
        return f(*args, **kwargs)
    return decorated_function


def protected_route(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            identity = get_jwt_identity()
            print(f"Verified identity: {identity}")
            return f(*args, **kwargs) 
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": "Unauthorized"}), 401
    return decorated

def handle_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return wrapper

def validate_request_keys(data, required_keys):
    email_regex = r"[^@]+@[^@]+\.[^@]+"
    password_regex = r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$'
    
    try:
        if not data or not all(key in data for key in required_keys):
            return {"error": "Missing required fields"}, 400
    
        if "email" in data and not re.match(email_regex, data["email"]):
            return {"error": "Invalid email format"}, 400
        
        if 'password' in data and not re.match(password_regex, data["password"]):
            return {"error": "Password must be at least 8 characters long and include both letters and numbers"}, 400
                
        if 'newPassword' in data and not re.match(password_regex, data["newPassword"]):
            return {"error": "Password must be at least 8 characters long and include both letters and numbers"}, 400
        
        if 'confirmPassword' in data:
            if not re.match(password_regex, data["confirmPassword"]):
                return {"error": "Password must be at least 8 characters long and include both letters and numbers"}, 400
            
            if "password" in data and data["password"] != data["confirmPassword"]:
                return {"error": "Passwords do not match"}, 400
            
            if "newPassword" in data and data["newPassword"] != data["confirmPassword"]:
                return {"error": "Passwords do not match"}, 400
        
        if "accessCode" in data and data["accessCode"] != config.cipher.REGISTRATION_KEY:
            return {"error": "Invalid encryption key"}, 403
        
        return None
    except Exception as e:
        print(f"Error: {e}")
        return {"error": "Internal server error"}, 500

    
    