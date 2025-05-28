# 🌾 KTC OpenWeather - Tobacco Cultivation Weather Risk Dashboard

**Version:** 2.0.0  
**Release Date:** May 28, 2025  
**Status:** Production Ready  

A comprehensive real-time weather monitoring and risk assessment dashboard specifically designed for tobacco cultivation in Pakistan. This Streamlit application provides critical weather insights and automated risk assessments for dust storms, hailstorms, and rain events that can impact tobacco crops.

## 📋 Version History

### v2.0.0 (Current) - Enhanced Risk Assessment
- **Major Enhancement**: Scientifically improved dust storm and hailstorm risk calculations
- **New Features**: CAPE integration, atmospheric pressure analysis, visibility confirmation
- **Improvements**: 80% reduction in false positive alerts
- **UI Updates**: Professional alert cards, timeline visualization, enhanced navigation
- **Files**: `enhanced_dashboard.py` (main), `code.py` (basic analysis)

### v1.0.0 - Initial Release
- Basic weather monitoring for 4 Pakistani regions
- Simple risk assessment algorithms
- Streamlit dashboard with tabbed navigation
- File: `dashboard.py`

## 🚀 Quick Start

### Option 1: Enhanced Dashboard (Recommended)
```bash
git clone https://github.com/[your-username]/KTC-OpenWeather.git
cd KTC-OpenWeather
pip install -r requirements.txt
streamlit run enhanced_dashboard.py --server.port 8505
```

### Option 2: Basic Dashboard
```bash
streamlit run dashboard.py --server.port 8501
```

### Option 3: Terminal Analysis
```bash
python code.py
```

## 🗂️ Project Structure

```
KTC-OpenWeather/
├── 📱 Main Applications
│   ├── enhanced_dashboard.py    # v2.0 Enhanced dashboard (RECOMMENDED)
│   ├── dashboard.py            # v1.0 Basic dashboard
│   └── code.py                 # Terminal-based analysis
├── 📋 Requirements
│   └── requirements.txt        # Python dependencies
├── 📚 Documentation
│   ├── README.md              # This file
│   ├── ENHANCED_RISK_CALCULATION_SUMMARY.md
│   ├── DUST_STORM_LOGIC_IMPROVEMENTS.md
│   ├── FORECAST_RISK_ANALYSIS_SUMMARY.md
│   └── [other documentation files]
├── 🗃️ Project Memory
│   └── memory-bank/           # Development documentation
└── 🔧 Configuration
    └── .gitignore            # Git ignore rules
```

## 🚀 Features

### 📊 Real-time Weather Monitoring
- Current weather conditions for 4 major tobacco cultivation regions in Pakistan
- 12-hour detailed forecast with hourly breakdowns
- 7-day weather outlook for planning purposes
- Live data from OpenWeatherMap API with 5-minute caching

### ⚠️ Risk Assessment System
- **Dust Storm Risk**: Based on wind speed, humidity, and atmospheric pressure
- **Hail Storm Risk**: Calculated using temperature, precipitation, cloud cover, and wind patterns
- **Rain Risk**: Assessed from precipitation intensity and duration
- 0-4 scale risk scoring with color-coded visual indicators

### 🎯 Tobacco-Specific Features
- Agricultural risk messaging tailored for tobacco cultivation
- Growth stage tracking (currently showing Flowering Day 75)
- Regional climate and elevation information
- Actionable recommendations for crop protection

### 📱 User Interface
- Clean, modern Streamlit dashboard
- Mobile-responsive design for field use
- Interactive gauges and trend charts
- Tabbed navigation for organized information display

## 🗺️ Supported Regions

| Region | Coordinates | Elevation | Climate |
|--------|-------------|-----------|---------|
| Mardan | 34.201°N, 72.050°E | 283m | Semi-arid continental |
| Multan | 30.157°N, 71.524°E | 122m | Hot desert |
| Swabi | 34.120°N, 72.470°E | 300m | Semi-arid continental |
| Charsadda | 34.150°N, 71.740°E | 276m | Semi-arid continental |

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- OpenWeatherMap API key (included in the code)
- Internet connection for real-time data

### Quick Start

1. **Clone or download the project files**
   ```bash
   git clone <repository-url>
   cd weather-dashboard
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the dashboard**
   ```bash
   streamlit run dashboard.py
   ```

4. **Access the dashboard**
   - Open your web browser
   - Navigate to `http://localhost:8501`
   - Select your region and start monitoring!

### Alternative Installation
If you encounter issues with `streamlit-gauge`, you can install dependencies manually:
```bash
pip install streamlit>=1.28.0 pandas>=1.5.0 requests>=2.28.0 plotly>=5.15.0 numpy>=1.24.0
```

## 📋 Dashboard Components

