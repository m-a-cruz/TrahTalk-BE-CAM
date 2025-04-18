from flask import jsonify, Response
from bson import json_util
from app.management.config import database
from app.model.predict import forecast_prophet, generate_insights, store_predictions_and_actuals

def forecast_route():
    forecast = forecast_prophet()
    store_predictions_and_actuals(forecast)
    summary = generate_insights(forecast)
    
    return jsonify({"message": summary})

def fetch_insight():
    forecast = forecast_prophet()
    store_predictions_and_actuals(forecast)
    generate_insights(forecast)
    
    latest_insight = database.insight_collection.find_one({}, sort=[("timestamp", -1)])
    if latest_insight:
        response = Response(json_util.dumps(latest_insight), mimetype='application/json')
        return response, 200
    else:
        return {"error": "No insight available."}, 404
    
    