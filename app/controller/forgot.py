from flask import request, jsonify
from app.management.config import database
import app.management.config as config
import app.management.encryption as encrypt
import datetime
from flask_mail import Message,Mail
import os, re
import logging
import app.management.middleware as middleware

# Configure logging
logging.basicConfig(level=logging.INFO)

# Dictionary to store reset tokens and their expiry
reset_token = {}

def forgot_password():
    from main import app, mail
    data = request.json
    required_keys = ["email"]
    user = database.users_collection.find_one({"email": data["email"]})
    
    if middleware.validate_request_keys(data, required_keys):
        return middleware.validate_request_keys(data, required_keys)
    
    if not user: return jsonify({"error": "User not found"}), 404
    
    # Generate reset token and expiry time
    token = config.generate_reset_token()
    expiry_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
    reset_token[data["email"]] = {"token": token, "expiry": expiry_time}
    
    # Email details
    recipient_email = data["email"]
    subject = "Request for Password Reset - Security Code"
    message_body = (
        f"Please use the following code to reset your password.Note that this code is valid for 5 minutes:\n\n"
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

def reset_password():
    data = request.json
    required_keys = ["email","code", "newPassword", "confirmPassword"]
    
    if data["code"] != reset_token[data["email"]]["token"]: return jsonify({"error": "Invalid or expired reset token"}), 400
    
    if middleware.validate_request_keys(data, required_keys) == None: print(reset_token[data["email"]])
    else: return middleware.validate_request_keys(data, required_keys)
    
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
