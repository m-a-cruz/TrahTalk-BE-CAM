from flask import jsonify,Response, request
from bson import json_util, ObjectId
from app.management.config import database
import datetime

def fetch_notif():
    notification = list(database.notification_collection.find().sort("timestamp", -1))
    response = Response(json_util.dumps(notification), mimetype='application/json')
    return response, 200

def record_notif_data():
    data = request.json
    notification = {"timestamp": datetime.datetime.utcnow(),"data": data, }
    database.notification_collection.insert_one(notification)
    return jsonify({"message": "Notification recorded successfully"}), 201

def update_notif_data():
    data = request.json
    query = {"_id": ObjectId(data["id"])}
    notification = {"$set": {"status": data["status"]}, "$currentDate": {"lastModified": True}}
    database.notification_collection.update_one(query, notification)
    return jsonify({"message": "Notification updated successfully"}), 201
