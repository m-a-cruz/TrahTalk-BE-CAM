from flask import request, jsonify
from management.database import database
import management.reset as reset
import management.encryptpassword as encrypt
import datetime

reset_token = {}
def forgot_password():
    data = request.json
    
    if not data or "email" not in data:
        return jsonify({"error": "Email is required"}), 400
    
    if not database.users_collection.find_one({"email": data["email"]}):
        return jsonify({"error": "User not found"}), 404
    
    reset_token[data["email"]] = reset.generate_reset_token()
    
    # Put the code for sending the reset token to the user's email
    
    return jsonify({"token": reset_token, "message": "Password reset token sent!"}), 200
    
def reset_password():
    data = request.json
    
    data = request.json
    if not data or not all(key in data for key in ["email", "reset_token", "new_password"]):
        return jsonify({"error": "Missing required fields"}), 400

    if data["email"] not in reset_token or reset_token[data["email"]] != data["reset_token"]:
        return jsonify({"error": "Invalid or expired reset token"}), 400

    if len(data["new_password"]) < 6:
        return jsonify({"error": "Password must be at least 6 characters long"}), 400
    
    database.users_collection.update_one({"email": data["email"]}, {"$set": {"password": encrypt.hash_password(data["new_password"])}})
    del reset_token[data["email"]]
    
    database.notification_collection.insert_one({"message": "Password reset successfully", "type": "Info", "status": "Unread", "timestamp": datetime.datetime.utcnow()})
    
    return jsonify({"message": "Password reset successfully"}), 200
    