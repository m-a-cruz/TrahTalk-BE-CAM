from flask import request, jsonify, make_response
import datetime
from app.management.config import database
import app.management.encryption as encrypt
from flask_jwt_extended import create_access_token
import app.management.middleware as middleware

def register():
    data = request.json
    required_keys = ["name", "email", "password", "confirmPassword", "accessCode"]
    
    if middleware.validate_request_keys(data, required_keys): return middleware.validate_request_keys(data, required_keys)
    if database.users_collection.find_one({"email": data["email"]}): return jsonify({"error": "User already exists"}), 400
    
    user = {"name": data["name"], "email":data["email"], 
            "password": encrypt.hash_password(data["password"]), "created_at": datetime.datetime.utcnow()}
    database.users_collection.insert_one(user)
    return jsonify({"message": "User registered successfully"}), 200

def login():
    data = request.json
    required_keys = ["email", "password"]
    user = database.users_collection.find_one({"email": data["email"]})
    
    if middleware.validate_request_keys(data, required_keys): return middleware.validate_request_keys(data, required_keys)
    if not user: return jsonify({"error": "User does not exists"}), 400
    if not user or not encrypt.check_password(user["password"], data["password"]): return jsonify({"error": "Invalid credentials"}), 401
    
    token = create_access_token(identity=data["email"], expires_delta=datetime.timedelta(hours=3))

    response = make_response(jsonify({"message": "Login successful"}))
    response.set_cookie(
        "access_token_cookie",
        token,
        secure=True,  # Use True for HTTPS in production
        httponly=True,  # Prevent access via JavaScript
        samesite="None",  # Adjust based on your use case, e.g., "None" for cross-origin
        max_age=3 * 60 * 60  # Cookie expires after 3 hours
    )
    return response

def logout():
    response = make_response(jsonify({"message": "Logout successful"}))
    response.set_cookie(
        "access_token_cookie", 
        "", 
        expires=0, 
        path="/", 
        httponly=True, 
        samesite="None", 
        secure=True
    )
    return response
