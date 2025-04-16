import cv2
import numpy as np
import base64
import datetime
from flask import request, jsonify, Response
from app.management.config import database
from bson import json_util, ObjectId


def upload_image():
    if not request.data:
        return jsonify({'error': 'No image data received'}), 400

    try:
        img_bytes = np.frombuffer(request.data, np.uint8)
        img = cv2.imdecode(img_bytes, cv2.IMREAD_COLOR)

        if img is None:
            return jsonify({'error': 'Failed to decode image'}), 400

        # Process...
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, buffer = cv2.imencode('.jpg', gray)
        encoded_image = base64.b64encode(buffer).decode('utf-8')

        database.image_collection.insert_one({
            "timestamp": datetime.datetime.utcnow(),
            "image_data": encoded_image,
            "description": "grayscale",
            "type": "raw",
        })

        return jsonify({"message": "Raw image received and stored"}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    

def view_latest_image():
    image = database.image_collection.find_one(sort=[("timestamp", -1)])
    if not image:
        return "No image found", 404
    
    response = Response(json_util.dumps(image), mimetype='application/json')

    # img_data = base64.b64decode(doc["image_data"])
    return response, 200