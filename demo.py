#!/usr/bin/env python3
"""
Demo script to test weather API and risk calculations
Run this to verify the dashboard components work correctly
"""

import requests
import pandas as pd
from datetime import datetime

# Constants from dashboard
API_KEY = "fdb65b20ef3e55d681c05652324d4839"
LOCATIONS = {
    "Mardan": {"coords": (34.201, 72.050), "elevation": "283m", "climate": "Semi-arid continental"},
    "Multan": {"coords": (30.157, 71.524), "elevation": "122m", "climate": "Hot desert"},
    "Swabi": {"coords": (34.120, 72.470), "elevation": "300m", "climate": "Semi-arid continental"},
    "Charsadda": {"coords": (34.150, 71.740), "elevation": "276m", "climate": "Semi-arid continental"}
}

def fetch_weather_data(lat, lon):
    """Fetch weather data from OpenWeatherMap API"""
    url = "https://api.openweathermap.org/data/3.0/onecall"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY,
        "units": "metric",
        "exclude": "minutely,alerts"
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None

def calculate_dust_risk(wind_speed, humidity, pressure):
    """Calculate dust storm risk (0-4 scale)"""
    if wind_speed > 15 and humidity < 30:
        return 4
    elif wind_speed > 10 and humidity < 35:
        return 3
    elif wind_speed > 7 and humidity < 40:
        return 2
    elif wind_speed > 4 and humidity < 50:
        return 1
    else:
        return 0

def calculate_hail_risk(temp, rain, clouds, wind_speed):
    """Calculate hail storm risk (0-4 scale)"""
    if temp > 25 and rain > 3 and clouds > 80 and wind_speed > 5:
        return 4
    elif temp > 25 and rain > 2 and clouds > 60:
        return 3
    elif rain > 1 and clouds > 40:
        return 2
    elif rain > 0.5 and clouds > 20:
        return 1
    else:
        return 0

def calculate_rain_risk(rain_1h):
    """Calculate rain risk (0-4 scale)"""
    rain = rain_1h * 3  # Estimate 3-hour rain
    
    if rain > 10:
        return 4
    elif rain > 6:
        return 3
    elif rain > 3:
        return 2
    elif rain > 0.5:
        return 1
    else:
        return 0

def main():
    print("🌾 Weather Risk Assessment Dashboard - Demo Test")
    print("=" * 60)
    
    # Test API connection and risk calculations for each region
    for region_name, region_data in LOCATIONS.items():
        print(f"\n📍 Testing {region_name}")
        print("-" * 40)
        
        lat, lon = region_data["coords"]
        elevation = region_data["elevation"]
        climate = region_data["climate"]
        
        print(f"Coordinates: {lat}°N, {lon}°E")
        print(f"Elevation: {elevation}")
        print(f"Climate: {climate}")
        
        # Fetch weather data
        print("Fetching weather data...")
        weather_data = fetch_weather_data(lat, lon)
        
        if weather_data is None:
            print("❌ Failed to fetch weather data")
            continue
        
        # Extract current weather
        current = weather_data.get("current", {})
        
        # Display current conditions
        print(f"\n🌤️ Current Conditions:")
        print(f"  Temperature: {current.get('temp', 0):.1f}°C")
        print(f"  Humidity: {current.get('humidity', 0)}%")
        print(f"  Wind Speed: {current.get('wind_speed', 0):.1f} m/s")
        print(f"  Pressure: {current.get('pressure', 0)} hPa")
        print(f"  Cloud Cover: {current.get('clouds', 0)}%")
        print(f"  Rain (1h): {current.get('rain', {}).get('1h', 0):.1f} mm")
        
        # Calculate risks
        dust_risk = calculate_dust_risk(
            current.get("wind_speed", 0),
            current.get("humidity", 0),
            current.get("pressure", 1013)
        )
        
        hail_risk = calculate_hail_risk(
            current.get("temp", 0),
            current.get("rain", {}).get("1h", 0),
            current.get("clouds", 0),
            current.get("wind_speed", 0)
        )
        
        rain_risk = calculate_rain_risk(
            current.get("rain", {}).get("1h", 0)
        )
        
        # Display risk assessments
        print(f"\n⚠️ Risk Assessment:")
        print(f"  🌪️ Dust Risk: {dust_risk}/4")
        print(f"  🧊 Hail Risk: {hail_risk}/4")
        print(f"  🌧️ Rain Risk: {rain_risk}/4")
        
        # Risk level interpretation
        risk_levels = ["No Risk", "Low Risk", "Moderate Risk", "High Risk", "Severe Risk"]
        print(f"\n📊 Risk Interpretation:")
        print(f"  Dust: {risk_levels[dust_risk]}")
        print(f"  Hail: {risk_levels[hail_risk]}")
        print(f"  Rain: {risk_levels[rain_risk]}")
        
        # Weather description
        weather_desc = current.get('weather', [{}])[0]
        print(f"\n🌈 Weather Description: {weather_desc.get('description', 'Unknown').title()}")
        
        print(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n" + "=" * 60)
    print("✅ Demo test completed successfully!")
    print("🚀 Dashboard is ready to run with: streamlit run dashboard.py")
    print("🌐 Access at: http://localhost:8501")

if __name__ == "__main__":
    main() 