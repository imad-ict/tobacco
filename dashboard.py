import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Weather Risk Assessment - Tobacco Cultivation",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Constants
API_KEY = "fdb65b20ef3e55d681c05652324d4839"

LOCATIONS = {
    "Mardan": {"coords": (34.201, 72.050), "elevation": "283m", "climate": "Semi-arid continental"},
    "Multan": {"coords": (30.157, 71.524), "elevation": "122m", "climate": "Hot desert"},
    "Swabi": {"coords": (34.120, 72.470), "elevation": "300m", "climate": "Semi-arid continental"},
    "Charsadda": {"coords": (34.150, 71.740), "elevation": "276m", "climate": "Semi-arid continental"}
}

# Caching for API calls
@st.cache_data(ttl=300)  # Cache for 5 minutes
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
        st.error(f"Error fetching weather data: {e}")
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

def calculate_rain_risk(rain_1h, rain_3h=None):
    """Calculate rain risk (0-4 scale)"""
    # Use 3-hour rain if available, otherwise use 1-hour
    rain = rain_3h if rain_3h is not None else rain_1h * 3
    
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

def get_risk_color(risk_level):
    """Get color based on risk level"""
    if risk_level >= 3:
        return "#FF4B4B"  # Red
    elif risk_level >= 2:
        return "#FF8C00"  # Orange
    elif risk_level >= 1:
        return "#FFD700"  # Yellow
    else:
        return "#00C851"  # Green

def get_risk_message(risk_type, risk_level):
    """Get risk-specific message for tobacco cultivation"""
    messages = {
        "dust": {
            0: "✅ No dust risk - Ideal conditions for tobacco growth",
            1: "⚠️ Low dust risk - Monitor wind conditions",
            2: "⚠️ Moderate dust risk - Consider protective measures for young plants",
            3: "🚨 High dust risk - Leaf damage and reduced photosynthesis likely",
            4: "🚨 Severe dust risk - Immediate protection required for crops"
        },
        "hail": {
            0: "✅ No hail risk - Safe conditions for tobacco",
            1: "⚠️ Low hail risk - Monitor weather updates",
            2: "⚠️ Moderate hail risk - Prepare protective covers",
            3: "🚨 High hail risk - Secure crops and equipment",
            4: "🚨 Severe hail risk - Immediate shelter required for tobacco plants"
        },
        "rain": {
            0: "✅ No rain - Consider irrigation needs",
            1: "🌧️ Light rain - Beneficial for tobacco growth",
            2: "🌧️ Moderate rain - Monitor soil drainage",
            3: "⚠️ Heavy rain - Risk of waterlogging and disease",
            4: "🚨 Severe rain - Flooding risk, protect tobacco fields"
        }
    }
    return messages[risk_type].get(risk_level, "Unknown risk level")

def create_gauge(value, title, max_value=4):
    """Create a gauge chart using Plotly"""
    color = get_risk_color(value)
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title, 'font': {'size': 16}},
        gauge = {
            'axis': {'range': [None, max_value], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 1], 'color': '#E8F5E8'},
                {'range': [1, 2], 'color': '#FFF8DC'},
                {'range': [2, 3], 'color': '#FFE4B5'},
                {'range': [3, 4], 'color': '#FFE4E1'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 3
            }
        }
    ))
    
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=40, b=20),
        font={'color': "darkblue", 'family': "Arial"}
    )
    
    return fig

