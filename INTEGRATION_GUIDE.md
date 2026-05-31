"""
Integration Guide: Connecting Modern Dashboard to Your API & Database

This guide shows how to integrate the dashboard_view_modern.py with your
existing Flask API and SQLAlchemy database.
"""

# ============================================================================

# EXAMPLE 1: Fetching Real Temperature Data from API

# ============================================================================

"""
Add this to dashboard_view_modern.py to fetch live data from your API:
"""

import requests
from datetime import datetime, timedelta

def fetch_temperature_data_from_api(self):
"""Fetch current temperature and humidity from your API"""
try: # Assuming your Flask API is running on localhost:5000
response = requests.get("http://localhost:5000/api/temperature/latest")

        if response.status_code == 200:
            data = response.json()
            self.current_temp = data.get('temperature', 30)
            self.humidity = data.get('humidity', 65)
            self.threshold = data.get('threshold', 35)

            # Update the display
            self.update_dashboard()
            return True
    except Exception as e:
        print(f"Error fetching data: {e}")
    return False

def fetch_hourly_trend_data(self):
"""Fetch hourly temperature trend data for the chart"""
try:
response = requests.get("http://localhost:5000/api/temperature/hourly")

        if response.status_code == 200:
            data = response.json()
            hours = [item['hour'] for item in data]
            temps = [item['temperature'] for item in data]

            # Update chart with real data
            self.update_chart_data(hours, temps)
            return True
    except Exception as e:
        print(f"Error fetching trend data: {e}")
    return False

def fetch_timeline_data(self):
"""Fetch temperature data for timeline"""
try:
response = requests.get("http://localhost:5000/api/temperature/timeline")

        if response.status_code == 200:
            data = response.json()
            return data  # List of {time, temperature} objects
    except Exception as e:
        print(f"Error fetching timeline data: {e}")
    return []

# ============================================================================

# EXAMPLE 2: Database Integration (Using SQLAlchemy)

# ============================================================================

"""
If you prefer direct database access instead of API, use this approach:
"""

from database.models import TemperatureReading
from database.db import SessionLocal
from datetime import datetime, timedelta
from sqlalchemy import desc

def fetch_from_database(self):
"""Fetch temperature data directly from database"""
db = SessionLocal()
try: # Get latest temperature reading
latest = db.query(TemperatureReading).order_by(
desc(TemperatureReading.timestamp)
).first()

        if latest:
            self.current_temp = latest.temperature
            self.humidity = latest.humidity
            self.threshold = 35  # From your settings or config

        # Get hourly data for the last 9 hours
        nine_hours_ago = datetime.now() - timedelta(hours=9)
        hourly_data = db.query(TemperatureReading).filter(
            TemperatureReading.timestamp >= nine_hours_ago
        ).order_by(TemperatureReading.timestamp).all()

        # Group by hour and average
        hourly_temps = {}
        for reading in hourly_data:
            hour_key = reading.timestamp.strftime('%H:00')
            if hour_key not in hourly_temps:
                hourly_temps[hour_key] = []
            hourly_temps[hour_key].append(reading.temperature)

        # Calculate averages
        hours = sorted(hourly_temps.keys())
        temps = [sum(hourly_temps[h]) / len(hourly_temps[h]) for h in hours]

        self.update_chart_data(hours, temps)

    finally:
        db.close()

# ============================================================================

# EXAMPLE 3: Real-Time Updates with Threading

# ============================================================================

"""
For live updates without blocking the UI, use threading:
"""

import threading
import time

class TemperatureDashboardWithLiveUpdates(TemperatureDashboard):
"""Enhanced dashboard with live data updates"""

    def __init__(self, root):
        super().__init__(root)

        # Start background update thread
        self.update_thread = threading.Thread(target=self._background_update, daemon=True)
        self.update_thread.start()

        # Schedule periodic updates
        self.schedule_updates()

    def schedule_updates(self):
        """Schedule periodic data refresh"""
        self.fetch_temperature_data_from_api()
        # Refresh every 5 seconds
        self.root.after(5000, self.schedule_updates)

    def _background_update(self):
        """Run background updates in separate thread"""
        while True:
            try:
                self.fetch_hourly_trend_data()
                time.sleep(30)  # Update trends every 30 seconds
            except Exception as e:
                print(f"Background update error: {e}")
                time.sleep(30)

# ============================================================================

# EXAMPLE 4: API Routes to Support Dashboard (in your routes.py)

# ============================================================================

"""
Add these routes to api/routes.py to support the dashboard:
"""

from flask import Blueprint, jsonify
from database.models import TemperatureReading
from database.db import SessionLocal
from sqlalchemy import desc
from datetime import datetime, timedelta

api_bp = Blueprint('dashboard_api', **name**, url_prefix='/api')

@api_bp.route('/temperature/latest', methods=['GET'])
def get_latest_temperature():
"""Get the latest temperature reading"""
db = SessionLocal()
try:
reading = db.query(TemperatureReading).order_by(
desc(TemperatureReading.timestamp)
).first()

        if reading:
            return jsonify({
                'temperature': reading.temperature,
                'humidity': reading.humidity,
                'threshold': 35,  # From your alert rules
                'timestamp': reading.timestamp.isoformat()
            })
        return jsonify({'error': 'No data available'}), 404
    finally:
        db.close()

