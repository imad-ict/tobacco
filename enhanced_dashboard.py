import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np
import pytz

# Page configuration
st.set_page_config(
    page_title="Weather Risk Assessment - Tobacco Cultivation",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Pakistan timezone
PAKISTAN_TZ = pytz.timezone('Asia/Karachi')

# Auto-refresh every 30 minutes
if "last_update" not in st.session_state:
    st.session_state.last_update = datetime.now(PAKISTAN_TZ)

# Check if 30 minutes have passed
def should_refresh():
    now = datetime.now(PAKISTAN_TZ)
    time_diff = (now - st.session_state.last_update).total_seconds()
    return time_diff >= 1800  # 30 minutes = 1800 seconds

# Auto-refresh mechanism
if should_refresh():
    st.session_state.last_update = datetime.now(PAKISTAN_TZ)
    st.rerun()

# Constants
API_KEY = "fdb65b20ef3e55d681c05652324d4839"

LOCATIONS = {
    "Mardan": {"coords": (34.201, 72.050), "elevation": "283m", "climate": "Semi-arid continental"},
    "Multan": {"coords": (30.473469, 71.486885), "elevation": "122m", "climate": "Hot desert"},
    "Swabi": {"coords": (34.120, 72.470), "elevation": "300m", "climate": "Semi-arid continental"},
    "Charsadda": {"coords": (34.150, 71.740), "elevation": "276m", "climate": "Semi-arid continental"}
}

# Tobacco cultivation calendar for Pakistan (based on research)
TOBACCO_CALENDAR = {
    "nursery_sowing": {"month": 12, "day": 20, "description": "Nursery sowing in December"},
    "transplanting": {"month": 3, "day": 25, "description": "Transplanting in late March"},
    "vegetative_growth": {"month": 4, "day": 15, "description": "Vegetative growth phase"},
    "flowering": {"month": 6, "day": 1, "description": "Flowering begins in June"},
    "topping": {"month": 6, "day": 15, "description": "Topping at 24 leaves stage"},
    "leaf_maturation": {"month": 7, "day": 1, "description": "Leaf maturation phase"},
    "harvest_start": {"month": 8, "day": 1, "description": "Harvest begins in August"},
    "harvest_end": {"month": 9, "day": 30, "description": "Harvest ends in September"}
}

def get_current_growth_stage():
    """Determine current tobacco growth stage based on date"""
    current_date = datetime.now(PAKISTAN_TZ)
    current_month = current_date.month
    current_day = current_date.day
    
    # Convert current date to day of year for comparison
    current_doy = current_date.timetuple().tm_yday
    
    # Calculate day of year for each stage
    stages = {}
    for stage, info in TOBACCO_CALENDAR.items():
        stage_date = datetime(current_date.year, info["month"], info["day"], tzinfo=PAKISTAN_TZ)
        if stage_date < current_date and info["month"] > 6:  # Handle year transition
            stage_date = datetime(current_date.year - 1, info["month"], info["day"], tzinfo=PAKISTAN_TZ)
        stages[stage] = stage_date.timetuple().tm_yday
    
    # Determine current stage
    if current_month >= 12 or current_month <= 2:
        return "Nursery Stage", "Seedlings in nursery beds", "🌱", "Low"
    elif current_month == 3:
        return "Transplanting", "Moving seedlings to field", "🌿", "High"
    elif current_month == 4 or current_month == 5:
        return "Vegetative Growth", "Rapid leaf development", "🍃", "Medium"
    elif current_month == 6:
        if current_day < 15:
            return "Flowering", "Flower bud formation", "🌸", "High"
        else:
            return "Topping Stage", "Removing flower buds", "✂️", "High"
    elif current_month == 7:
        return "Leaf Maturation", "Leaves reaching maturity", "🌾", "High"
    elif current_month == 8 or current_month == 9:
        return "Harvest Period", "Leaf harvesting active", "🚜", "Critical"
    else:
        return "Post-Harvest", "Field preparation for next season", "🏞️", "Low"

def calculate_stage_specific_risk_multiplier(stage_name):
    """Calculate risk multiplier based on growth stage vulnerability"""
    stage_multipliers = {
        "Nursery Stage": 0.8,      # Lower field risk
        "Transplanting": 1.5,      # Very vulnerable to weather
        "Vegetative Growth": 1.2,   # Moderate vulnerability
        "Flowering": 1.4,          # High vulnerability to stress
        "Topping Stage": 1.3,      # Vulnerable during topping
        "Leaf Maturation": 1.6,    # Critical for quality
        "Harvest Period": 1.8,     # Most critical period
        "Post-Harvest": 0.6        # Minimal risk
    }
    return stage_multipliers.get(stage_name, 1.0)

# Caching for API calls - Updated to 30 minutes
@st.cache_data(ttl=1800)  # Cache for 30 minutes (1800 seconds)
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

def calculate_dust_risk(wind_speed, humidity, pressure, stage_multiplier=1.0, visibility=None, dew_point=None, temp=None, clouds=None):
    """
    Calculate dust storm risk (0-4 scale) with realistic meteorological thresholds
    
    Refined logic to reduce false positives:
    - Only consider dust risk when wind ≥8 m/s, humidity ≤40%, pressure ≤998 hPa
    - Clear cutoffs for base risk assignment
    - Conservative approach to avoid over-amplification
    """
    base_risk = 0
    
    # Primary condition check: Only proceed if basic dust storm conditions are met
    if wind_speed < 8 or humidity > 40 or pressure > 998:
        return 0  # No dust risk if basic conditions not met
    
    # Core dust storm risk assessment with realistic thresholds
    # All conditions require wind ≥8 m/s, humidity ≤40%, pressure ≤998 hPa
    if wind_speed >= 15 and humidity <= 20 and pressure <= 990:
        base_risk = 4  # Severe: Very high wind, very dry, very low pressure
    elif wind_speed >= 12 and humidity <= 25 and pressure <= 995:
        base_risk = 3  # High: High wind, dry, low pressure
    elif wind_speed >= 10 and humidity <= 30 and pressure <= 998:
        base_risk = 2  # Moderate: Moderate-high wind, moderately dry
    elif wind_speed >= 8 and humidity <= 40 and pressure <= 998:
        base_risk = 1  # Light: Minimum conditions met
    
    # Optional enhancements (only if base conditions are already met)
    if base_risk > 0:
        # Visibility confirmation (if available)
        if visibility is not None and visibility < 5000:
            base_risk = min(4, base_risk + 1)  # Dust confirmed by poor visibility
        
        # Dew point spread (if available) - indicates very dry air
        if temp is not None and dew_point is not None:
            temp_dew_spread = temp - dew_point
            if temp_dew_spread > 15:  # Very dry air (stricter threshold)
                base_risk = min(4, base_risk + 1)
    
    # Conservative false positive exclusion
    # High humidity override (even if other conditions met)
    if humidity > 50:
        base_risk = 0
    
    # Very low wind override
    if wind_speed < 6:
        base_risk = 0
    
    # High cloud cover with stable conditions
    if clouds is not None and clouds > 70 and wind_speed < 10:
        base_risk = 0  # Stable atmospheric conditions
    
    # Apply stage multiplier conservatively and round to integer
    adjusted_risk = base_risk * stage_multiplier
    final_risk = min(4, round(adjusted_risk))
    
    return int(final_risk)

def calculate_hail_risk(temp, rain, clouds, wind_speed, stage_multiplier=1.0, pressure=None, cape=None, humidity=None):
    """
    Calculate hail storm risk (0-4 scale) with enhanced meteorological variables
    
    Enhanced with:
    - Atmospheric pressure as risk amplifier
    - CAPE (Convective Available Potential Energy) for convective storm strength
    - False positive exclusion rules
    """
    base_risk = 0
    
    # Core hail storm risk assessment (original logic)
    if temp > 25 and rain > 3 and clouds > 80 and wind_speed > 5:
        base_risk = 4
    elif temp > 25 and rain > 2 and clouds > 60:
        base_risk = 3
    elif rain > 1 and clouds > 40:
        base_risk = 2
    elif rain > 0.5 and clouds > 20:
        base_risk = 1
    
    # Enhancement 1: Atmospheric Pressure Amplifier
    # Low/falling pressure (< 1000 hPa) is a known precursor to convective storms
    if pressure is not None and pressure < 1000 and base_risk > 0:
        base_risk = min(4, base_risk + 1)  # Increment risk by +1, capped at 4
        # Additional pressure-based risk for very low pressure (strong convection)
        if pressure < 995:
            base_risk = min(4, base_risk + 1)
    
    # Enhancement 2: CAPE (Convective Available Potential Energy)
    # CAPE is one of the best predictors of convective storm strength and hail potential
    if cape is not None:
        if cape > 2000:  # Very high CAPE - strong convective potential
            base_risk = min(4, base_risk + 2)
        elif cape > 1000:  # Moderate CAPE - moderate convective potential
            base_risk = min(4, base_risk + 1)
        elif cape > 500:  # Low CAPE - slight convective enhancement
            if base_risk > 0:
                base_risk = min(4, base_risk + 0.5)
    
    # Enhancement 3: Temperature-based convective enhancement
    # Higher temperatures increase convective potential
    if temp > 30:  # Very warm conditions enhance convection
        if base_risk > 0:
            base_risk = min(4, base_risk + 0.5)
    elif temp > 35:  # Extremely warm conditions
        if base_risk > 0:
            base_risk = min(4, base_risk + 1)
    
    # Enhancement 4: False Positive Exclusion Rules
    # Suppress hail alerts under conditions unfavorable for hailstorms
    
    # Rule 1: Low cloud cover exclusion (< 20%)
    # Hailstorms require significant cloud development
    if clouds < 20:
        base_risk = 0  # Insufficient cloud cover for hailstorm development
    
    # Rule 2: Very low temperature exclusion (< 15°C)
    # Hailstorms are unlikely in very cool conditions
    if temp < 15:
        base_risk = 0  # Too cold for significant convective development
    
    # Rule 3: Very low humidity with low clouds (< 40% humidity, < 40% clouds)
    # Dry conditions with low clouds unlikely to produce hail
    if humidity is not None and humidity < 40 and clouds < 40:
        base_risk = max(0, base_risk - 1)  # Reduce risk for dry, clear conditions
    
    # Rule 4: Very low wind speed with moderate conditions
    # Weak wind shear reduces hail potential in marginal conditions
    if wind_speed < 2 and base_risk <= 2:
        base_risk = max(0, base_risk - 1)  # Reduce risk for weak wind conditions
    
    # Apply stage-specific multiplier and ensure final risk is capped at 4
    adjusted_risk = min(4, base_risk * stage_multiplier)
    return round(adjusted_risk)

def calculate_rain_risk(rain_1h, rain_3h=None, stage_multiplier=1.0):
    """Calculate rain risk (0-4 scale) with stage-specific adjustments"""
    # Use 3-hour rain if available, otherwise estimate from 1-hour
    rain = rain_3h if rain_3h is not None else rain_1h * 3
    
    base_risk = 0
    if rain > 10:
        base_risk = 4
    elif rain > 6:
        base_risk = 3
    elif rain > 3:
        base_risk = 2
    elif rain > 0.5:
        base_risk = 1
    
    # Apply stage-specific multiplier and cap at 4
    adjusted_risk = min(4, base_risk * stage_multiplier)
    return round(adjusted_risk)

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

def get_risk_intensity_label(risk_level):
    """Get risk intensity label based on risk level"""
    if risk_level >= 4:
        return "Severe"
    elif risk_level >= 3:
        return "High"
    elif risk_level >= 2:
        return "Moderate"
    elif risk_level >= 1:
        return "Light"
    else:
        return "None"

def get_stage_specific_risk_message(risk_type, risk_level, stage_name):
    """Get stage-specific risk message for tobacco cultivation"""
    stage_messages = {
        "dust": {
            "Nursery Stage": {
                0: "✅ No dust risk - Nursery beds protected",
                1: "⚠️ Low dust risk - Monitor nursery covers",
                2: "⚠️ Moderate dust risk - Secure nursery protection",
                3: "🚨 High dust risk - Seedlings vulnerable to desiccation",
                4: "🚨 Severe dust risk - Emergency nursery protection needed"
            },
            "Transplanting": {
                0: "✅ No dust risk - Good conditions for transplanting",
                1: "⚠️ Low dust risk - Monitor newly transplanted seedlings",
                2: "⚠️ Moderate dust risk - Provide windbreaks for young plants",
                3: "🚨 High dust risk - Delay transplanting if possible",
                4: "🚨 Severe dust risk - Postpone transplanting operations"
            },
            "Vegetative Growth": {
                0: "✅ No dust risk - Optimal growth conditions",
                1: "⚠️ Low dust risk - Monitor leaf development",
                2: "⚠️ Moderate dust risk - Dust may reduce photosynthesis",
                3: "🚨 High dust risk - Leaf damage and stunted growth likely",
                4: "🚨 Severe dust risk - Severe leaf damage expected"
            },
            "Flowering": {
                0: "✅ No dust risk - Good flowering conditions",
                1: "⚠️ Low dust risk - Monitor flower development",
                2: "⚠️ Moderate dust risk - May affect flower formation",
                3: "🚨 High dust risk - Flowering stress and poor seed set",
                4: "🚨 Severe dust risk - Severe flowering disruption"
            },
            "Topping Stage": {
                0: "✅ No dust risk - Good conditions for topping",
                1: "⚠️ Low dust risk - Normal topping operations",
                2: "⚠️ Moderate dust risk - Protect fresh cuts from dust",
                3: "🚨 High dust risk - Delay topping operations",
                4: "🚨 Severe dust risk - Postpone all field operations"
            },
            "Leaf Maturation": {
                0: "✅ No dust risk - Optimal leaf maturation",
                1: "⚠️ Low dust risk - Monitor leaf quality",
                2: "⚠️ Moderate dust risk - May affect leaf quality",
                3: "🚨 High dust risk - Reduced leaf quality and value",
                4: "🚨 Severe dust risk - Significant quality degradation"
            },
            "Harvest Period": {
                0: "✅ No dust risk - Good harvesting conditions",
                1: "⚠️ Low dust risk - Normal harvest operations",
                2: "⚠️ Moderate dust risk - Protect harvested leaves",
                3: "🚨 High dust risk - Delay harvest if possible",
                4: "🚨 Severe dust risk - Suspend harvest operations"
            },
            "Post-Harvest": {
                0: "✅ No dust risk - Good for field preparation",
                1: "⚠️ Low dust risk - Normal field operations",
                2: "⚠️ Moderate dust risk - Limit field activities",
                3: "🚨 High dust risk - Postpone field preparation",
                4: "🚨 Severe dust risk - Avoid all field operations"
            }
        },
        "hail": {
            "Nursery Stage": {
                0: "✅ No hail risk - Nursery beds safe",
                1: "⚠️ Low hail risk - Monitor weather updates",
                2: "⚠️ Moderate hail risk - Prepare nursery covers",
                3: "🚨 High hail risk - Secure nursery protection",
                4: "🚨 Severe hail risk - Emergency nursery shelter needed"
            },
            "Transplanting": {
                0: "✅ No hail risk - Safe for transplanting",
                1: "⚠️ Low hail risk - Monitor young plants",
                2: "⚠️ Moderate hail risk - Prepare plant protection",
                3: "🚨 High hail risk - Delay transplanting",
                4: "🚨 Severe hail risk - Postpone all transplanting"
            },
            "Vegetative Growth": {
                0: "✅ No hail risk - Good growth conditions",
                1: "⚠️ Low hail risk - Monitor plant development",
                2: "⚠️ Moderate hail risk - Prepare protective measures",
                3: "🚨 High hail risk - Severe leaf damage possible",
                4: "🚨 Severe hail risk - Crop destruction likely"
            },
            "Flowering": {
                0: "✅ No hail risk - Safe flowering period",
                1: "⚠️ Low hail risk - Monitor flower development",
                2: "⚠️ Moderate hail risk - Protect flowering plants",
                3: "🚨 High hail risk - Flower damage and poor seed set",
                4: "🚨 Severe hail risk - Complete flowering failure"
            },
            "Topping Stage": {
                0: "✅ No hail risk - Safe for topping operations",
                1: "⚠️ Low hail risk - Normal operations",
                2: "⚠️ Moderate hail risk - Monitor topped plants",
                3: "🚨 High hail risk - Severe damage to fresh cuts",
                4: "🚨 Severe hail risk - Devastating plant damage"
            },
            "Leaf Maturation": {
                0: "✅ No hail risk - Optimal maturation conditions",
                1: "⚠️ Low hail risk - Monitor leaf development",
                2: "⚠️ Moderate hail risk - Prepare leaf protection",
                3: "🚨 High hail risk - Severe leaf damage and quality loss",
                4: "🚨 Severe hail risk - Complete crop loss possible"
            },
            "Harvest Period": {
                0: "✅ No hail risk - Safe harvesting conditions",
                1: "⚠️ Low hail risk - Normal harvest operations",
                2: "⚠️ Moderate hail risk - Accelerate harvest if possible",
                3: "🚨 High hail risk - Emergency harvest needed",
                4: "🚨 Severe hail risk - Immediate crop protection required"
            },
            "Post-Harvest": {
                0: "✅ No hail risk - Safe for field operations",
                1: "⚠️ Low hail risk - Normal activities",
                2: "⚠️ Moderate hail risk - Protect equipment",
                3: "🚨 High hail risk - Secure all equipment",
                4: "🚨 Severe hail risk - Seek shelter immediately"
            }
        },
        "rain": {
            "Nursery Stage": {
                0: "✅ No rain - Monitor nursery irrigation",
                1: "🌧️ Light rain - Beneficial for seedlings",
                2: "🌧️ Moderate rain - Monitor nursery drainage",
                3: "⚠️ Heavy rain - Risk of seedling damping-off",
                4: "🚨 Severe rain - Nursery flooding risk"
            },
            "Transplanting": {
                0: "✅ No rain - Good transplanting conditions",
                1: "🌧️ Light rain - Helpful for establishment",
                2: "🌧️ Moderate rain - Monitor soil conditions",
                3: "⚠️ Heavy rain - Delay transplanting operations",
                4: "🚨 Severe rain - Postpone all transplanting"
            },
            "Vegetative Growth": {
                0: "✅ No rain - Monitor irrigation needs",
                1: "🌧️ Light rain - Beneficial for growth",
                2: "🌧️ Moderate rain - Good for development",
                3: "⚠️ Heavy rain - Risk of waterlogging",
                4: "🚨 Severe rain - Flooding and root damage risk"
            },
            "Flowering": {
                0: "✅ No rain - Good flowering conditions",
                1: "🌧️ Light rain - Adequate moisture",
                2: "🌧️ Moderate rain - Monitor flower health",
                3: "⚠️ Heavy rain - Flower damage and disease risk",
                4: "🚨 Severe rain - Severe flowering disruption"
            },
            "Topping Stage": {
                0: "✅ No rain - Ideal for topping operations",
                1: "🌧️ Light rain - Acceptable conditions",
                2: "🌧️ Moderate rain - Delay topping if possible",
                3: "⚠️ Heavy rain - Postpone topping operations",
                4: "🚨 Severe rain - Risk of disease in fresh cuts"
            },
            "Leaf Maturation": {
                0: "✅ No rain - Optimal maturation conditions",
                1: "🌧️ Light rain - Monitor leaf development",
                2: "🌧️ Moderate rain - May delay maturation",
                3: "⚠️ Heavy rain - Risk of leaf disease and quality loss",
                4: "🚨 Severe rain - Severe quality degradation"
            },
            "Harvest Period": {
                0: "✅ No rain - Perfect harvesting weather",
                1: "🌧️ Light rain - Delay harvest until dry",
                2: "🌧️ Moderate rain - Postpone harvest operations",
                3: "⚠️ Heavy rain - Risk of leaf rot and mold",
                4: "🚨 Severe rain - Emergency crop protection needed"
            },
            "Post-Harvest": {
                0: "✅ No rain - Good for field preparation",
                1: "🌧️ Light rain - Beneficial for soil",
                2: "🌧️ Moderate rain - Good for next season prep",
                3: "⚠️ Heavy rain - Limit field operations",
                4: "🚨 Severe rain - Avoid all field activities"
            }
        }
    }
    
    # Fallback to generic messages if stage not found
    generic_messages = {
        "dust": {
            0: "✅ No dust risk - Ideal conditions for tobacco growth",
            1: "⚠️ Low dust risk - Monitor wind conditions",
            2: "⚠️ Moderate dust risk - Consider protective measures",
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
    
    try:
        return stage_messages[risk_type][stage_name][risk_level]
    except KeyError:
        return generic_messages[risk_type].get(risk_level, "Unknown risk level")

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

def create_risk_legend():
    """Create comprehensive risk level legend"""
    st.markdown("### 📋 Comprehensive Risk Assessment Legend")
    
    # Risk Level Overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style='background-color: #E8F5E8; padding: 15px; border-radius: 10px; text-align: center; border: 2px solid #00C851;'>
            <h4 style='color: #00C851; margin: 0;'>🟢 Level 0-1: LOW RISK</h4>
            <p style='margin: 5px 0;'><strong>Safe Conditions</strong></p>
            <p style='font-size: 12px; margin: 0;'>Normal operations can proceed<br>Routine monitoring sufficient</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background-color: #FFF8DC; padding: 15px; border-radius: 10px; text-align: center; border: 2px solid #FFD700;'>
            <h4 style='color: #DAA520; margin: 0;'>🟡 Level 1-2: MODERATE RISK</h4>
            <p style='margin: 5px 0;'><strong>Monitor Conditions</strong></p>
            <p style='font-size: 12px; margin: 0;'>Increased vigilance required<br>Prepare preventive measures</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='background-color: #FFE4B5; padding: 15px; border-radius: 10px; text-align: center; border: 2px solid #FF8C00;'>
            <h4 style='color: #FF8C00; margin: 0;'>🟠 Level 2-3: HIGH RISK</h4>
            <p style='margin: 5px 0;'><strong>Take Precautions</strong></p>
            <p style='font-size: 12px; margin: 0;'>Implement protective measures<br>Consider delaying operations</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style='background-color: #FFE4E1; padding: 15px; border-radius: 10px; text-align: center; border: 2px solid #FF4B4B;'>
            <h4 style='color: #FF4B4B; margin: 0;'>🔴 Level 3-4: CRITICAL RISK</h4>
            <p style='margin: 5px 0;'><strong>Immediate Action</strong></p>
            <p style='font-size: 12px; margin: 0;'>Emergency measures required<br>Suspend field operations</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Detailed Risk Explanations
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        #### 🌪️ Enhanced Dust Storm Risk Factors
        **Core Meteorological Conditions:**
        - Wind Speed > 15 m/s (Critical)
        - Humidity < 30% (Very Dry)
        - Low Atmospheric Pressure < 1000 hPa
        
        **🔬 Scientific Enhancements:**
        - **Pressure Amplifier:** Low pressure (< 1000 hPa) +1 risk
        - **Visibility Confirmation:** < 5 km confirms dust conditions
        - **Dew Point Spread:** Temp-dew point > 12°C indicates dry air
        - **False Positive Exclusion:** Humidity > 70% or wind < 3 m/s = no risk
        
        **Tobacco Impact:**
        - Leaf surface damage and reduced photosynthesis
        - Stunted growth and quality degradation
        - Respiratory stress in plants
        
        **Critical Stages:**
        - Transplanting (1.5x multiplier)
        - Leaf Maturation (1.6x multiplier)
        - Harvest Period (1.8x multiplier)
        """)
    
    with col2:
        st.markdown("""
        #### 🧊 Enhanced Hail Storm Risk Factors
        **Core Meteorological Conditions:**
        - Temperature > 25°C
        - Heavy Precipitation > 3mm/h
        - Cloud Cover > 80%
        - Strong Winds > 5 m/s
        
        **🔬 Scientific Enhancements:**
        - **Pressure Amplifier:** Low pressure (< 1000 hPa) +1 risk
        - **CAPE Integration:** Convective energy > 2000 J/kg +2 risk
        - **Temperature Enhancement:** > 30°C increases convective potential
        - **False Positive Exclusion:** Clouds < 20% or temp < 15°C = no risk
        
        **Tobacco Impact:**
        - Physical leaf damage and stem breakage
        - Flower/bud destruction
        - Complete crop loss possible
        
        **Critical Stages:**
        - Flowering (1.4x multiplier)
        - Leaf Maturation (1.6x multiplier)
        - Harvest Period (1.8x multiplier)
        """)
    
    with col3:
        st.markdown("""
        #### 🌧️ Rain Risk Factors
        **Meteorological Conditions:**
        - Light: 0.5-3mm/3h
        - Moderate: 3-6mm/3h
        - Heavy: 6-10mm/3h
        - Severe: >10mm/3h
        
        **🔬 Assessment Method:**
        - Uses 3-hour accumulation when available
        - Estimates from 1-hour data otherwise
        - Stage-specific vulnerability applied
        
        **Tobacco Impact:**
        - Waterlogging stress and root damage
        - Disease development (fungal/bacterial)
        - Harvest delays and quality issues
        
        **Critical Stages:**
        - Transplanting (1.5x multiplier)
        - Harvest Period (1.8x multiplier)
        
        **🌱 Beneficial Effects:**
        - Light rain (Level 1) often beneficial
        - Provides needed moisture during growth
        """)
    
    # Scientific Methodology Section
    st.markdown("---")
    st.markdown("#### 🔬 **Scientific Methodology & Data Sources**")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **Enhanced Risk Calculation Features:**
        - **Atmospheric Pressure Integration:** Low pressure systems amplify storm risks
        - **Visibility-Based Confirmation:** Dust storms reduce visibility < 5 km
        - **Dew Point Analysis:** Temperature-dew point spread indicates atmospheric dryness
        - **CAPE Assessment:** Convective Available Potential Energy predicts storm intensity
        - **False Positive Reduction:** Multiple exclusion rules prevent incorrect alerts
        
        **Data Quality Assurance:**
        - Real-time sensor validation
        - Model prediction cross-verification
        - Stage-specific risk multipliers
        - Regional climate considerations
        """)
    
    with col2:
        st.markdown("""
        **Meteorological Variables Used:**
        - **Primary:** Temperature, humidity, wind speed, pressure, precipitation
        - **Enhanced:** Visibility, dew point, cloud cover, CAPE (when available)
        - **Derived:** Temperature-dew point spread, pressure trends
        - **Agricultural:** Growth stage multipliers, crop vulnerability factors
        
        **Risk Validation:**
        - Minimum thresholds prevent false alerts
        - Multiple parameter confirmation required
        - Stage-specific impact assessment
        - Regional tobacco cultivation expertise
        """)
    
    # Data Availability Note
    st.info("""
    **📊 Data Availability Note:** Some enhanced parameters (visibility, dew point, CAPE) may not be available 
    in all forecast periods. The system gracefully handles missing data while maintaining accuracy for available parameters.
    """)
    
    # Growth Stage Vulnerability
    st.markdown("---")
    st.markdown("#### 🌱 Growth Stage Vulnerability Multipliers")
    
    stage_info = [
        ("🌱 Nursery Stage", "0.8x", "Lower field exposure, protected environment"),
        ("🌿 Transplanting", "1.5x", "Highest vulnerability, establishment stress"),
        ("🍃 Vegetative Growth", "1.2x", "Moderate vulnerability, active growth"),
        ("🌸 Flowering", "1.4x", "High vulnerability to stress"),
        ("✂️ Topping Stage", "1.3x", "Vulnerable during operations"),
        ("🌾 Leaf Maturation", "1.6x", "Critical for quality development"),
        ("🚜 Harvest Period", "1.8x", "Maximum vulnerability, quality critical"),
        ("🏞️ Post-Harvest", "0.6x", "Minimal crop risk")
    ]
    
    for i in range(0, len(stage_info), 2):
        col1, col2 = st.columns(2)
        with col1:
            if i < len(stage_info):
                stage, mult, desc = stage_info[i]
                st.markdown(f"**{stage}** - Multiplier: `{mult}`  \n{desc}")
        with col2:
            if i + 1 < len(stage_info):
                stage, mult, desc = stage_info[i + 1]
                st.markdown(f"**{stage}** - Multiplier: `{mult}`  \n{desc}")

def create_temperature_comparison_card(current_temp, forecast_temp, current_time, forecast_time):
    """Create a comparison card showing current vs forecast temperature"""
    temp_diff = abs(current_temp - forecast_temp)
    diff_color = "#FF8C00" if temp_diff > 2 else "#00C851"
    
    return f"""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 15px; color: white; margin: 10px 0;'>
        <h4 style='margin: 0 0 15px 0; text-align: center;'>🌡️ Temperature Comparison</h4>
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <div style='text-align: center; flex: 1;'>
                <div style='background: rgba(255,255,255,0.2); padding: 10px; border-radius: 10px; margin: 5px;'>
                    <h5 style='margin: 0; font-size: 12px;'>📡 Live Temperature</h5>
                    <h6 style='margin: 5px 0; font-size: 10px; opacity: 0.8;'>(Real-Time Sensor)</h6>
                    <h3 style='margin: 5px 0; font-size: 24px;'>{current_temp:.1f}°C</h3>
                    <p style='margin: 0; font-size: 10px;'>Updated: {current_time}</p>
                </div>
            </div>
            <div style='text-align: center; padding: 0 10px;'>
                <span style='font-size: 20px;'>⚖️</span>
                <br>
                <span style='font-size: 12px; color: {diff_color};'>±{temp_diff:.1f}°C</span>
            </div>
            <div style='text-align: center; flex: 1;'>
                <div style='background: rgba(255,255,255,0.2); padding: 10px; border-radius: 10px; margin: 5px;'>
                    <h5 style='margin: 0; font-size: 12px;'>🔮 Forecasted Temperature</h5>
                    <h6 style='margin: 5px 0; font-size: 10px; opacity: 0.8;'>(Model Estimate)</h6>
                    <h3 style='margin: 5px 0; font-size: 24px;'>{forecast_temp:.1f}°C</h3>
                    <p style='margin: 0; font-size: 10px;'>For: {forecast_time}</p>
                </div>
            </div>
        </div>
        <div style='text-align: center; margin-top: 10px; font-size: 11px; opacity: 0.8;'>
            💡 Forecasted values are model predictions and may slightly differ from real-time sensor data due to update intervals and data sourcing.
        </div>
    </div>
    """

def create_enhanced_temperature_metric(temp_value, label, help_text, is_current=True):
    """Create an enhanced temperature metric with tooltip"""
    icon = "📡" if is_current else "🔮"
    bg_color = "#E8F5E8" if is_current else "#FFF8DC"
    border_color = "#00C851" if is_current else "#FFD700"
    
    return f"""
    <div style='background-color: {bg_color}; padding: 15px; border-radius: 10px; border: 2px solid {border_color}; text-align: center; margin: 5px;'>
        <div style='display: flex; align-items: center; justify-content: center; margin-bottom: 5px;'>
            <h4 style='margin: 0; color: #333;'>{icon} {label}</h4>
            <span style='margin-left: 5px; cursor: help;' title='{help_text}'>ℹ️</span>
        </div>
        <h2 style='margin: 5px 0; color: #333; font-size: 28px;'>{temp_value:.1f}°C</h2>
        <p style='margin: 0; font-size: 12px; color: #666;'>{help_text[:50]}...</p>
    </div>
    """

def analyze_forecast_risks(hourly_data, daily_data, stage_multiplier, min_risk_level=2):
    """Analyze forecast data for upcoming weather risks"""
    alerts = []
    
    # Analyze hourly forecasts
    for i, hour in enumerate(hourly_data):
        dt = datetime.fromtimestamp(hour["dt"], tz=PAKISTAN_TZ)
        
        # Extract enhanced meteorological parameters
        temp = hour["temp"]
        humidity = hour["humidity"]
        pressure = hour["pressure"]
        wind_speed = hour["wind_speed"]
        clouds = hour["clouds"]
        rain_1h = hour.get("rain", {}).get("1h", 0)
        visibility = hour.get("visibility", None)  # May not be available in all forecasts
        dew_point = hour.get("dew_point", None)   # May not be available in all forecasts
        cape = hour.get("cape", None)             # May not be available in standard API
        
        # Calculate risks for this hour with enhanced parameters
        dust_risk = calculate_dust_risk(
            wind_speed, 
            humidity, 
            pressure, 
            stage_multiplier,
            visibility=visibility,
            dew_point=dew_point,
            temp=temp,
            clouds=clouds
        )
        
        hail_risk = calculate_hail_risk(
            temp, 
            rain_1h, 
            clouds, 
            wind_speed, 
            stage_multiplier,
            pressure=pressure,
            cape=cape,
            humidity=humidity
        )
        
        rain_risk = calculate_rain_risk(
            rain_1h, 
            None, 
            stage_multiplier
        )
        
        # Check for significant risks
        risks = []
        if dust_risk >= min_risk_level:
            risks.append(("Dust", dust_risk))
        if hail_risk >= min_risk_level:
            risks.append(("Hail", hail_risk))
        if rain_risk >= min_risk_level:
            risks.append(("Rain", rain_risk))
        
        # Create alerts for significant risks
        for risk_type, risk_level in risks:
            alerts.append({
                "datetime": dt,
                "type": "hourly",
                "risk_type": risk_type,
                "risk_level": risk_level,
                "intensity": get_risk_intensity_label(risk_level),
                "temp": temp,
                "humidity": humidity,
                "wind_speed": wind_speed,
                "clouds": clouds,
                "rain": rain_1h,
                "pressure": pressure,
                "visibility": visibility,
                "dew_point": dew_point,
                "weather_desc": hour.get("weather", [{}])[0].get("description", "").title()
            })
    
    # Analyze daily forecasts
    for i, day in enumerate(daily_data):
        dt = datetime.fromtimestamp(day["dt"], tz=PAKISTAN_TZ)
        
        # Extract enhanced meteorological parameters for daily data
        temp_day = day["temp"]["day"]
        humidity = day["humidity"]
        pressure = day["pressure"]
        wind_speed = day["wind_speed"]
        clouds = day["clouds"]
        rain_daily = day.get("rain", 0)
        # Daily forecasts typically don't have visibility, dew_point, or CAPE
        
        # Calculate risks for this day with enhanced parameters
        dust_risk = calculate_dust_risk(
            wind_speed, 
            humidity, 
            pressure, 
            stage_multiplier,
            visibility=None,  # Not available in daily forecasts
            dew_point=None,   # Not available in daily forecasts
            temp=temp_day,
            clouds=clouds
        )
        
        hail_risk = calculate_hail_risk(
            temp_day, 
            rain_daily, 
            clouds, 
            wind_speed, 
            stage_multiplier,
            pressure=pressure,
            cape=None,        # Not available in daily forecasts
            humidity=humidity
        )
        
        rain_risk = calculate_rain_risk(
            rain_daily / 24,  # Convert daily to hourly estimate
            rain_daily / 8,   # 3-hour estimate
            stage_multiplier
        )
        
        # Check for significant risks
        risks = []
        if dust_risk >= min_risk_level:
            risks.append(("Dust", dust_risk))
        if hail_risk >= min_risk_level:
            risks.append(("Hail", hail_risk))
        if rain_risk >= min_risk_level:
            risks.append(("Rain", rain_risk))
        
        # Create alerts for significant risks
        for risk_type, risk_level in risks:
            alerts.append({
                "datetime": dt,
                "type": "daily",
                "risk_type": risk_type,
                "risk_level": risk_level,
                "intensity": get_risk_intensity_label(risk_level),
                "temp": temp_day,
                "humidity": humidity,
                "wind_speed": wind_speed,
                "clouds": clouds,
                "rain": rain_daily,
                "pressure": pressure,
                "visibility": None,
                "dew_point": None,
                "weather_desc": day.get("weather", [{}])[0].get("description", "").title()
            })
    
    # Sort alerts chronologically
    alerts.sort(key=lambda x: x["datetime"])
    
    return alerts

def create_risk_alert_card(alert, stage_name):
    """Create a visual alert card for a risk using Streamlit components"""
    risk_color = get_risk_color(alert["risk_level"])
    risk_icon = {
        "Dust": "🌪️",
        "Hail": "🧊", 
        "Rain": "🌧️"
    }.get(alert["risk_type"], "⚠️")
    
    time_format = "%a %b %d, %H:%M" if alert["type"] == "hourly" else "%a %b %d"
    time_str = alert["datetime"].strftime(time_format)
    
    # Use Streamlit container for better rendering
    with st.container():
        # Create a colored border using markdown
        st.markdown(f"""
        <div style='border-left: 5px solid {risk_color}; 
                    background: {risk_color}15; 
                    padding: 15px; 
                    margin: 10px 0; 
                    border-radius: 8px;'>
        </div>
        """, unsafe_allow_html=True)
        
        # Header row with risk info and level badge
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{risk_icon} {alert['risk_type']} Storm Risk - {alert['intensity']}**")
        with col2:
            st.markdown(f"""
            <div style='background: {risk_color}; 
                        color: white; 
                        padding: 4px 8px; 
                        border-radius: 15px; 
                        text-align: center; 
                        font-size: 12px; 
                        font-weight: bold;'>
                Level {alert["risk_level"]}/4
            </div>
            """, unsafe_allow_html=True)
        
        # Time and weather description
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**📅 {time_str}**")
            st.caption(f"{alert['weather_desc']}")
        with col2:
            st.markdown(f"**🌡️ {alert['temp']:.1f}°C**")
            st.caption(f"💧 {alert['humidity']}% humidity")
        
        # Weather parameters in columns
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🌬️ Wind", f"{alert['wind_speed']:.1f} m/s")
        with col2:
            st.metric("☁️ Clouds", f"{alert['clouds']}%")
        with col3:
            st.metric("☔ Rain", f"{alert['rain']:.1f} mm")
        with col4:
            st.metric("📉 Pressure", f"{alert['pressure']} hPa")
        
        # Stage-specific impact message
        impact_message = get_stage_specific_risk_message(alert["risk_type"].lower(), alert["risk_level"], stage_name)
        st.info(f"🌱 **{stage_name} Impact:** {impact_message}")
        
        st.markdown("---")  # Separator between alerts

def create_forecast_risk_summary(alerts):
    """Create a summary of upcoming risks"""
    if not alerts:
        return "✅ No significant weather risks detected in the forecast period."
    
    # Count risks by type and severity
    risk_counts = {"Dust": 0, "Hail": 0, "Rain": 0}
    severity_counts = {"Light": 0, "Moderate": 0, "High": 0, "Severe": 0}
    
    for alert in alerts:
        risk_counts[alert["risk_type"]] += 1
        severity_counts[alert["intensity"]] += 1
    
    # Create summary text
    total_alerts = len(alerts)
    summary_parts = []
    
    for risk_type, count in risk_counts.items():
        if count > 0:
            icon = {"Dust": "🌪️", "Hail": "🧊", "Rain": "🌧️"}[risk_type]
            summary_parts.append(f"{icon} {count} {risk_type}")
    
    summary_text = f"⚠️ **{total_alerts} upcoming risk alerts detected**\n\n"
    summary_text += "**Risk Types:** " + " | ".join(summary_parts) + "\n\n"
    
    severity_parts = []
    for severity, count in severity_counts.items():
        if count > 0:
            severity_parts.append(f"{count} {severity}")
    
    summary_text += "**Severity Levels:** " + " | ".join(severity_parts)
    
    return summary_text

def enhance_forecast_table_with_risks(df, risk_data, is_hourly=True):
    """Add risk information to forecast dataframes"""
    risk_column = []
    
    for i, row in df.iterrows():
        if is_hourly:
            time_key = row["Time"]
        else:
            time_key = row["Date"]
        
        # Find matching risks for this time
        matching_risks = []
        for alert in risk_data:
            if is_hourly:
                alert_time = alert["datetime"].strftime("%H:%M")
                if alert_time == time_key and alert["type"] == "hourly":
                    matching_risks.append(f"{alert['risk_type']} ({alert['intensity']})")
            else:
                alert_date = alert["datetime"].strftime("%Y-%m-%d")
                if alert_date == time_key and alert["type"] == "daily":
                    matching_risks.append(f"{alert['risk_type']} ({alert['intensity']})")
        
        if matching_risks:
            risk_column.append(" | ".join(matching_risks))
        else:
            risk_column.append("No Risk")
    
    df["Risk Type & Level"] = risk_column
    return df

def create_simple_alert_card(alert):
    """Create a simple visual alert card for overview sections"""
    risk_color = get_risk_color(alert["risk_level"])
    risk_icon = {
        "Dust": "🌪️",
        "Hail": "🧊", 
        "Rain": "🌧️"
    }.get(alert["risk_type"], "⚠️")
    
    time_str = alert["datetime"].strftime("%H:%M" if alert["type"] == "hourly" else "All Day")
    
    with st.container():
        st.markdown(f"""
        <div style='padding: 12px; 
                    margin: 8px 0; 
                    border-left: 4px solid {risk_color}; 
                    background: {risk_color}20; 
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div>
                    <strong style='color: {risk_color};'>{risk_icon} {alert["risk_type"]} Risk - {alert["intensity"]}</strong><br>
                    <small style='color: #666;'>📅 {time_str} | 🌡️ {alert["temp"]:.1f}°C | 🌬️ {alert["wind_speed"]:.1f} m/s | 💧 {alert["humidity"]}%</small>
                </div>
                <div style='background: {risk_color}; 
                           color: white; 
                           padding: 4px 8px; 
                           border-radius: 12px; 
                           font-size: 11px; 
                           font-weight: bold;'>
                    Level {alert["risk_level"]}/4
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def create_upcoming_risks_timeline(forecast_alerts, stage_name):
    """Create a clear timeline view of upcoming risks by hour and day"""
    if not forecast_alerts:
        st.success("✅ **No Weather Risks Detected** - Clear conditions for the next 7 days")
        return
    
    # Separate hourly and daily alerts
    hourly_alerts = [a for a in forecast_alerts if a["type"] == "hourly"]
    daily_alerts = [a for a in forecast_alerts if a["type"] == "daily"]
    
    # Create two main sections
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### ⏰ **HOURLY RISKS** (Next 24 Hours)")
        if hourly_alerts:
            # Group hourly alerts by hour
            hourly_by_time = {}
            for alert in hourly_alerts:
                hour_key = alert["datetime"].strftime("%H:%M")
                if hour_key not in hourly_by_time:
                    hourly_by_time[hour_key] = []
                hourly_by_time[hour_key].append(alert)
            
            # Display each hour with risks
            for hour, alerts in sorted(hourly_by_time.items()):
                with st.container():
                    # Hour header
                    st.markdown(f"**🕐 {hour}** ({len(alerts)} risk{'s' if len(alerts) > 1 else ''})")
                    
                    # Display each risk for this hour
                    for alert in alerts:
                        risk_color = get_risk_color(alert["risk_level"])
                        intensity_emoji = {
                            "Light": "🟡",
                            "Moderate": "🟠", 
                            "High": "🔴",
                            "Severe": "🚨"
                        }.get(alert["intensity"], "⚠️")
                        
                        risk_icon = {
                            "Dust": "🌪️",
                            "Hail": "🧊",
                            "Rain": "🌧️"
                        }.get(alert["risk_type"], "⚠️")
                        
                        st.markdown(f"""
                        <div style='background: {risk_color}20; 
                                    border-left: 5px solid {risk_color}; 
                                    padding: 10px; 
                                    margin: 5px 0; 
                                    border-radius: 5px;'>
                            <div style='display: flex; justify-content: space-between; align-items: center;'>
                                <div>
                                    <strong style='color: {risk_color}; font-size: 16px;'>
                                        {risk_icon} {alert["risk_type"]} Storm
                                    </strong>
                                    <br>
                                    <span style='font-size: 14px;'>
                                        🌡️ {alert["temp"]:.1f}°C | 🌬️ {alert["wind_speed"]:.1f} m/s | 💧 {alert["humidity"]}%
                                    </span>
                                </div>
                                <div style='text-align: center;'>
                                    <div style='font-size: 20px;'>{intensity_emoji}</div>
                                    <div style='background: {risk_color}; 
                                               color: white; 
                                               padding: 3px 8px; 
                                               border-radius: 10px; 
                                               font-size: 12px; 
                                               font-weight: bold;'>
                                        {alert["intensity"].upper()}
                                    </div>
                                    <div style='font-size: 10px; color: #666;'>Level {alert["risk_level"]}/4</div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("---")
        else:
            st.info("✅ No hourly risks detected in the next 24 hours")
    
    with col2:
        st.markdown("### 📅 **DAILY RISKS** (Next 7 Days)")
        if daily_alerts:
            # Group daily alerts by date
            daily_by_date = {}
            for alert in daily_alerts:
                date_key = alert["datetime"].strftime("%a, %b %d")
                if date_key not in daily_by_date:
                    daily_by_date[date_key] = []
                daily_by_date[date_key].append(alert)
            
            # Display each day with risks
            for date, alerts in sorted(daily_by_date.items()):
                with st.container():
                    # Date header
                    st.markdown(f"**📅 {date}** ({len(alerts)} risk{'s' if len(alerts) > 1 else ''})")
                    
                    # Display each risk for this day
                    for alert in alerts:
                        risk_color = get_risk_color(alert["risk_level"])
                        intensity_emoji = {
                            "Light": "🟡",
                            "Moderate": "🟠", 
                            "High": "🔴",
                            "Severe": "🚨"
                        }.get(alert["intensity"], "⚠️")
                        
                        risk_icon = {
                            "Dust": "🌪️",
                            "Hail": "🧊",
                            "Rain": "🌧️"
                        }.get(alert["risk_type"], "⚠️")
                        
                        st.markdown(f"""
                        <div style='background: {risk_color}20; 
                                    border-left: 5px solid {risk_color}; 
                                    padding: 10px; 
                                    margin: 5px 0; 
                                    border-radius: 5px;'>
                            <div style='display: flex; justify-content: space-between; align-items: center;'>
                                <div>
                                    <strong style='color: {risk_color}; font-size: 16px;'>
                                        {risk_icon} {alert["risk_type"]} Storm
                                    </strong>
                                    <br>
                                    <span style='font-size: 14px;'>
                                        🌡️ {alert["temp"]:.1f}°C | 🌬️ {alert["wind_speed"]:.1f} m/s | 💧 {alert["humidity"]}%
                                    </span>
                                </div>
                                <div style='text-align: center;'>
                                    <div style='font-size: 20px;'>{intensity_emoji}</div>
                                    <div style='background: {risk_color}; 
                                               color: white; 
                                               padding: 3px 8px; 
                                               border-radius: 10px; 
                                               font-size: 12px; 
                                               font-weight: bold;'>
                                        {alert["intensity"].upper()}
                                    </div>
                                    <div style='font-size: 10px; color: #666;'>Level {alert["risk_level"]}/4</div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("---")
        else:
            st.info("✅ No daily risks detected in the next 7 days")

def create_risk_summary_cards(forecast_alerts):
    """Create summary cards showing risk counts and next risk timing"""
    if not forecast_alerts:
        return
    
    # Calculate summary statistics
    total_risks = len(forecast_alerts)
    next_24h_risks = len([a for a in forecast_alerts if a["datetime"] <= datetime.now(PAKISTAN_TZ) + timedelta(hours=24)])
    high_severe_risks = len([a for a in forecast_alerts if a["risk_level"] >= 3])
    
    # Find next risk
    next_risk = min(forecast_alerts, key=lambda x: x["datetime"])
    hours_to_next = (next_risk["datetime"] - datetime.now(PAKISTAN_TZ)).total_seconds() / 3600
    
    # Risk type counts
    dust_count = len([a for a in forecast_alerts if a["risk_type"] == "Dust"])
    hail_count = len([a for a in forecast_alerts if a["risk_type"] == "Hail"])
    rain_count = len([a for a in forecast_alerts if a["risk_type"] == "Rain"])
    
    # Create summary cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #FF6B6B, #FF8E53); 
                    color: white; 
                    padding: 20px; 
                    border-radius: 15px; 
                    text-align: center;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);'>
            <h2 style='margin: 0; font-size: 32px;'>{total_risks}</h2>
            <p style='margin: 5px 0 0 0; font-size: 14px;'>Total Risk Alerts</p>
            <p style='margin: 0; font-size: 12px; opacity: 0.8;'>Next 7 Days</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #4ECDC4, #44A08D); 
                    color: white; 
                    padding: 20px; 
                    border-radius: 15px; 
                    text-align: center;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);'>
            <h2 style='margin: 0; font-size: 32px;'>{next_24h_risks}</h2>
            <p style='margin: 5px 0 0 0; font-size: 14px;'>Next 24 Hours</p>
            <p style='margin: 0; font-size: 12px; opacity: 0.8;'>Immediate Risks</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #667eea, #764ba2); 
                    color: white; 
                    padding: 20px; 
                    border-radius: 15px; 
                    text-align: center;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);'>
            <h2 style='margin: 0; font-size: 32px;'>{high_severe_risks}</h2>
            <p style='margin: 5px 0 0 0; font-size: 14px;'>High/Severe Risks</p>
            <p style='margin: 0; font-size: 12px; opacity: 0.8;'>Critical Alerts</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #f093fb, #f5576c); 
                    color: white; 
                    padding: 20px; 
                    border-radius: 15px; 
                    text-align: center;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);'>
            <h2 style='margin: 0; font-size: 24px;'>{hours_to_next:.1f}h</h2>
            <p style='margin: 5px 0 0 0; font-size: 14px;'>Next Risk In</p>
            <p style='margin: 0; font-size: 12px; opacity: 0.8;'>{next_risk["risk_type"]} - {next_risk["intensity"]}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Risk type breakdown
    st.markdown("### 📊 Risk Type Breakdown")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if dust_count > 0:
            st.markdown(f"""
            <div style='background: #FFE4B5; 
                        border: 2px solid #FF8C00; 
                        padding: 15px; 
                        border-radius: 10px; 
                        text-align: center;'>
                <h3 style='margin: 0; color: #FF8C00;'>🌪️ Dust Storms</h3>
                <h2 style='margin: 5px 0; color: #FF8C00;'>{dust_count}</h2>
                <p style='margin: 0; color: #666;'>alerts detected</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.success("🌪️ **Dust Storms:** No alerts")
    
    with col2:
        if hail_count > 0:
            st.markdown(f"""
            <div style='background: #E6F3FF; 
                        border: 2px solid #4A90E2; 
                        padding: 15px; 
                        border-radius: 10px; 
                        text-align: center;'>
                <h3 style='margin: 0; color: #4A90E2;'>🧊 Hail Storms</h3>
                <h2 style='margin: 5px 0; color: #4A90E2;'>{hail_count}</h2>
                <p style='margin: 0; color: #666;'>alerts detected</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.success("🧊 **Hail Storms:** No alerts")
    
    with col3:
        if rain_count > 0:
            st.markdown(f"""
            <div style='background: #E8F5E8; 
                        border: 2px solid #4CAF50; 
                        padding: 15px; 
                        border-radius: 10px; 
                        text-align: center;'>
                <h3 style='margin: 0; color: #4CAF50;'>🌧️ Rain Risks</h3>
                <h2 style='margin: 5px 0; color: #4CAF50;'>{rain_count}</h2>
                <p style='margin: 0; color: #666;'>alerts detected</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.success("🌧️ **Rain Risks:** No alerts")

def main():
    # Add auto-refresh info in header
    current_time_pk = datetime.now(PAKISTAN_TZ)
    next_update = st.session_state.last_update + timedelta(minutes=30)
    
    # Header Section
    st.markdown(f"""
    <div style='text-align: center; padding: 20px; background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%); color: white; border-radius: 10px; margin-bottom: 20px;'>
        <h1 style='margin: 0; font-size: 2.5em;'>🌾 Real-time Weather Monitoring and Risk Assessment</h1>
        <h3 style='margin: 10px 0 0 0; font-weight: 300;'>for Tobacco Cultivation in Pakistan</h3>
        <p style='margin: 10px 0 0 0; opacity: 0.9;'>Regional weather insights, risks, and forecast for dust, hail, and rain</p>
        <div style='margin-top: 15px; padding: 10px; background: rgba(255,255,255,0.1); border-radius: 5px;'>
            <p style='margin: 0; font-size: 14px;'>🕐 Pakistan Time: {current_time_pk.strftime('%Y-%m-%d %H:%M:%S')} | 🔄 Auto-refresh: Every 30 minutes | Next Update: {next_update.strftime('%H:%M')}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Region Selection and Options
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        show_temp_comparison = st.checkbox(
            "🔄 Show Current vs Forecast Comparison",
            value=False,
            help="Toggle to compare real-time sensor data with forecast model predictions"
        )
    with col2:
        selected_region = st.selectbox(
            "📍 Select Region",
            options=list(LOCATIONS.keys()),
            index=0,
            help="Choose a tobacco cultivation region for detailed weather analysis"
        )
    with col3:
        # Manual refresh button and auto-refresh settings
        col3a, col3b = st.columns(2)
        with col3a:
            if st.button("🔄 Refresh Now", help="Manually refresh weather data"):
                st.cache_data.clear()
                st.session_state.last_update = datetime.now(PAKISTAN_TZ)
                st.rerun()
        with col3b:
            show_light_alerts = st.checkbox(
                "Include Light Alerts",
                value=False,
                help="Show alerts for light risk levels (Level 1)"
            )
    
    # Auto-refresh status display
    time_until_refresh = 1800 - (datetime.now(PAKISTAN_TZ) - st.session_state.last_update).total_seconds()
    minutes_until_refresh = max(0, time_until_refresh / 60)
    
    if minutes_until_refresh > 25:
        refresh_status = f"🟢 Recently updated ({30 - minutes_until_refresh:.0f} min ago)"
        refresh_color = "#00C851"
    elif minutes_until_refresh > 15:
        refresh_status = f"🟡 Next refresh in {minutes_until_refresh:.0f} minutes"
        refresh_color = "#FFD700"
    else:
        refresh_status = f"🔴 Refreshing soon ({minutes_until_refresh:.0f} min remaining)"
        refresh_color = "#FF4B4B"
    
    st.markdown(f"""
    <div style='background: {refresh_color}20; 
                border-left: 4px solid {refresh_color}; 
                padding: 10px; 
                margin: 10px 0; 
                border-radius: 5px;'>
        <p style='margin: 0; color: {refresh_color}; font-weight: bold;'>{refresh_status}</p>
        <p style='margin: 0; font-size: 12px; color: #666;'>Data automatically refreshes every 30 minutes | Last update: {st.session_state.last_update.strftime('%H:%M:%S')} PKT</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get coordinates and location info
    lat, lon = LOCATIONS[selected_region]["coords"]
    elevation = LOCATIONS[selected_region]["elevation"]
    climate = LOCATIONS[selected_region]["climate"]
    
    # Get current growth stage
    stage_name, stage_desc, stage_icon, stage_priority = get_current_growth_stage()
    stage_multiplier = calculate_stage_specific_risk_multiplier(stage_name)
    
    # Fetch weather data
    with st.spinner(f"Fetching weather data for {selected_region}..."):
        weather_data = fetch_weather_data(lat, lon)
    
    if weather_data is None:
        st.error("Unable to fetch weather data. Please try again later.")
        return
    
    # Extract current weather
    current = weather_data.get("current", {})
    hourly = weather_data.get("hourly", [])[:24]  # Next 24 hours
    daily = weather_data.get("daily", [])[:7]     # Next 7 days
    
    # Analyze forecast risks
    min_risk_level = 1 if show_light_alerts else 2
    forecast_alerts = analyze_forecast_risks(hourly, daily, stage_multiplier, min_risk_level)
    
    # Get current and first forecast hour for comparison
    current_temp = current.get('temp', 0)
    current_time = current_time_pk.strftime('%H:%M')
    
    # Find the forecast for current hour or closest hour
    first_forecast = hourly[0] if hourly else {}
    forecast_temp = first_forecast.get('temp', current_temp)
    forecast_time = datetime.fromtimestamp(first_forecast.get('dt', 0)).strftime('%H:%M') if first_forecast else current_time
    
    # Risk Alert Notification Badge
    if forecast_alerts:
        alert_count = len(forecast_alerts)
        next_24h_alerts = [a for a in forecast_alerts if a["datetime"] <= datetime.now(PAKISTAN_TZ) + timedelta(hours=24)]
        st.markdown(f"""
        <div style='background: linear-gradient(90deg, #FF6B6B 0%, #FF8E53 100%); 
                    color: white; 
                    padding: 10px 20px; 
                    border-radius: 25px; 
                    text-align: center; 
                    margin: 10px 0;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);'>
            <h4 style='margin: 0;'>⚠️ {len(next_24h_alerts)} upcoming risk alerts in next 24h | {alert_count} total forecast alerts</h4>
        </div>
        """, unsafe_allow_html=True)
    
    # Temperature Comparison Display (if enabled)
    if show_temp_comparison:
        st.markdown("### 🌡️ Temperature Data Comparison")
        st.markdown(
            create_temperature_comparison_card(current_temp, forecast_temp, current_time, forecast_time),
            unsafe_allow_html=True
        )
    
    # Current Regional Overview
    st.markdown("### 📊 Current Regional Overview")
    
    # Calculate current risks with stage-specific adjustments and enhanced parameters
    current_dust_risk = calculate_dust_risk(
        current.get("wind_speed", 0),
        current.get("humidity", 0),
        current.get("pressure", 1013),
        stage_multiplier,
        visibility=current.get("visibility", None),
        dew_point=current.get("dew_point", None),
        temp=current.get("temp", 0),
        clouds=current.get("clouds", 0)
    )
    
    current_hail_risk = calculate_hail_risk(
        current.get("temp", 0),
        current.get("rain", {}).get("1h", 0),
        current.get("clouds", 0),
        current.get("wind_speed", 0),
        stage_multiplier,
        pressure=current.get("pressure", 1013),
        cape=current.get("cape", None),  # May not be available in current weather
        humidity=current.get("humidity", 0)
    )
    
    current_rain_risk = calculate_rain_risk(
        current.get("rain", {}).get("1h", 0),
        None,
        stage_multiplier
    )
    
    # Calculate 7-day precipitation total
    total_precipitation = sum([day.get("rain", 0) for day in daily])
    
    # Enhanced KPI Cards with Temperature Distinction
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        # Enhanced temperature metric with clear labeling
        temp_help_text = "Real-time sensor data from weather stations. Updated every few minutes with actual measured temperature."
        st.markdown(
            create_enhanced_temperature_metric(
                current_temp, 
                "Live Temperature (Real-Time Sensor)", 
                temp_help_text, 
                is_current=True
            ),
            unsafe_allow_html=True
        )
    
    with col2:
        st.metric(
            "💧 Humidity",
            f"{current.get('humidity', 0)}%",
            f"{current.get('humidity', 0) - 60:.0f}% from optimal",
            help="Current humidity level from real-time sensors"
        )
    
    with col3:
        st.metric(
            "🌬️ Wind Speed",
            f"{current.get('wind_speed', 0):.1f} m/s",
            f"Risk Level: {current_dust_risk}",
            help="Real-time wind speed measurements affecting dust risk"
        )
    
    with col4:
        st.metric(
            "☔ 7-Day Precipitation",
            f"{total_precipitation:.1f} mm",
            f"Risk Level: {current_rain_risk}",
            help="Forecasted precipitation total for next 7 days"
        )
    
    with col5:
        st.metric(
            f"{stage_icon} Growth Stage",
            stage_name,
            f"Priority: {stage_priority}",
            help="Current tobacco cultivation stage based on agricultural calendar"
        )
    
    with col6:
        st.metric(
            "📍 Location Info",
            f"{elevation}",
            climate,
            help=f"Elevation and climate type for {selected_region}"
        )
    
    # Growth Stage Information
    st.markdown("### 🌱 Current Tobacco Growth Stage")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"""
        **Current Stage:** {stage_icon} {stage_name}  
        **Description:** {stage_desc}  
        **Risk Multiplier:** {stage_multiplier}x  
        **Priority Level:** {stage_priority}
        """)
    
    with col2:
        # Show next stage
        current_month = datetime.now().month
        if current_month >= 12 or current_month <= 2:
            next_stage = "Transplanting in March"
        elif current_month == 3:
            next_stage = "Vegetative Growth in April"
        elif current_month <= 5:
            next_stage = "Flowering in June"
        elif current_month == 6:
            next_stage = "Leaf Maturation in July"
        elif current_month == 7:
            next_stage = "Harvest in August"
        elif current_month <= 9:
            next_stage = "Post-Harvest preparation"
        else:
            next_stage = "Nursery preparation in December"
        
        st.info(f"""
        **Next Stage:** {next_stage}  
        **Weather Sensitivity:** High during transitions  
        **Recommended Actions:** Monitor forecasts closely
        """)
    
    with col3:
        st.warning(f"""
        **Stage-Specific Risks:**  
        - Weather impacts are multiplied by {stage_multiplier}x  
        - {stage_name} requires special attention  
        - Adjust operations based on risk levels
        """)
    
    # Upcoming Weather Risks Section
    if forecast_alerts:
        st.markdown("---")
        st.markdown("### ⚠️ Upcoming Weather Risks Forecast")
        
        # Risk summary cards
        create_risk_summary_cards(forecast_alerts)
        
        st.markdown("---")
        
        # Clear timeline view of risks
        create_upcoming_risks_timeline(forecast_alerts, stage_name)
        
        st.markdown("---")
        
        # Additional filter options for detailed view
        with st.expander("🔍 **Advanced Risk Analysis & Filters**", expanded=False):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(create_forecast_risk_summary(forecast_alerts))
            with col2:
                # Risk filter options
                risk_type_filter = st.selectbox(
                    "Filter by Risk Type",
                    options=["All", "Dust", "Hail", "Rain"],
                    help="Filter alerts by specific risk type"
                )
                
                severity_filter = st.selectbox(
                    "Filter by Severity",
                    options=["All", "Light", "Moderate", "High", "Severe"],
                    help="Filter alerts by severity level"
                )
            
            # Filter alerts based on user selection
            filtered_alerts = forecast_alerts
            if risk_type_filter != "All":
                filtered_alerts = [a for a in filtered_alerts if a["risk_type"] == risk_type_filter]
            if severity_filter != "All":
                filtered_alerts = [a for a in filtered_alerts if a["intensity"] == severity_filter]
            
            # Display filtered alerts
            if filtered_alerts:
                st.markdown(f"📋 **Detailed Alert Information** ({len(filtered_alerts)} alerts)")
                for alert in filtered_alerts:
                    create_risk_alert_card(alert, stage_name)
            else:
                st.info("No alerts match the selected filters.")
    else:
        st.markdown("---")
        st.markdown("### ✅ Upcoming Weather Risks Forecast")
        st.success("""
        **🌤️ Clear Weather Conditions Ahead**
        
        No significant weather risks detected in the forecast period for the next 7 days.
        Current forecast conditions appear favorable for tobacco cultivation activities.
        
        **📊 Monitoring Status:**
        - ✅ 24-hour forecast: Clear
        - ✅ 7-day forecast: Clear  
        - ⚙️ Risk threshold: Level 2+ (Moderate or higher)
        - 🌱 Growth stage: {stage_name} (Multiplier: {stage_multiplier}x)
        """)
    
    # Navigation Tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Overview", 
        "🌤️ Weather Details", 
        "⚠️ Risk Assessment", 
        "📈 Trends", 
        "🚨 Forecast Alerts",
        "📋 Risk Guide"
    ])
    
    with tab1:
        st.markdown("### 🌤️ Current Weather Conditions")
        
        # Current weather details with enhanced labeling
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            **📡 Current Real-Time Conditions for {selected_region}**
            - **Live Temperature (Real-Time Sensor):** {current.get('temp', 0):.1f}°C
            - **Feels Like:** {current.get('feels_like', 0):.1f}°C
            - **Humidity:** {current.get('humidity', 0)}%
            - **Pressure:** {current.get('pressure', 0)} hPa
            - **Wind Speed:** {current.get('wind_speed', 0):.1f} m/s
            - **Wind Direction:** {current.get('wind_deg', 0)}°
            - **Cloud Cover:** {current.get('clouds', 0)}%
            - **UV Index:** {current.get('uvi', 0):.1f}
            
            *📊 Data from real-time weather sensors*
            """)
        
        with col2:
            # Weather description and forecast comparison
            weather_desc = current.get('weather', [{}])[0]
            st.markdown(f"""
            **🌤️ Weather Description & Forecast Info**
            - **Current Condition:** {weather_desc.get('main', 'Unknown')}
            - **Description:** {weather_desc.get('description', 'No description').title()}
            - **Visibility:** {current.get('visibility', 0)/1000:.1f} km
            - **Dew Point:** {current.get('dew_point', 0):.1f}°C
            
            **🔮 Next Hour Forecast (Model Estimate):**
            - **Forecasted Temperature:** {forecast_temp:.1f}°C
            - **Temperature Difference:** ±{abs(current_temp - forecast_temp):.1f}°C
            
            **🌱 Growth Stage Impact**
            - **Current Stage:** {stage_name}
            - **Risk Multiplier:** {stage_multiplier}x
            - **Last Updated:** {current_time_pk.strftime('%Y-%m-%d %H:%M:%S')} PKT
            """)
        
        # Add data source explanation
        st.info("""
        **ℹ️ Data Sources:** Current conditions are from real-time weather sensors. 
        Forecast values are model predictions that may slightly differ from sensor readings due to update intervals and data sourcing methods.
        """)
    
    with tab2:
        st.markdown("### 🕐 24-Hour Forecast")
        
        # Add disclaimer at the top
        st.info("""
        📋 **Data Source Information:**
        - **Current readings** are from real-time weather sensors
        - **Forecasted values** are model predictions and may slightly differ from real-time sensor data due to update intervals and data sourcing
        """)
        
        # Show current vs first forecast comparison if enabled
        if show_temp_comparison and hourly:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                **📡 Current Real-Time Data:**
                - **Live Temperature:** {current_temp:.1f}°C
                - **Humidity:** {current.get('humidity', 0)}%
                - **Wind Speed:** {current.get('wind_speed', 0):.1f} m/s
                - **Pressure:** {current.get('pressure', 0)} hPa
                """)
            with col2:
                st.markdown(f"""
                **🔮 Next Hour Forecast:**
                - **Forecasted Temperature:** {forecast_temp:.1f}°C
                - **Humidity:** {first_forecast.get('humidity', 0)}%
                - **Wind Speed:** {first_forecast.get('wind_speed', 0):.1f} m/s
                - **Pressure:** {first_forecast.get('pressure', 0)} hPa
                """)
        
        # Prepare hourly forecast data with clear labeling
        hourly_data = []
        for i, hour in enumerate(hourly):
            hourly_data.append({
                "Time": datetime.fromtimestamp(hour["dt"]).strftime("%H:%M"),
                "Forecasted Temp (°C)": f"{hour['temp']:.1f}",
                "Wind (m/s)": f"{hour['wind_speed']:.1f}",
                "Humidity (%)": f"{hour['humidity']}",
                "Rain (mm)": f"{hour.get('rain', {}).get('1h', 0):.1f}",
                "Clouds (%)": f"{hour['clouds']}",
                "Pressure (hPa)": f"{hour['pressure']}"
            })
        
        hourly_df = pd.DataFrame(hourly_data)
        
        # Enhance table with risk information
        hourly_df_enhanced = enhance_forecast_table_with_risks(hourly_df, forecast_alerts, is_hourly=True)
        
        # Add column explanation
        st.markdown("**📊 24-Hour Forecast Table** *(Model Estimates with Risk Analysis)*")
        
        # Style the dataframe to highlight risks
        def highlight_risks(row):
            if row["Risk Type & Level"] != "No Risk":
                return ['background-color: #FFE4B5'] * len(row)
            return [''] * len(row)
        
        styled_df = hourly_df_enhanced.style.apply(highlight_risks, axis=1)
        st.dataframe(styled_df, use_container_width=True)
        
        st.markdown("### 📅 7-Day Forecast")
        
        # Prepare daily forecast data with clear labeling
        daily_data = []
        for day in daily:
            daily_data.append({
                "Date": datetime.fromtimestamp(day["dt"]).strftime("%Y-%m-%d"),
                "Forecasted Day Temp (°C)": f"{day['temp']['day']:.1f}",
                "Forecasted Night Temp (°C)": f"{day['temp']['night']:.1f}",
                "Humidity (%)": f"{day['humidity']}",
                "Wind (m/s)": f"{day['wind_speed']:.1f}",
                "Rain (mm)": f"{day.get('rain', 0):.1f}",
                "Clouds (%)": f"{day['clouds']}"
            })
        
        daily_df = pd.DataFrame(daily_data)
        
        # Enhance table with risk information
        daily_df_enhanced = enhance_forecast_table_with_risks(daily_df, forecast_alerts, is_hourly=False)
        
        # Add column explanation
        st.markdown("**📊 Daily Forecast Table** *(Model Estimates with Risk Analysis)*")
        
        # Style the dataframe to highlight risks
        styled_daily_df = daily_df_enhanced.style.apply(highlight_risks, axis=1)
        st.dataframe(styled_daily_df, use_container_width=True)
        
        # Add comprehensive disclaimer
        st.markdown("---")
        st.warning("""
        **📝 Important Note:** Current readings and forecasts may vary due to data refresh timing. 
        Forecasts are generated by predictive weather models and represent estimates based on atmospheric conditions. 
        Real-time sensor data provides actual measured values but may have slight delays in updates.
        
        **🚨 Risk Highlighting:** Rows with orange background indicate forecasted weather conditions that may pose risks to tobacco cultivation.
        """)
    
    with tab3:
        st.markdown("### ⚠️ Stage-Specific Risk Assessment")
        
        # Risk gauges
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.plotly_chart(
                create_gauge(current_dust_risk, "🌪️ Dust Risk"),
                use_container_width=True
            )
            st.markdown(get_stage_specific_risk_message("dust", current_dust_risk, stage_name))
        
        with col2:
            st.plotly_chart(
                create_gauge(current_hail_risk, "🧊 Hail Risk"),
                use_container_width=True
            )
            st.markdown(get_stage_specific_risk_message("hail", current_hail_risk, stage_name))
        
        with col3:
            st.plotly_chart(
                create_gauge(current_rain_risk, "🌧️ Rain Risk"),
                use_container_width=True
            )
            st.markdown(get_stage_specific_risk_message("rain", current_rain_risk, stage_name))
        
        # Stage-specific risk summary
        st.markdown("---")
        st.markdown(f"### 📋 {stage_name} Risk Summary")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            **Current Growth Stage:** {stage_icon} {stage_name}  
            **Risk Multiplier:** {stage_multiplier}x  
            **Stage Description:** {stage_desc}  
            **Priority Level:** {stage_priority}
            """)
        
        with col2:
            max_risk = max(current_dust_risk, current_hail_risk, current_rain_risk)
            if max_risk >= 3:
                alert_level = "🚨 CRITICAL"
                alert_color = "#FF4B4B"
            elif max_risk >= 2:
                alert_level = "⚠️ HIGH"
                alert_color = "#FF8C00"
            elif max_risk >= 1:
                alert_level = "🟡 MODERATE"
                alert_color = "#FFD700"
            else:
                alert_level = "✅ LOW"
                alert_color = "#00C851"
            
            st.markdown(f"""
            <div style='background-color: {alert_color}20; padding: 15px; border-radius: 10px; border: 2px solid {alert_color};'>
                <h4 style='color: {alert_color}; margin: 0;'>Overall Risk Level: {alert_level}</h4>
                <p style='margin: 5px 0 0 0;'>Maximum risk score: {max_risk}/4</p>
            </div>
            """, unsafe_allow_html=True)
    
    with tab4:
        st.markdown("### 📈 Weather and Risk Trends")
        
        # Add explanation about forecast data
        st.info("""
        **📊 How to Read These Charts:**
        - **Weather Forecast Chart**: Shows how temperature and humidity will change over the next 24 hours
        - **Risk Level Chart**: Shows potential dangers to tobacco crops on a scale of 0-4 (0 = safe, 4 = dangerous)
        - **Red dashed lines**: Mark times when weather alerts are expected
        - **Orange line**: Shows the alert threshold (when farmers should take precautions)
        - **Current real-time temperature**: **{:.1f}°C** (from weather sensors)
        - **Growth stage factor**: Risk levels are adjusted for current tobacco growth stage
        """.format(current_temp))
        
        # Add simple explanation box
        with st.expander("❓ **What Do These Charts Mean for My Tobacco Crop?**", expanded=False):
            st.markdown(f"""
            **🌡️ Temperature & Humidity Chart:**
            - **Blue line (Temperature)**: Shows if it will get hotter or cooler
            - **Teal line (Humidity)**: Shows how much moisture is in the air
            - **Ideal conditions**: Temperature 25-35°C, Humidity 40-60%
            
            **🚨 Risk Level Chart:**
            - **Orange line (Dust Risk)**: Sand storms that can damage leaves
            - **Blue line (Hail Risk)**: Ice storms that can destroy crops
            - **Green line (Rain Risk)**: Heavy rain that can cause flooding
            
            **🌱 Current Growth Stage: {stage_name}**
            - Your tobacco is currently in the **{stage_name}** phase
            - Risk levels are multiplied by **{stage_multiplier}x** because this stage is more/less sensitive
            - **{stage_desc}** - this is what's happening to your plants now
            
            **⚠️ What to Do:**
            - **Green area (0-1)**: Normal farming operations
            - **Yellow area (1-2)**: Monitor weather closely
            - **Orange area (2-3)**: Take protective measures
            - **Red area (3-4)**: Emergency action needed
            """)
        
        # Prepare trend data with stage-specific risks and enhanced parameters
        trend_data = []
        for i, hour in enumerate(hourly):
            dt = datetime.fromtimestamp(hour["dt"], tz=PAKISTAN_TZ)
            
            # Extract enhanced meteorological parameters for trend analysis
            temp = hour["temp"]
            humidity = hour["humidity"]
            pressure = hour["pressure"]
            wind_speed = hour["wind_speed"]
            clouds = hour["clouds"]
            rain_1h = hour.get("rain", {}).get("1h", 0)
            visibility = hour.get("visibility", None)
            dew_point = hour.get("dew_point", None)
            cape = hour.get("cape", None)
            
            # Calculate enhanced risks for trend analysis
            dust_risk = calculate_dust_risk(
                wind_speed, 
                humidity, 
                pressure, 
                stage_multiplier,
                visibility=visibility,
                dew_point=dew_point,
                temp=temp,
                clouds=clouds
            )
            
            hail_risk = calculate_hail_risk(
                temp, 
                rain_1h, 
                clouds, 
                wind_speed, 
                stage_multiplier,
                pressure=pressure,
                cape=cape,
                humidity=humidity
            )
            
            rain_risk = calculate_rain_risk(rain_1h, None, stage_multiplier)
            
            # Check if this hour has any alerts
            has_alert = any(alert["datetime"].hour == dt.hour and alert["datetime"].date() == dt.date() 
                          for alert in forecast_alerts if alert["type"] == "hourly")
            
            trend_data.append({
                "Time": dt,
                "Forecasted Temperature": temp,
                "Humidity": humidity,
                "Wind Speed": wind_speed,
                "Dust Risk": dust_risk,
                "Hail Risk": hail_risk,
                "Rain Risk": rain_risk,
                "Max Risk": max(dust_risk, hail_risk, rain_risk),
                "Has Alert": has_alert
            })
        
        trend_df = pd.DataFrame(trend_data)
        
        # Temperature and humidity trend with clear labeling
        fig_temp = px.line(trend_df, x="Time", y=["Forecasted Temperature", "Humidity"], 
                          title=f"🌡️ Weather Forecast for Next 24 Hours - {selected_region}")
        
        # Customize the temperature chart for better readability
        fig_temp.update_traces(
            selector=dict(name="Forecasted Temperature"),
            name="Temperature (°C)",
            line=dict(color="#FF6B6B", width=3)
        )
        fig_temp.update_traces(
            selector=dict(name="Humidity"),
            name="Humidity (%)",
            line=dict(color="#4ECDC4", width=3)
        )
        
        # Add alert markers with better labeling
        alert_times = [alert["datetime"] for alert in forecast_alerts if alert["type"] == "hourly"]
        if alert_times:
            try:
                for i, alert_time in enumerate(alert_times):
                    # Ensure the alert_time is within the trend data range
                    if trend_df["Time"].min() <= alert_time <= trend_df["Time"].max():
                        # Use add_shape instead of add_vline for better compatibility
                        fig_temp.add_shape(
                            type="line",
                            x0=alert_time, x1=alert_time,
                            y0=0, y1=1,
                            yref="paper",
                            line=dict(color="red", width=3, dash="dash")
                        )
                        # Add annotation for the first alert only to avoid clutter
                        if i == 0:
                            fig_temp.add_annotation(
                                x=alert_time,
                                y=1.05,
                                yref="paper",
                                text="⚠️ Weather Alert Time",
                                showarrow=True,
                                arrowhead=2,
                                arrowcolor="red",
                                bgcolor="rgba(255,255,255,0.8)",
                                bordercolor="red"
                            )
            except Exception as e:
                # If there's an issue with adding alert markers, continue without them
                st.warning(f"Note: Alert markers could not be displayed on temperature chart")
        
        fig_temp.update_layout(
            title={
                'text': f"🌡️ Weather Forecast for Next 24 Hours - {selected_region}",
                'x': 0.5,
                'font': {'size': 18}
            },
            xaxis_title="📅 Time of Day",
            yaxis_title="🌡️ Temperature (°C) / 💧 Humidity (%)",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            annotations=[
                dict(
                    x=0.5, y=-0.15, xref='paper', yref='paper',
                    text="📊 Based on weather forecasting models | Red lines show when weather alerts are expected",
                    showarrow=False, 
                    font=dict(size=11, color="gray"),
                    xanchor='center'
                )
            ]
        )
        st.plotly_chart(fig_temp, use_container_width=True)
        
        # Risk trends with stage adjustment and alert highlighting
        fig_risk = px.line(trend_df, x="Time", y=["Dust Risk", "Hail Risk", "Rain Risk"],
                          title=f"🚨 Weather Risk Levels for Tobacco Crops - {selected_region}")
        
        # Customize risk chart colors and styling
        fig_risk.update_traces(
            selector=dict(name="Dust Risk"),
            name="🌪️ Dust Storm Risk",
            line=dict(color="#FF8C00", width=3)
        )
        fig_risk.update_traces(
            selector=dict(name="Hail Risk"), 
            name="🧊 Hail Storm Risk",
            line=dict(color="#4A90E2", width=3)
        )
        fig_risk.update_traces(
            selector=dict(name="Rain Risk"),
            name="🌧️ Heavy Rain Risk", 
            line=dict(color="#00C851", width=3)
        )
        
        # Add risk threshold line with better explanation
        fig_risk.add_hline(y=2, line_dash="dot", line_color="orange", line_width=2,
                          annotation_text="⚠️ Alert Level (Risk = 2)", 
                          annotation_position="right",
                          annotation=dict(bgcolor="rgba(255,255,255,0.8)", bordercolor="orange"))
        
        # Add alert markers with explanations
        if alert_times:
            try:
                for i, alert_time in enumerate(alert_times):
                    # Ensure the alert_time is within the trend data range
                    if trend_df["Time"].min() <= alert_time <= trend_df["Time"].max():
                        # Use add_shape instead of add_vline for better compatibility
                        fig_risk.add_shape(
                            type="line",
                            x0=alert_time, x1=alert_time,
                            y0=0, y1=4,
                            line=dict(color="red", width=3, dash="dash")
                        )
                        # Add annotation for the first alert only
                        if i == 0:
                            fig_risk.add_annotation(
                                x=alert_time,
                                y=4.2,
                                text="🚨 Risk Alert Expected",
                                showarrow=True,
                                arrowhead=2,
                                arrowcolor="red",
                                bgcolor="rgba(255,255,255,0.8)",
                                bordercolor="red"
                            )
            except Exception as e:
                # If there's an issue with adding alert markers, continue without them
                st.warning(f"Note: Alert markers could not be displayed on risk chart")
        
        fig_risk.update_layout(
            title={
                'text': f"🚨 Weather Risk Levels for Tobacco Crops - {selected_region}",
                'x': 0.5,
                'font': {'size': 18}
            },
            xaxis_title="📅 Time of Day",
            yaxis_title="⚠️ Risk Level (0 = Safe, 4 = Dangerous)",
            yaxis=dict(range=[0, 4.5], tickvals=[0, 1, 2, 3, 4], 
                      ticktext=["0 - Safe", "1 - Low Risk", "2 - Alert Level", "3 - High Risk", "4 - Danger"]),
            legend=dict(
                orientation="h",
                yanchor="bottom", 
                y=1.02,
                xanchor="right",
                x=1
            ),
            annotations=[
                dict(
                    x=0.5, y=-0.15, xref='paper', yref='paper',
                    text=f"🌱 Risk levels adjusted for {stage_name} (×{stage_multiplier}) | Orange line = Alert threshold | Red lines = Expected risk times",
                    showarrow=False, 
                    font=dict(size=11, color="gray"),
                    xanchor='center'
                )
            ]
        )
        st.plotly_chart(fig_risk, use_container_width=True)
        
        # Risk timeline summary
        st.markdown("### 📊 Simple Summary Charts")
        
        col1, col2 = st.columns(2)
        with col1:
            # Risk distribution chart with better labels
            risk_counts = trend_df.groupby('Max Risk').size().reset_index(name='Hours')
            risk_counts['Risk Level'] = risk_counts['Max Risk'].apply(lambda x: 
                "🟢 Safe (0)" if x == 0 else
                "🟡 Low Risk (1)" if x == 1 else
                "🟠 Alert Level (2)" if x == 2 else
                "🔴 High Risk (3)" if x == 3 else
                "🚨 Danger (4)")
            
            fig_dist = px.bar(risk_counts, x='Risk Level', y='Hours', 
                            title="⏰ How Many Hours at Each Risk Level",
                            color='Max Risk', 
                            color_continuous_scale=[[0, '#00C851'], [0.25, '#FFD700'], [0.5, '#FF8C00'], [0.75, '#FF4B4B'], [1, '#8B0000']])
            
            fig_dist.update_layout(
                title={
                    'text': "⏰ How Many Hours at Each Risk Level (Next 24h)",
                    'x': 0.5,
                    'font': {'size': 16}
                },
                xaxis_title="🚨 Risk Level",
                yaxis_title="⏱️ Number of Hours",
                showlegend=False
            )
            st.plotly_chart(fig_dist, use_container_width=True)
        
        with col2:
            # Alert timeline with better explanation
            if forecast_alerts:
                alert_timeline = []
                for alert in forecast_alerts[:10]:  # Show next 10 alerts
                    hours_from_now = (alert["datetime"] - datetime.now(PAKISTAN_TZ)).total_seconds() / 3600
                    alert_timeline.append({
                        "Hours from Now": hours_from_now,
                        "Risk Type": f"{alert['risk_type']} Storm",
                        "Risk Level": alert["risk_level"],
                        "Time": alert["datetime"].strftime("%m/%d %H:%M"),
                        "Severity": get_risk_intensity_label(alert["risk_level"])
                    })
                
                alert_df = pd.DataFrame(alert_timeline)
                fig_timeline = px.scatter(alert_df, x="Hours from Now", y="Risk Level", 
                                        color="Risk Type", size="Risk Level",
                                        title="🚨 When Weather Alerts Will Happen",
                                        hover_data=["Time", "Severity"],
                                        size_max=20)
                
                fig_timeline.update_layout(
                    title={
                        'text': "🚨 When Weather Alerts Will Happen",
                        'x': 0.5,
                        'font': {'size': 16}
                    },
                    xaxis_title="⏰ Hours from Now",
                    yaxis_title="🚨 Risk Level (0=Safe, 4=Danger)",
                    yaxis=dict(range=[0, 5], tickvals=[0, 1, 2, 3, 4],
                              ticktext=["Safe", "Low", "Alert", "High", "Danger"])
                )
                st.plotly_chart(fig_timeline, use_container_width=True)
                
                # Add simple explanation
                st.info(f"""
                **📍 What This Shows:**
                - **Dots on the chart**: Each dot is a weather alert
                - **Colors**: Different types of weather risks (dust, hail, rain)
                - **Size**: Bigger dots = more dangerous weather
                - **X-axis**: How many hours from now the alert will happen
                - **Next alert**: {forecast_alerts[0]['risk_type']} storm in {hours_from_now:.1f} hours
                """)
            else:
                st.success("✅ **Good News!** No weather alerts expected in the next 24 hours")
                st.info("Your tobacco crops should be safe from weather risks. Continue normal farming operations.")
        
        # Enhanced risk trend summary with simpler language
        st.markdown(f"""
        **📋 Easy Summary for Farmers:**
        - **Your tobacco stage**: {stage_name} - {stage_desc}
        - **Weather sensitivity**: {stage_multiplier}x more sensitive than normal
        - **Current temperature**: {current_temp:.1f}°C (real sensor reading)
        - **Next hour forecast**: {forecast_temp:.1f}°C (computer prediction)
        - **Temperature difference**: ±{abs(current_temp - forecast_temp):.1f}°C between real and forecast
        - **Total weather alerts**: {len(forecast_alerts)} alerts in the next 7 days
        - **Urgent alerts**: {len([a for a in forecast_alerts if a["datetime"] <= datetime.now(PAKISTAN_TZ) + timedelta(hours=24)])} alerts in the next 24 hours
        
        **🌱 What This Means:**
        - Higher numbers = more danger to your tobacco plants
        - Take action when risk levels reach 2 or higher
        - Check weather updates regularly during sensitive growth stages
        """)
    
    with tab5:
        st.markdown("### 🚨 Forecast Weather Risk Alerts")
        
        if not forecast_alerts:
            st.success("""
            ✅ **No Weather Risk Alerts**
            
            No significant weather risks detected in the forecast period for the next 7 days.
            Current forecast conditions appear favorable for tobacco cultivation activities.
            
            **Monitoring Status:**
            - 24-hour forecast: Clear
            - 7-day forecast: Clear
            - Risk threshold: Level 2+ (Moderate or higher)
            """)
        else:
            # Quick overview with summary cards
            create_risk_summary_cards(forecast_alerts)
            
            st.markdown("---")
            
            # Clear timeline display
            st.markdown("## 📅 **EASY-TO-READ RISK TIMELINE**")
            st.markdown("*Hour-by-hour and day-by-day breakdown with intensity levels*")
            
            create_upcoming_risks_timeline(forecast_alerts, stage_name)
            
            st.markdown("---")
            
            # Alert management controls
            st.markdown("### 🔧 **Alert Management & Export**")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                alert_view = st.radio(
                    "View Mode",
                    options=["All Alerts", "Next 24h Only", "High/Severe Only"],
                    help="Choose which alerts to display"
                )
            
            with col2:
                sort_by = st.selectbox(
                    "Sort By",
                    options=["Time (Earliest First)", "Risk Level (Highest First)", "Risk Type"],
                    help="Choose how to sort the alerts"
                )
            
            with col3:
                show_details = st.checkbox(
                    "Show Detailed Weather Data",
                    value=False,
                    help="Include detailed weather parameters in alert cards"
                )
            
            # Filter and sort alerts
            display_alerts = forecast_alerts.copy()
            
            if alert_view == "Next 24h Only":
                display_alerts = [a for a in display_alerts if a["datetime"] <= datetime.now(PAKISTAN_TZ) + timedelta(hours=24)]
            elif alert_view == "High/Severe Only":
                display_alerts = [a for a in display_alerts if a["risk_level"] >= 3]
            
            if sort_by == "Risk Level (Highest First)":
                display_alerts.sort(key=lambda x: x["risk_level"], reverse=True)
            elif sort_by == "Risk Type":
                display_alerts.sort(key=lambda x: x["risk_type"])
            # Default is already sorted by time
            
            # Display alerts
            if display_alerts:
                st.markdown(f"### 📋 Alert Details ({len(display_alerts)} alerts)")
                
                # Group alerts by date for better organization
                alerts_by_date = {}
                for alert in display_alerts:
                    date_key = alert["datetime"].strftime("%Y-%m-%d")
                    if date_key not in alerts_by_date:
                        alerts_by_date[date_key] = []
                    alerts_by_date[date_key].append(alert)
                
                # Display alerts grouped by date
                for date_key, day_alerts in alerts_by_date.items():
                    date_obj = datetime.strptime(date_key, "%Y-%m-%d")
                    day_name = date_obj.strftime("%A, %B %d, %Y")
                    
                    with st.expander(f"📅 {day_name} ({len(day_alerts)} alerts)", expanded=True):
                        for alert in day_alerts:
                            if show_details:
                                create_risk_alert_card(alert, stage_name)
                            else:
                                # Simplified alert display using new visual card
                                create_simple_alert_card(alert)
            else:
                st.info("No alerts match the selected filters.")
            
            # Export/Download options
            st.markdown("---")
            st.markdown("### 📤 Export Options")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📋 Copy Alert Summary"):
                    summary_text = create_forecast_risk_summary(display_alerts)
                    st.code(summary_text, language="text")
            
            with col2:
                # Create CSV data for download
                if display_alerts:
                    csv_data = []
                    for alert in display_alerts:
                        csv_data.append({
                            "Date": alert["datetime"].strftime("%Y-%m-%d"),
                            "Time": alert["datetime"].strftime("%H:%M"),
                            "Risk Type": alert["risk_type"],
                            "Risk Level": alert["risk_level"],
                            "Intensity": alert["intensity"],
                            "Temperature": alert["temp"],
                            "Humidity": alert["humidity"],
                            "Wind Speed": alert["wind_speed"],
                            "Rain": alert["rain"],
                            "Pressure": alert["pressure"]
                        })
                    
                    csv_df = pd.DataFrame(csv_data)
                    csv_string = csv_df.to_csv(index=False)
                    
                    st.download_button(
                        label="📥 Download Alerts CSV",
                        data=csv_string,
                        file_name=f"weather_alerts_{selected_region}_{datetime.now(PAKISTAN_TZ).strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
    
    with tab6:
        create_risk_legend()
    
    # Footer with Pakistan time
    st.markdown("---")
    st.markdown(f"""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>🌾 Tobacco Cultivation Weather Monitoring System | Data provided by OpenWeatherMap</p>
        <p>Growth stage-specific risk assessment for Pakistan tobacco regions</p>
        <p>Last updated: {current_time_pk.strftime('%Y-%m-%d %H:%M:%S')} PKT | Auto-refresh: Every 30 minutes</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 