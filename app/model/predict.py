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