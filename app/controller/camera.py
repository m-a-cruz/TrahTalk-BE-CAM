import cv2
import numpy as np
import base64
import datetime
from flask import request, jsonify, Response
from app.management.config import database
from bson import json_util, ObjectId
from ultralytics import YOLO
import logging

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('pymongo').setLevel(logging.WARNING)
logging.info("App started")

# Load your YOLO model once (outside the function)
model = YOLO("app/model/my_model.pt")

def upload_image():
    logging.info("Content-Type: %s", request.content_type)
    logging.info("Request data length: %d", len(request.data))
    logging.info("Files: %s", request.files)

    try:
        content_type = request.content_type
        img_bytes = None

        if content_type.startswith('multipart/form-data'):
            if 'image' not in request.files:
                return jsonify({'error': 'No image file provided in form-data'}), 400
            file = request.files['image']
            img_bytes = file.read()  # Read image stream directly

        elif content_type in ['application/octet-stream', 'image/jpeg', 'image/jpg']:
            if not request.data:
                return jsonify({'error': 'No image data provided'}), 400
            img_bytes = request.data  # Use the raw stream directly
        else:
            return jsonify({'error': f'Unsupported content type: {content_type}'}), 400

        # Convert bytes to image (no need to save to disk)
        img = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)

        if img is None:
            logging.error("Failed to decode image")
            return jsonify({'error': 'Failed to decode image'}), 400
        
        # Resize the image to fit YOLO model input size (adjust if needed)
        img = cv2.resize(img, (224, 224))  # Resizing to a square shape if needed

        # Run inference
        results = model(img)

        detections = []
        for box in results[0].boxes:
            cls_id = int(box.cls[0].item())
            conf = float(box.conf[0].item())
            name = results[0].names[cls_id]
            detections.append({
                "class_id": cls_id,
                "class_name": name,
                "confidence": round(conf, 3)
            })

        # Plot bounding boxes and annotations
        annotated_img = results[0].plot()
        _, raw_buffer = cv2.imencode('.jpg', img)
        _, ann_buffer = cv2.imencode('.jpg', annotated_img)

        # Encode images to base64
        raw_encoded = base64.b64encode(raw_buffer).decode('utf-8')
        annotated_encoded = base64.b64encode(ann_buffer).decode('utf-8')

        # Store in the database
        database.image_collection.insert_one({
            "timestamp": datetime.datetime.utcnow(),
            "detected_objects": detections,
            "image_raw_base64": raw_encoded,
            "image_annotated_base64": annotated_encoded,
            "type": "inference",
        })

        return jsonify({
            "message": "Image received and processed",
            "detections": detections
        }), 200

    except Exception as e:
        # Log the exception for debugging purposes
        logging.error("Error processing image: %s", str(e))
        return jsonify({'error': str(e)}), 500
