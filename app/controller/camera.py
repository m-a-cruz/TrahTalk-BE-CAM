import cv2
import numpy as np
import base64
import datetime
from flask import request, jsonify, Response
from app.management.config import database

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 5 * 1024 * 1024
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']

    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400

    try:
        # Read image file directly
        img_bytes = np.frombuffer(file.read(), np.uint8)
        img = cv2.imdecode(img_bytes, cv2.IMREAD_COLOR)

        if img is None:
            return jsonify({'error': 'Failed to decode image'}), 400

        # Process: convert to grayscale (example)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Encode processed image to base64
        _, buffer = cv2.imencode('.jpg', gray)
        encoded_image = base64.b64encode(buffer).decode('utf-8')

        # Insert into MongoDB
        database.image_collection.insert_one({
            "timestamp": datetime.datetime.utcnow(),
            "image_data": encoded_image,
            "description": "grayscale",
        })

        return jsonify({"message": "Image received and stored"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    

def view_latest_image():
    doc = database.image_collection.find_one(sort=[("timestamp", -1)])
    if not doc:
        return "No image found", 404

    img_data = base64.b64decode(doc["image_data"])
    return Response(img_data, mimetype='image/jpeg')