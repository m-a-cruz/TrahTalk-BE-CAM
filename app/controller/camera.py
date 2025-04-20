import cv2
import numpy as np
import base64
import datetime
from flask import request, jsonify, Response
from app.management.config import database
from bson import json_util, ObjectId
from ultralytics import YOLO


# Load your YOLO model once (outside the function)
model = YOLO("app/model/my_model.pt")

def upload_image():
    print("Content-Type:", request.content_type)
    print("Request data length:", len(request.data))
    print("Files:", request.files)

    try:
        content_type = request.content_type
        img_bytes = None

        if content_type.startswith('multipart/form-data'):
            if 'image' not in request.files:
                return jsonify({'error': 'No image file provided in form-data'}), 400
            file = request.files['image']
            img_bytes = np.frombuffer(file.read(), np.uint8)

        elif content_type in ['application/octet-stream', 'image/jpeg', 'image/jpg']:
            if not request.data:
                return jsonify({'error': 'No image data provided'}), 400
            img_bytes = np.frombuffer(request.data, np.uint8)
        else:
            return jsonify({'error': f'Unsupported content type: {content_type}'}), 400

        # Save for debugging
        with open("debug_upload.jpg", "wb") as f:
            f.write(img_bytes)

        img = cv2.imdecode(img_bytes, cv2.IMREAD_COLOR)

        if img is None:
            return jsonify({'error': 'Failed to decode image'}), 400
        
        img = cv2.resize(img, (640, 480)) 

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

        annotated_img = results[0].plot()
        _, raw_buffer = cv2.imencode('.jpg', img)
        _, ann_buffer = cv2.imencode('.jpg', annotated_img)

        raw_encoded = base64.b64encode(raw_buffer).decode('utf-8')
        annotated_encoded = base64.b64encode(ann_buffer).decode('utf-8')

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
        return jsonify({'error': str(e)}), 500