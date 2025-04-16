# from prophet import Prophet
# from pymongo import MongoClient
# import pandas as pd
# import datetime
# import os
# import math, numbers

# # Step 1: MongoDB setup
# client = MongoClient(os.environ.get("MONGO_URI"))
# db = client[os.environ.get("DB_CLIENT")]

# collection = db[os.environ.get("GAS_RECORDS")]                # actual source
# prediction_collection = db[os.environ.get("PREDICTION_COLLECTION")]  # optional if still storing separately
# combined_collection = db["gas_trends"]                        # final chart data

# # Step 2: Load data from gas_records
# cursor = collection.find({})
# raw_data = []

# for doc in cursor:
#     row = {
#         "timestamp": doc["timestamp"],
#         "LPG": doc["data"].get("LEL_LPG"),
#         "methane": doc["data"].get("LEL_methane"),
#         "smoke": doc["data"].get("LEL_smoke"),
#         "CO": doc["data"].get("LEL_CO"),
#         "hydrogen": doc["data"].get("LEL_hydrogen")
#     }
#     raw_data.append(row)

# df = pd.DataFrame(raw_data)
# df["timestamp"] = pd.to_datetime(df["timestamp"])
# df = df.sort_values("timestamp")

# # Step 3: Store actual values in common format
# gas_types = ["LPG", "methane", "smoke", "CO", "hydrogen"]
# actual_docs = []

# for _, row in df.iterrows():
#     for gas in gas_types:
#         val = row.get(gas)
#         if isinstance(val, numbers.Number) and not math.isnan(val):
#             actual_docs.append({
#                 "timestamp": row["timestamp"],
#                 "predicted_value": round(val, 2),
#                 "gas_type": gas,
#                 "type": "actual"
#             })

# # Step 4: Train and predict for each gas
# forecast_hours = 12
# prediction_docs = []

# for gas in gas_types:
#     gas_df = df[["timestamp", gas]].dropna()
#     gas_df = gas_df.rename(columns={"timestamp": "ds", gas: "y"})

#     if len(gas_df) < 10:
#         continue

#     model = Prophet()
#     model.fit(gas_df)

#     future = model.make_future_dataframe(periods=forecast_hours, freq="H")
#     forecast = model.predict(future)

#     predictions = forecast[["ds", "yhat"]].tail(forecast_hours)

#     for _, row in predictions.iterrows():
#         prediction_docs.append({
#             "timestamp": row["ds"],
#             "predicted_value": round(row["yhat"], 2),
#             "gas_type": gas,
#             "type": "predicted"
#         })

# # Step 5: Combine and insert

# print()
# print(prediction_docs)
# combined_collection.delete_many({})
# combined_collection.insert_many(actual_docs + prediction_docs)

# print("✅ Combined actual and predicted values inserted into gas_trends.")

# import pickle

# filename = 'prophet_model.pkl'
# with open(filename, 'wb') as file:
#     pickle.dump(model, file)

# print(f"Model saved to {filename}")


# import pickle
# import pandas as pd
# import matplotlib.pyplot as plt
# from app.management.config import database


# # Load the saved model
# with open("prophet_model.pkl", "rb") as file:
#     model = pickle.load(file)

# cursor = database.gas_collection.find({})
# docs = list(cursor)

# data = pd.DataFrame([{
#     "ds": doc["timestamp"],
#     "y": doc["data"].get("LEL_LPG")
# } for doc in docs])

# data.dropna(subset=["y"], inplace=True)
# data["ds"] = pd.to_datetime(data["ds"])
# data = data.sort_values("ds")

# model.history = data
# future = model.make_future_dataframe(periods=12, freq="H")

# forcast = model.predict(future)
# future_predictions = forcast.tail(12)[["ds", "yhat"]]
# print(future_predictions)



from prophet import Prophet
import pandas as pd
import math, numbers
from app.management.config import database
import pickle
import datetime


# Fetch the latest data
def get_latest_data():
    data = list(database.gas_collection.find({}))
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')
    return df[['timestamp', 'value']].rename(columns={'timestamp': 'ds', 'value': 'y'})


def train_prophet():
    # Step 1: Load data from gas_records
    cursor = get_latest_data()
    raw_data = []

    for doc in cursor:
        row = {
            "timestamp": doc["timestamp"],
            "LPG": doc["data"].get("LEL_LPG"),
            "methane": doc["data"].get("LEL_methane"),
            "smoke": doc["data"].get("LEL_smoke"),
            "CO": doc["data"].get("LEL_CO"),
            "hydrogen": doc["data"].get("LEL_hydrogen")
        }
        raw_data.append(row)

    df = pd.DataFrame(raw_data)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")

    # Step 2: Calculate average gas level for each timestamp
    gas_types = ["LPG", "methane", "smoke", "CO", "hydrogen"]
    df["average_gas_level"] = df[gas_types].mean(axis=1, skipna=True)

    # Filter out rows where the average is NaN
    df = df.dropna(subset=["average_gas_level"])

    # Rename columns for Prophet compatibility
    df = df.rename(columns={"timestamp": "ds", "average_gas_level": "y"})

    # Step 3: Train a new model
    model = Prophet()
    model.fit(df)
    print("Trained a new model for average gas levels")

    # Save the latest model to MongoDB with a timestamp
    database.prediction_models_collection.insert_one({
        "model_type": "average_gas",
        "timestamp": datetime.now(),
        "model": pickle.dumps(model)
    })
    print("Saved the latest model for average gas levels in MongoDB")

    # Step 4: Load the latest model from MongoDB
    latest_model_doc = database.prediction_models_collection.find_one(
        {"model_type": "average_gas"},
        sort=[("timestamp", -1)]  # Get the latest model based on timestamp
    )
    latest_model = pickle.loads(latest_model_doc["model"])
    print("Loaded the latest trained model for average gas levels")

    # Step 5: Make future predictions using the latest model
    forecast_hours = 12
    future = latest_model.make_future_dataframe(periods=forecast_hours, freq="H")
    forecast = latest_model.predict(future)

    # Extract predictions
    prediction_docs = []
    predictions = forecast[["ds", "yhat"]].tail(forecast_hours)

    for _, row in predictions.iterrows():
        prediction_docs.append({
            "timestamp": row["ds"],
            "predicted_value": round(row["yhat"], 2),
            "type": "predicted"
        })

    # Step 6: Insert actual and predicted values into gas_trends_collection
    actual_docs = []
    for _, row in df.iterrows():
        if isinstance(row["y"], numbers.Number) and not math.isnan(row["y"]):
            actual_docs.append({
                "timestamp": row["ds"],
                "predicted_value": round(row["y"], 2),
                "type": "actual"
            })

    database.gas_trends_collection.delete_many({})
    database.gas_trends_collection.insert_many(actual_docs + prediction_docs)

    print("✅ Combined actual and predicted values inserted into gas_trends.")
    return "Gas data trained, saved, and stored successfully!", 200

