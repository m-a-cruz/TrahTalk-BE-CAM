from flask import request, jsonify
from management.database import database
import management.reset as reset
import management.encryptpassword as encrypt
from management.cipherprivatekey import CiperPrivateKey
import datetime
from flask_mail import Message,Mail
import os, re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Dictionary to store reset tokens and their expiry
reset_token = {}

def forgot_password():
    
    data = request.json

    from main import app, mail
    
    # Validate input data
    if not data or "email" not in data:
        return jsonify({"error": "Email is required"}), 400
    
    user = database.users_collection.find_one({"email": data["email"]})
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Generate reset token and expiry time
    token = reset.generate_reset_token()
    expiry_time = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    reset_token[data["email"]] = {"token": token, "expiry": expiry_time}
    
    # Email details
    recipient_email = data["email"]
    subject = "Request for Password Reset - Security Code"
    message_body = (
        f"Please use the following code to reset your password:\n\n"
        f"Security Code: {token}\n\n"
        "Only enter this code on an official website or app. Don't share it with anyone.\n"
        "We'll never ask for it outside an official platform.\n\n"
        "Thank you for using our service.\n\n"
        "Sincerely,\nBin There Done That Team"
    )
    
    msg = Message(subject, sender=app.config['MAIL_USERNAME'], recipients=[recipient_email])
    msg.body = message_body
    
    try:
        mail.send(msg)
        logging.info(f"Password reset token sent to {recipient_email}")
        return jsonify({"message": "Password reset token sent to your email!"}), 200
    except Exception as e:
        logging.error(f"Failed to send email: {str(e)}")
        return jsonify({"error": "Failed to send email", "details": str(e)}), 500

def security_code_verification():
    data = request.json
    
    # Validate input data
    if not data or not all(key in data for key in ["email", "code"]):
        return jsonify({"error": "Email and reset token are required"}), 400
    
    token_data = reset_token.get(data["email"])
    if not token_data:
        return jsonify({"error": "Invalid or expired reset token"}), 400
    
    # Check token validity and expiry
    if token_data["token"] != data["code"] or token_data["expiry"] < datetime.datetime.utcnow():
        return jsonify({"error": "Invalid or expired reset token"}), 400
    
    return jsonify({"message": "Reset token verified successfully"}), 200

def reset_password():
    data = request.json
    
    # Validate input data
    if not data or not all(key in data for key in ["email", "newPassword", "confirmPassword"]):
        return jsonify({"error": "Missing required fields"}), 400
    
    password_regex = r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$'
    
    if not re.match(password_regex, data["newPassword"]):
        return jsonify({"error": "Password must be at least 8 characters long and include both letters and numbers"}), 400
    
    if data["newPassword"] != data["confirmPassword"]:
        return jsonify({"error": "Passwords do not match"}), 400  
    
    # Update user's password
    database.users_collection.update_one(
        {"email": data["email"]},
        {"$set": {"password": encrypt.hash_password(data["newPassword"])}}
    )
    del reset_token[data["email"]]
    
    # Log password reset notification
    database.notification_collection.insert_one({
        "message": "Password reset successfully",
        "type": "Info",
        "status": "Unread",
        "timestamp": datetime.datetime.utcnow()
    })
    
    logging.info(f"Password reset successfully for {data['email']}")
    return jsonify({"message": "Password reset successfully"}), 200