@api_bp.route('/temperature/hourly', methods=['GET'])
def get_hourly_temperature():
"""Get hourly temperature averages for the last 9 hours"""
db = SessionLocal()
try:
nine_hours_ago = datetime.now() - timedelta(hours=9)

        readings = db.query(TemperatureReading).filter(
            TemperatureReading.timestamp >= nine_hours_ago
        ).order_by(TemperatureReading.timestamp).all()

        # Group by hour
        hourly = {}
        for reading in readings:
            hour_key = reading.timestamp.strftime('%H:00')
            if hour_key not in hourly:
                hourly[hour_key] = []
            hourly[hour_key].append(reading.temperature)

        # Calculate averages
        result = [
            {
                'hour': hour,
                'temperature': sum(temps) / len(temps)
            }
            for hour, temps in sorted(hourly.items())
        ]

        return jsonify(result)
    finally:
        db.close()

@api_bp.route('/temperature/timeline', methods=['GET'])
def get_temperature_timeline():
"""Get temperature readings for timeline (key times of day)"""
db = SessionLocal()
try:
today = datetime.now().date()

        # Define key times: 09:00, 12:00, 15:00, 18:00, 21:00, 24:00
        key_times = ['09:00', '12:00', '15:00', '18:00', '21:00', '24:00']
        result = []

        for time_str in key_times:
            hour, minute = map(int, time_str.split(':'))

            # Find closest reading to this time
            start = datetime.combine(today, datetime.min.time()).replace(hour=hour, minute=minute)
            end = start + timedelta(hours=1)

            reading = db.query(TemperatureReading).filter(
                TemperatureReading.timestamp >= start,
                TemperatureReading.timestamp < end
            ).order_by(desc(TemperatureReading.timestamp)).first()

            if reading:
                result.append({
                    'time': time_str,
                    'temperature': reading.temperature
                })

        return jsonify(result)
    finally:
        db.close()

# ============================================================================

# EXAMPLE 5: Navigation Button Integration

# ============================================================================

"""
Wire up navigation buttons in the dashboard to load different views:
"""

def on_nav_click(self, label):
"""Handle navigation button click""" # Update button styles
for btn_label, btn in self.nav_buttons.items():
if btn_label == label:
btn.configure(fg_color=COLOR_PRIMARY, text_color="white")
else:
btn.configure(fg_color="transparent", text_color=COLOR_PRIMARY)

    # Navigate to different views
    if label == "Dashboard":
        print("Show dashboard content")
        # Already visible, just make sure it's displayed

    elif label == "Alerts":
        print("Show alerts view")
        # Load alerts from your core.alert_rules
        self.show_alerts_view()

    elif label == "Settings":
        print("Show settings view")
        # Load settings from your config.settings.yaml
        self.show_settings_view()

def show_alerts_view(self):
"""Replace dashboard content with alerts""" # Implementation would hide current content and show alerts
pass

def show_settings_view(self):
"""Replace dashboard content with settings""" # Implementation would hide current content and show settings
pass

# ============================================================================

# EXAMPLE 6: Complete Integration in main.py

# ============================================================================

"""
Example of how to use the dashboard in your main application:
"""

from app.dashboard_view_modern import TemperatureDashboard
from api.app import create_app
import threading
import customtkinter as ctk

def main(): # Start Flask API in background
api_thread = threading.Thread(target=lambda: create_app().run(debug=False), daemon=True)
api_thread.start()

    # Give API time to start
    time.sleep(2)

    # Start GUI
    root = ctk.CTk()
    dashboard = TemperatureDashboard(root)

    # Fetch initial data
    dashboard.fetch_temperature_data_from_api()
    dashboard.fetch_hourly_trend_data()

    # Schedule periodic updates
    def update_loop():
        while True:
            dashboard.fetch_temperature_data_from_api()
            root.after(5000)

    update_thread = threading.Thread(target=update_loop, daemon=True)
    update_thread.start()

    root.mainloop()

if **name** == "**main**":
main()

# ============================================================================

# SUMMARY OF INTEGRATION OPTIONS

# ============================================================================

"""

1. API-Based Integration (Recommended)
   - Pros: Decoupled, scalable, can run API and GUI separately
   - How: Use requests library to fetch from Flask API
   - File: Keep requests in separate fetch functions

2. Direct Database Access
   - Pros: Direct control, no API overhead
   - How: Use SQLAlchemy directly in dashboard
   - File: Import from database.models and database.db

3. Real-Time with Threading
   - Pros: Live updates without blocking UI
   - How: Use background threads with time.sleep()
   - File: Create separate update thread

4. Hybrid Approach
   - Pros: Best of both worlds
   - How: API for core data, database for advanced queries
   - File: Use both when needed

Start simple with API integration, then add real-time updates as needed!
"""