def main():
    # Header Section
    st.markdown("""
    <div style='text-align: center; padding: 20px; background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%); color: white; border-radius: 10px; margin-bottom: 20px;'>
        <h1 style='margin: 0; font-size: 2.5em;'>🌾 Real-time Weather Monitoring and Risk Assessment</h1>
        <h3 style='margin: 10px 0 0 0; font-weight: 300;'>for Tobacco Cultivation in Pakistan</h3>
        <p style='margin: 10px 0 0 0; opacity: 0.9;'>Regional weather insights, risks, and forecast for dust, hail, and rain</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Region Selection
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        selected_region = st.selectbox(
            "📍 Select Region",
            options=list(LOCATIONS.keys()),
            index=0,
            help="Choose a tobacco cultivation region for detailed weather analysis"
        )
    
    # Get coordinates and location info
    lat, lon = LOCATIONS[selected_region]["coords"]
    elevation = LOCATIONS[selected_region]["elevation"]
    climate = LOCATIONS[selected_region]["climate"]
    
    # Fetch weather data
    with st.spinner(f"Fetching weather data for {selected_region}..."):
        weather_data = fetch_weather_data(lat, lon)
    
    if weather_data is None:
        st.error("Unable to fetch weather data. Please try again later.")
        return
    
    # Extract current weather
    current = weather_data.get("current", {})
    hourly = weather_data.get("hourly", [])[:12]  # Next 12 hours
    daily = weather_data.get("daily", [])[:7]     # Next 7 days
    
    # Current Regional Overview
    st.markdown("### 📊 Current Regional Overview")
    
    # Calculate current risks
    current_dust_risk = calculate_dust_risk(
        current.get("wind_speed", 0),
        current.get("humidity", 0),
        current.get("pressure", 1013)
    )
    
    current_hail_risk = calculate_hail_risk(
        current.get("temp", 0),
        current.get("rain", {}).get("1h", 0),
        current.get("clouds", 0),
        current.get("wind_speed", 0)
    )
    
    current_rain_risk = calculate_rain_risk(
        current.get("rain", {}).get("1h", 0)
    )
    
    # Calculate 7-day precipitation total
    total_precipitation = sum([day.get("rain", 0) for day in daily])
    
    # KPI Cards
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric(
            "🌡️ Temperature",
            f"{current.get('temp', 0):.1f}°C",
            f"{current.get('temp', 0) - 25:.1f}°C from optimal"
        )
    
    with col2:
        st.metric(
            "💧 Humidity",
            f"{current.get('humidity', 0)}%",
            f"{current.get('humidity', 0) - 60:.0f}% from optimal"
        )
    
    with col3:
        st.metric(
            "🌬️ Wind Speed",
            f"{current.get('wind_speed', 0):.1f} m/s",
            f"Risk Level: {current_dust_risk}"
        )
    
    with col4:
        st.metric(
            "☔ 7-Day Precipitation",
            f"{total_precipitation:.1f} mm",
            f"Risk Level: {current_rain_risk}"
        )
    
    with col5:
        st.metric(
            "🌾 Growth Stage",
            "Flowering Day 75",
            "Critical Period"
        )
    
    with col6:
        st.metric(
            "📍 Location Info",
            f"{elevation}",
            climate
        )
    
    # Navigation Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🌤️ Weather Details", "⚠️ Risk Assessment", "📈 Trends"])
    
    with tab1:
        st.markdown("### 🌤️ Current Weather Conditions")
        
        # Current weather details
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            **Current Conditions for {selected_region}**
            - **Temperature:** {current.get('temp', 0):.1f}°C
            - **Feels Like:** {current.get('feels_like', 0):.1f}°C
            - **Humidity:** {current.get('humidity', 0)}%
            - **Pressure:** {current.get('pressure', 0)} hPa
            - **Wind Speed:** {current.get('wind_speed', 0):.1f} m/s
            - **Wind Direction:** {current.get('wind_deg', 0)}°
            - **Cloud Cover:** {current.get('clouds', 0)}%
            - **UV Index:** {current.get('uvi', 0):.1f}
            """)
        
        with col2:
            # Weather description
            weather_desc = current.get('weather', [{}])[0]
            st.markdown(f"""
            **Weather Description**
            - **Condition:** {weather_desc.get('main', 'Unknown')}
            - **Description:** {weather_desc.get('description', 'No description').title()}
            - **Visibility:** {current.get('visibility', 0)/1000:.1f} km
            - **Dew Point:** {current.get('dew_point', 0):.1f}°C
            
            **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """)
    
    with tab2:
        st.markdown("### 🕐 12-Hour Forecast")
        
        # Prepare hourly forecast data
        hourly_data = []
        for i, hour in enumerate(hourly):
            hourly_data.append({
                "Time": datetime.fromtimestamp(hour["dt"]).strftime("%H:%M"),
                "Temp (°C)": f"{hour['temp']:.1f}",
                "Wind (m/s)": f"{hour['wind_speed']:.1f}",
                "Humidity (%)": f"{hour['humidity']}",
                "Rain (mm)": f"{hour.get('rain', {}).get('1h', 0):.1f}",
                "Clouds (%)": f"{hour['clouds']}",
                "Pressure (hPa)": f"{hour['pressure']}"
            })
        
        hourly_df = pd.DataFrame(hourly_data)
        st.dataframe(hourly_df, use_container_width=True)
        
        st.markdown("### 📅 7-Day Forecast")
        
        # Prepare daily forecast data
        daily_data = []
        for day in daily:
            daily_data.append({
                "Date": datetime.fromtimestamp(day["dt"]).strftime("%Y-%m-%d"),
                "Day Temp (°C)": f"{day['temp']['day']:.1f}",
                "Night Temp (°C)": f"{day['temp']['night']:.1f}",
                "Humidity (%)": f"{day['humidity']}",
                "Wind (m/s)": f"{day['wind_speed']:.1f}",
                "Rain (mm)": f"{day.get('rain', 0):.1f}",
                "Clouds (%)": f"{day['clouds']}"
            })
        
        daily_df = pd.DataFrame(daily_data)
        st.dataframe(daily_df, use_container_width=True)
    
    with tab3:
        st.markdown("### ⚠️ Risk Assessment Gauges")
        
        # Risk gauges
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.plotly_chart(
                create_gauge(current_dust_risk, "🌪️ Dust Risk"),
                use_container_width=True
            )
            st.markdown(get_risk_message("dust", current_dust_risk))
        
        with col2:
            st.plotly_chart(
                create_gauge(current_hail_risk, "🧊 Hail Risk"),
                use_container_width=True
            )
            st.markdown(get_risk_message("hail", current_hail_risk))
        
        with col3:
            st.plotly_chart(
                create_gauge(current_rain_risk, "🌧️ Rain Risk"),
                use_container_width=True
            )
            st.markdown(get_risk_message("rain", current_rain_risk))
        
        # Risk Legend
        st.markdown("### 📋 Risk Level Legend")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div style='background-color: #E8F5E8; padding: 10px; border-radius: 5px; text-align: center;'>
                <strong>🟢 Low Risk (0-1)</strong><br>
                Safe conditions
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style='background-color: #FFF8DC; padding: 10px; border-radius: 5px; text-align: center;'>
                <strong>🟡 Light Risk (1-2)</strong><br>
                Monitor conditions
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style='background-color: #FFE4B5; padding: 10px; border-radius: 5px; text-align: center;'>
                <strong>🟠 Moderate Risk (2-3)</strong><br>
                Take precautions
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div style='background-color: #FFE4E1; padding: 10px; border-radius: 5px; text-align: center;'>
                <strong>🔴 Severe Risk (3-4)</strong><br>
                Immediate action
            </div>
            """, unsafe_allow_html=True)
    
    with tab4:
        st.markdown("### 📈 Weather Trends")
        
        # Prepare trend data
        trend_data = []
        for i, hour in enumerate(hourly):
            dt = datetime.fromtimestamp(hour["dt"])
            dust_risk = calculate_dust_risk(hour["wind_speed"], hour["humidity"], hour["pressure"])
            hail_risk = calculate_hail_risk(hour["temp"], hour.get("rain", {}).get("1h", 0), hour["clouds"], hour["wind_speed"])
            rain_risk = calculate_rain_risk(hour.get("rain", {}).get("1h", 0))
            
            trend_data.append({
                "Time": dt,
                "Temperature": hour["temp"],
                "Humidity": hour["humidity"],
                "Wind Speed": hour["wind_speed"],
                "Dust Risk": dust_risk,
                "Hail Risk": hail_risk,
                "Rain Risk": rain_risk
            })
        
        trend_df = pd.DataFrame(trend_data)
        
        # Temperature and humidity trend
        fig_temp = px.line(trend_df, x="Time", y=["Temperature", "Humidity"], 
                          title="Temperature and Humidity Trend (Next 12 Hours)")
        st.plotly_chart(fig_temp, use_container_width=True)
        
        # Risk trends
        fig_risk = px.line(trend_df, x="Time", y=["Dust Risk", "Hail Risk", "Rain Risk"],
                          title="Risk Level Trends (Next 12 Hours)")
        st.plotly_chart(fig_risk, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>🌾 Tobacco Cultivation Weather Monitoring System | Data provided by OpenWeatherMap</p>
        <p>Last updated: {}</p>
    </div>
    """.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), unsafe_allow_html=True)

if __name__ == "__main__":
    main() 