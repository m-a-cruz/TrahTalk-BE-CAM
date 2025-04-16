import pandas as pd
from datetime import datetime
from prophet import Prophet
from app.management.config import database
import pickle


def retrain_and_predict():
    print("🔁 Running retrain_and_predict:", datetime.now())

    # Load latest data
    cursor = collection.find({})
    docs = list(cursor)
    df = pd.DataFrame([{
        "ds": doc["timestamp"],
        "y": doc["data"].get("LEL_LPG")  # Adjust to your actual gas type
    } for doc in docs if doc["data"].get("LEL_LPG") is not None])

    df["ds"] = pd.to_datetime(df["ds"])
    df = df.sort_values("ds")

    # Retrain model
    model = Prophet()
    model.fit(df)

    # Forecast next 2 hours
    future = model.make_future_dataframe(periods=2, freq="H")
    forecast = model.predict(future)
    predictions = forecast.tail(2)[["ds", "yhat"]]

    # Store predictions
    prediction_docs = [{
        "timestamp": row["ds"],
        "predicted_value": row["yhat"]
    } for _, row in predictions.iterrows()]
    
    prediction_collection.insert_many(prediction_docs)
    print("✅ Predictions inserted.")