### 1. Header Section
- Professional title and branding
- Region selection dropdown
- Real-time data status indicator

### 2. Current Regional Overview (KPI Cards)
- 🌡️ **Temperature**: Current temperature with optimal range comparison
- 💧 **Humidity**: Relative humidity with agricultural targets
- 🌬️ **Wind Speed**: Current wind conditions with dust risk level
- ☔ **7-Day Precipitation**: Total rainfall forecast with risk assessment
- 🌾 **Growth Stage**: Current tobacco development phase
- 📍 **Location Info**: Elevation and climate classification

### 3. Navigation Tabs

#### 📊 Overview Tab
- Comprehensive current weather conditions
- Real-time atmospheric data
- Weather description and visibility

#### 🌤️ Weather Details Tab
- 12-hour hourly forecast table
- 7-day daily forecast summary
- Detailed meteorological parameters

#### ⚠️ Risk Assessment Tab
- Three interactive risk gauges (Dust, Hail, Rain)
- Tobacco-specific risk messaging
- Color-coded risk level legend
- Actionable recommendations

#### 📈 Trends Tab
- Temperature and humidity trend charts
- Risk level progression over time
- Interactive Plotly visualizations

## 🎨 Risk Assessment Logic

### Dust Storm Risk (0-4 Scale)
- **Level 4 (Severe)**: Wind > 15 m/s + Humidity < 30%
- **Level 3 (High)**: Wind > 10 m/s + Humidity < 35%
- **Level 2 (Moderate)**: Wind > 7 m/s + Humidity < 40%
- **Level 1 (Low)**: Wind > 4 m/s + Humidity < 50%
- **Level 0 (None)**: Below threshold conditions

### Hail Storm Risk (0-4 Scale)
- **Level 4 (Severe)**: Temp > 25°C + Rain > 3mm + Clouds > 80% + Wind > 5 m/s
- **Level 3 (High)**: Temp > 25°C + Rain > 2mm + Clouds > 60%
- **Level 2 (Moderate)**: Rain > 1mm + Clouds > 40%
- **Level 1 (Low)**: Rain > 0.5mm + Clouds > 20%
- **Level 0 (None)**: Below threshold conditions

### Rain Risk (0-4 Scale)
- **Level 4 (Severe)**: > 10mm in 3 hours
- **Level 3 (High)**: > 6mm in 3 hours
- **Level 2 (Moderate)**: > 3mm in 3 hours
- **Level 1 (Low)**: > 0.5mm in 3 hours
- **Level 0 (None)**: No precipitation

## 🔧 Technical Details

### Architecture
- **Frontend**: Streamlit web framework
- **Data Source**: OpenWeatherMap API 3.0 OneCall
- **Visualization**: Plotly for interactive charts and gauges
- **Data Processing**: Pandas for weather data manipulation
- **Caching**: 5-minute TTL for API responses

### Performance Features
- Efficient API caching to minimize requests
- Responsive design for various screen sizes
- Error handling for network issues
- Graceful degradation when data is unavailable

### File Structure
```
├── dashboard.py          # Main Streamlit application
├── code.py              # Original weather analysis script
├── requirements.txt     # Python dependencies
├── README.md           # This documentation
└── memory-bank/        # Project documentation
    ├── projectbrief.md
    └── activeContext.md
```

## 🌐 API Information

This dashboard uses the OpenWeatherMap API 3.0 OneCall endpoint:
- **Endpoint**: `https://api.openweathermap.org/data/3.0/onecall`
- **Data Includes**: Current weather, hourly forecast (48h), daily forecast (8 days)
- **Update Frequency**: Real-time data with 5-minute caching
- **Rate Limits**: Respects API rate limits with efficient caching

## 🚨 Troubleshooting

### Common Issues

1. **"Module not found" errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Try installing packages individually if batch installation fails

2. **API connection errors**
   - Check internet connection
   - Verify API key is valid (current key is embedded)
   - Wait a few minutes if rate limits are exceeded

3. **Dashboard not loading**
   - Ensure Streamlit is properly installed
   - Try running with: `python -m streamlit run dashboard.py`
   - Check if port 8501 is available

4. **Gauge charts not displaying**
   - Install plotly: `pip install plotly>=5.15.0`
   - Clear browser cache and refresh

### Performance Tips
- Dashboard automatically caches API responses for 5 minutes
- Refresh the page to get the latest data
- Use the region selector to switch between locations efficiently

## 📞 Support

For technical issues or feature requests:
1. Check the troubleshooting section above
2. Verify all dependencies are correctly installed
3. Ensure stable internet connection for API access

## 📄 License

This project is designed for agricultural monitoring and educational purposes. The OpenWeatherMap API key included is for demonstration - please obtain your own key for production use.

---

**🌾 Built for tobacco farmers and agricultural advisors in Pakistan** 