from prophet import Prophet
import pandas as pd
import math, numbers
from app.management.config import database
import pickle
import datetime


def get_data():
    
    # Step 1: Fetch data from MongoDB
    data = list(database.gas_collection.find({}))
    
    raw_data = []

    for doc in data:
        try:
            row = {
                "timestamp": doc["timestamp"],
                "LPG": doc["data"].get("LEL_LPG"),
                "methane": doc["data"].get("LEL_methane"),
                "smoke": doc["data"].get("LEL_smoke"),
                "CO": doc["data"].get("LEL_CO"),
                "hydrogen": doc["data"].get("LEL_hydrogen")
            }
            raw_data.append(row)
        except (KeyError, TypeError) as e:
            print(f"⚠️ Skipped a document due to missing fields: {e}")
            continue
        
    df = pd.DataFrame(raw_data)
            
    if df.empty:
        print("⚠️ No valid data found to train the model.")
        return

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")

    # Step 2: Compute average gas level
    gas_types = ["LPG", "methane", "smoke", "CO", "hydrogen"]
    df["average_gas_level"] = df[gas_types].mean(axis=1, skipna=True)
    df = df.dropna(subset=["average_gas_level"])
    df = df.rename(columns={"timestamp": "ds", "average_gas_level": "y"})
    return df

# Fetch the latest data
def train_prophet():
    df = get_data()

    # Step 3: Train the Prophet model
    model = Prophet()
    model.fit(df)

    # Step 4: Save model to MongoDB
    database.prediction_models_collection.insert_one({
        "model_type": "average_gas",
        "timestamp": datetime.datetime.now(),
        "model": pickle.dumps(model)
    })

    print("✅ Model trained and saved.")

def forecast_prophet(forecast_hours=12):
    latest_model_doc = database.prediction_models_collection.find_one(
        {"model_type": "average_gas"},
        sort=[("timestamp", -1)]
    )

    if not latest_model_doc:
        raise Exception("No trained model found in the database.")

    model = pickle.loads(latest_model_doc["model"])

    # Create future dataframe and forecast
    future = model.make_future_dataframe(periods=forecast_hours, freq="h")
    forecast = model.predict(future)
    
    forecast = pd.DataFrame(forecast)

    return forecast

# Format timestamp for frontend
def format_timestamp_for_frontend(timestamp):
    return timestamp.strftime('%Y-%m-%d %H:%M')

# Extract insights from forecast data
def generate_insights(forecast):
    forecast_values = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
    forecast_values['ds'] = pd.to_datetime(forecast_values['ds'])

    # Calculate the overall trend
    start_value = forecast_values['yhat'].iloc[0]
    end_value = forecast_values['yhat'].iloc[-1]
    trend = "increasing" if end_value > start_value else "decreasing"

    # Insights for the last 5 predictions
    latest_predictions = forecast_values.tail(5)
    insights = []

    for index, row in latest_predictions.iterrows():
        date = format_timestamp_for_frontend(row['ds'])
        predicted_value = row['yhat']
        lower_bound = row['yhat_lower']
        upper_bound = row['yhat_upper']
        insight = f"On {date}, the predicted value is {predicted_value:.2f}. The forecasted range is between {lower_bound:.2f} and {upper_bound:.2f}."
        insights.append(insight)

    # Summary of the trend
    summary = f"The overall trend of the data is {trend}. The most recent forecasted values are as follows:\n"
    summary += "\n".join(insights)

    # Store insights in MongoDB
    database.insight_collection.insert_one({
        "timestamp": datetime.datetime.now(),
        "trend": trend,
        "insights": insights,
        "summary": summary
    })

    return "Insights Successfully Recorded!", 200

# Store both predicted and actual values in MongoDB

def store_predictions_and_actuals(forecast):
    prediction_docs = []
    actual_docs = []
    df = get_data()

    # Step 1: Collect the predicted values (from the forecast DataFrame)
    for _, row in forecast.iterrows():
        timestamp = row['ds']
        predicted_value = round(row['yhat'], 2)
        predicted_lower = round(row['yhat_lower'], 2)
        predicted_upper = round(row['yhat_upper'], 2)

        prediction_docs.append({
            "timestamp": timestamp,
            "predicted_value": predicted_value,
            "predicted_lower": predicted_lower,
            "predicted_upper": predicted_upper,
            "type": "predicted"
        })

    # Step 2: Collect the actual values (from the original training data df)
    for _, row in df.iterrows():
        if isinstance(row["y"], numbers.Number) and not math.isnan(row["y"]):
            actual_docs.append({
                "timestamp": row["ds"],
                "predicted_value": round(row["y"], 2),
                "type": "actual"
            })

    # Step 3: Insert the actual and predicted values into gas_trends_collection
    database.gas_trends_collection.delete_many({})  # Optional: delete old data first
    database.gas_trends_collection.insert_many(actual_docs + prediction_docs)

# def store_predictions_and_actuals(forecast, df):
#     prediction_docs = []
#     actual_docs = []

#     # Step 1: Collect the predicted values (from the forecast DataFrame)
#     for _, row in forecast.iterrows():
#         timestamp = row['ds']
#         predicted_value = round(row['yhat'], 2)
#         predicted_lower = round(row['yhat_lower'], 2)
#         predicted_upper = round(row['yhat_upper'], 2)

#         prediction_docs.append({
#             "timestamp": timestamp,
#             "predicted_value": predicted_value,
#             "predicted_lower": predicted_lower,
#             "predicted_upper": predicted_upper,
#             "type": "predicted"
#         })

#     # Step 2: Collect the actual values (from the original training data df)
#     for _, row in df.iterrows():
#         if isinstance(row["y"], numbers.Number) and not math.isnan(row["y"]):
#             actual_docs.append({
#                 "timestamp": row["ds"],
#                 "predicted_value": round(row["y"], 2),
#                 "type": "actual"
#             })

#     # Step 3: Insert the actual and predicted values into gas_trends_collection
#     database.gas_trends_collection.delete_many({})  # Optional: delete old data first
#     database.gas_trends_collection.insert_many(actual_docs + prediction_docs)