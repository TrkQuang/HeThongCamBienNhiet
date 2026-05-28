# Placeholder: Python script to validate IoT payload before sending.
import firebase_admin
from firebase_admin import credentials,db
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime


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
    
    db.reference('sensor_data').push(data.model_dump())
    
    return {"message": "Payload is valid."}
