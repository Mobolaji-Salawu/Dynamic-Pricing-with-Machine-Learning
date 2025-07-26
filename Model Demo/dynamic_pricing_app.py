from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pickle
import pandas as pd

# Initialize FastAPI app
app = FastAPI(title="Ride Hail Dynamic Pricing API", version="1.0")

# Load your trained pipeline model
with open("dynamic_pricing_pipeline.pkl", "rb") as f:
    pipeline = pickle.load(f)

# Function to classify booking time from hour
def classify_booking_time(hour: int) -> str:
    if 6 <= hour <= 12:
        return "Morning"
    elif 13 <= hour <= 17:
        return "Afternoon"
    elif 18 <= hour <= 21:
        return "Evening"
    else:
        return "Night"

# Define input data schema
class RideRequest(BaseModel):
    trips_this_hour: int
    trip_distance_km: float
    hour: int
    day: str
    vehicle_type: str

# Health check endpoint
@app.get("/")
def read_root():
    return {"message": "Ride Hail Dynamic Pricing API is live!"}

# Prediction endpoint
@app.post("/predict_fare")
def predict_fare(request: RideRequest):
    try:
        # Generate booking_time from hour
        booking_time = classify_booking_time(request.hour)

        # Construct DataFrame for model
        input_df = pd.DataFrame([{
            "trips_this_hour": request.trips_this_hour,
            "trip_distance_km": request.trip_distance_km,
            "hour": request.hour,
            "day": request.day,
            "vehicle_type": request.vehicle_type,
            "booking_time": booking_time
        }])

        # Predict fare
        predicted_fare = float(pipeline.predict(input_df)[0])

        # Return result
        return {
            "predicted_fare": round(predicted_fare, 2),
            "inputs": input_df.to_dict(orient="records")[0]
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))