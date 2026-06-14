# Placeholder: Python script to validate IoT payload before sending.
import firebase_admin
from firebase_admin import credentials,db
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from firebase.client import get_db  # Import the get_db function from the local module

credential_path = "key_firebase_HeThongNhiet.json"
initialize_app = firebase_admin.initialize_app(credentials.Certificate(credential_path), {
    'databaseURL': 'https://hethongcambiennhiet-default-rtdb.asia-southeast1.firebasedatabase.app/'
})
app=FastAPI()

class SensorData(BaseModel):
    sensor_id: str
    temperature: float
    humidity: float
    timestamp: str
    
@app.post("/validate_payload")
async def validate_payload(data: SensorData):
    # Validate sensor_id
    if not data.sensor_id:
        raise HTTPException(status_code=400, detail="sensor_id is required.")
    
    # Validate temperature
    if not (-50 <= data.temperature <= 60):
        raise HTTPException(status_code=400, detail="temperature must be between -50 and 60.")
    
    # Validate humidity
    if not (0 <= data.humidity <= 100):
        raise HTTPException(status_code=400, detail="humidity must be between 0 and 100.")
    
    # Validate timestamp
    try:
        datetime.strptime(data.timestamp, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        raise HTTPException(status_code=400, detail="timestamp must be in ISO 8601 format (YYYY-MM-DDTHH:MM:SS).")

    # Check for forceMeasure flag
    try:
        db = get_db()
        force_measure = db.reference(f"settings/{data.sensor_id}/forceMeasure").get()
        # Usually ESP32 uses 1 as True for the flag
        if force_measure == 1 or force_measure is True:
            # Set back to 0 to prevent re-triggering
            db.reference(f"settings/{data.sensor_id}/forceMeasure").set(0)
            print(f"[payload_check] Force measure detected for {data.sensor_id}, setting flag to 0")
    except Exception as e:
        print(f"[payload_check] Error handling forceMeasure: {e}")

    # Save sensor data
    db.reference(f'sensor_data/{data.sensor_id}').push(data.model_dump())
    
    return {"message": "Payload is valid.", "forceMeasure": bool(force_measure)}
