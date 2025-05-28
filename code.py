import requests
import pandas as pd

API_KEY = "fdb65b20ef3e55d681c05652324d4839"

LOCATIONS = {
    "Mardan": (34.201, 72.050),
    "Multan": (30.473469, 71.486885),
    "Swabi": (34.120, 72.470),
    "Charsadda": (34.150, 71.740)
}

def fetch_forecast(lat, lon):
    url = "https://api.openweathermap.org/data/3.0/onecall"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY,
        "units": "metric",
        "exclude": "minutely,current,alerts"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def classify_weather_hourly(row):
    wind = row["wind_speed (m/s)"]
    humidity = row["humidity (%)"]
    temp = row["temp (°C)"]
    rain = row["rain (mm)"]
    clouds = row["clouds (%)"]
    pressure = row["pressure (hPa)"]

    # Improved dust storm logic - more realistic thresholds
    # Only consider dust risk when wind ≥8 m/s, humidity ≤40%, pressure ≤998 hPa
    dust_risk = False
    if wind >= 8 and humidity <= 40 and pressure <= 998:
        if wind >= 15 and humidity <= 20 and pressure <= 990:
            dust_risk = "Severe"
        elif wind >= 12 and humidity <= 25 and pressure <= 995:
            dust_risk = "Moderate"
        elif wind >= 10 and humidity <= 30:
            dust_risk = "Moderate"
        elif wind >= 8:
            dust_risk = "Mild"
    
    # Hailstorm logic (unchanged)
    hail_risk = False
    if temp > 25 and humidity > 60 and rain > 3 and clouds > 80 and wind > 4 and pressure < 1005:
        hail_risk = "Severe"
    elif temp > 25 and rain > 2 and clouds > 60:
        hail_risk = "Moderate"
    elif rain > 1 and clouds > 40:
        hail_risk = "Mild"

    # Return the highest risk
    if dust_risk:
        return f"Dust Storm Risk ({dust_risk})"
    elif hail_risk:
        return f"Hailstorm Risk ({hail_risk})"
    else:
        return "Clear or Normal"

def classify_weather_daily(row):
    wind = row["wind_speed (m/s)"]
    humidity = row["humidity (%)"]
    temp = row["temp_day (°C)"]
    rain = row["rain (mm)"]
    clouds = row["clouds (%)"]
    pressure = row["pressure (hPa)"]

    # Improved dust storm logic - more realistic thresholds
    # Only consider dust risk when wind ≥8 m/s, humidity ≤40%, pressure ≤998 hPa
    dust_risk = False
    if wind >= 8 and humidity <= 40 and pressure <= 998:
        if wind >= 15 and humidity <= 20 and pressure <= 990:
            dust_risk = "Severe"
        elif wind >= 12 and humidity <= 25 and pressure <= 995:
            dust_risk = "Moderate"
        elif wind >= 10 and humidity <= 30:
            dust_risk = "Moderate"
        elif wind >= 8:
            dust_risk = "Mild"
    
    # Hailstorm logic (unchanged)
    hail_risk = False
    if temp > 25 and humidity > 60 and rain > 3 and clouds > 80 and wind > 4 and pressure < 1005:
        hail_risk = "Severe"
    elif temp > 25 and rain > 2 and clouds > 60:
        hail_risk = "Moderate"
    elif rain > 1 and clouds > 40:
        hail_risk = "Mild"

    # Return the highest risk
    if dust_risk:
        return f"Dust Storm Risk ({dust_risk})"
    elif hail_risk:
        return f"Hailstorm Risk ({hail_risk})"
    else:
        return "Clear or Normal"

# Fetch and display forecasts
for city, (lat, lon) in LOCATIONS.items():
    print(f"\n📍 Forecast for {city}")
    js = fetch_forecast(lat, lon)

    # Hourly
    hourly_data = []
    for entry in js["hourly"][:24]:  # Next 24 hours
        hourly_data.append({
            "time": pd.to_datetime(entry["dt"], unit='s'),
            "temp (°C)": entry["temp"],
            "humidity (%)": entry["humidity"],
            "pressure (hPa)": entry["pressure"],
            "wind_speed (m/s)": entry["wind_speed"],
            "clouds (%)": entry["clouds"],
            "rain (mm)": entry.get("rain", {}).get("1h", 0.0)
        })
    hourly_df = pd.DataFrame(hourly_data)
    hourly_df["risk"] = hourly_df.apply(classify_weather_hourly, axis=1)
    print("\nHourly Forecast (Next 24h):")
    print(hourly_df.head(10))

    # Daily
    daily_data = []
    for entry in js["daily"][:7]:
        daily_data.append({
            "date": pd.to_datetime(entry["dt"], unit='s').date(),
            "temp_day (°C)": entry["temp"]["day"],
            "humidity (%)": entry["humidity"],
            "pressure (hPa)": entry["pressure"],
            "wind_speed (m/s)": entry["wind_speed"],
            "clouds (%)": entry["clouds"],
            "rain (mm)": entry.get("rain", 0.0)
        })
    daily_df = pd.DataFrame(daily_data)
    daily_df["risk"] = daily_df.apply(classify_weather_daily, axis=1)
    print("\nDaily Forecast (7 Days):")
    print(daily_df)
