from flask import jsonify,Response, request
from bson import json_util
from app.management.config import database
import datetime

def record_gas_level():
    data = request.json
    record = {"timestamp": datetime.datetime.utcnow(),"data": data, }
    database.gas_collection.insert_one(record)
    return jsonify({"message": "Gas data recorded successfully"}), 201

def fetch_gas_chart():
    gas_chart = list(database.chart_collection.find())
    response = Response(json_util.dumps(gas_chart), mimetype='application/json')
    return response, 200
