# 🌾 Pakistan Tobacco Weather Risk Assessment Dashboard

A comprehensive real-time weather monitoring and risk assessment dashboard specifically designed for tobacco cultivation in Pakistan. This Streamlit application provides critical weather insights and automated risk assessments for dust storms, hailstorms, heavy rain, and drought conditions that can impact tobacco crops.

## 🚀 Live Demo

**Deployed on Render:** [View Dashboard](https://your-render-app-url.onrender.com)

## 📊 Features

### Real-time Weather Monitoring
- Current weather conditions for 9 major tobacco cultivation regions in Pakistan
- 24-hour detailed forecast with hourly breakdowns
- 7-day weather outlook for agricultural planning
- Live data from OpenWeatherMap API with 30-minute caching

### ⚠️ Advanced Risk Assessment System
- **🌪️ Dust Storm Risk**: Based on wind speed, humidity, atmospheric pressure, and visibility
- **🧊 Hail Storm Risk**: Calculated using temperature, precipitation, cloud cover, and wind patterns
- **🌧️ Heavy Rain Risk**: Assessed from precipitation intensity and duration
- **🌡️ Drought Risk**: NEW! Ultra-conservative drought detection for extreme conditions
- 0-4 scale risk scoring with color-coded visual indicators

### 🌱 Tobacco-Specific Intelligence
- Growth stage tracking with Pakistani agricultural calendar
- Stage-specific risk multipliers for accurate assessments
- Regional climate and elevation information
- Actionable agricultural recommendations

### 📱 Enhanced User Interface
- Clean, modern Streamlit dashboard with professional styling
- **District Alert Sidebar**: Real-time overview of all regions
- Interactive risk gauges and trend charts
- Forecast timeline with risk predictions
- Mobile-responsive design for field use

## 🗺️ Supported Regions

| Region | Coordinates | Elevation | Climate | Tobacco Type |
|--------|-------------|-----------|---------|--------------|
| Mardan | 34.201°N, 72.050°E | 283m | Semi-arid continental | Virginia |
| Multan | 30.157°N, 71.524°E | 122m | Hot desert | Burley |
| Swabi | 34.120°N, 72.470°E | 300m | Semi-arid continental | Virginia |
| Charsadda | 34.150°N, 71.740°E | 276m | Semi-arid continental | Virginia |
| Peshawar | 34.016°N, 71.578°E | 359m | Semi-arid continental | Virginia |
| Nowshera | 34.016°N, 71.983°E | 293m | Semi-arid continental | Virginia |
| Dir | 35.205°N, 71.878°E | 1,419m | Humid subtropical | Mountain Virginia |
| Bannu | 32.985°N, 70.604°E | 371m | Hot semi-arid | Burley |
| Lakki Marwat | 32.607°N, 70.911°E | 258m | Hot semi-arid | Local varieties |

## 🛠️ Installation & Deployment

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/tobacco-weather-dashboard.git
   cd tobacco-weather-dashboard
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the dashboard**
   ```bash
   streamlit run enhanced_dashboard_with_alerts.py
   ```

4. **Access locally**
   - Open `http://localhost:8501` in your browser

### Render Deployment

1. **Fork this repository** to your GitHub account

2. **Connect to Render:**
   - Go to [render.com](https://render.com)
   - Create new "Web Service"
   - Connect your GitHub repository
   - Use these settings:
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
     - **Environment:** `Python 3`

3. **Deploy:** Render will automatically deploy and provide a live URL

## 📋 Dashboard Components

### 1. Header Section
- Professional branding and title
- Region selection dropdown
- Real-time data status and auto-refresh indicator

### 2. Current Regional Overview (KPI Cards)
- 🌡️ **Temperature**: Current with optimal range comparison
- 💧 **Humidity**: Relative humidity with agricultural targets
- 🌬️ **Wind Speed**: Current conditions with dust risk assessment
- ☔ **7-Day Precipitation**: Total rainfall forecast
- 🌾 **Growth Stage**: Current tobacco development phase
- 📍 **Location Info**: Elevation and climate classification

### 3. District Alert Sidebar (NEW)
- Real-time risk overview for all 9 regions
- Color-coded alert indicators
- Quick access to high-risk areas
- Summary statistics and urgent warnings

### 4. Navigation Tabs

#### 📊 Overview Tab
- Comprehensive current weather display
- Real-time atmospheric data
- Weather descriptions and visibility

#### 🌤️ Weather Details Tab
- 24-hour hourly forecast table
- 7-day daily forecast summary
- Detailed meteorological parameters

#### ⚠️ Risk Assessment Tab
- Four interactive risk gauges (Dust, Hail, Rain, Drought)
- Tobacco-specific risk messaging
- Color-coded risk level legend
- Stage-specific agricultural recommendations

#### 📈 Trends Tab
- Temperature and humidity trend charts
- Risk level progression over 24 hours
- Interactive Plotly visualizations
- Historical pattern analysis

## 🎨 Risk Assessment Logic

### Dust Storm Risk (0-4 Scale)
- **Severe (4)**: Wind >15 m/s + Humidity <30% + Low pressure
- **High (3)**: Wind >12 m/s + Humidity <40%
- **Moderate (2)**: Wind >8 m/s + Humidity <50%
- **Light (1)**: Wind >5 m/s + Humidity <60%

### Drought Risk (Ultra-Conservative)
- **Severe (4)**: ≥52°C + ≤2% humidity (Record-breaking conditions)
- **High (3)**: ≥50°C + ≤3% humidity (Extreme heat wave)
- **Moderate (2)**: ≥48°C + ≤5% humidity (Very extreme heat)
- **Light (1)**: ≥45°C + ≤10% humidity (Extreme heat + low humidity)

### Growth Stage Multipliers
- **Nursery**: 1.5x (Most vulnerable)
- **Transplanting**: 1.8x (Critical period)
- **Flowering**: 1.3x (Moderate sensitivity)
- **Harvest**: 1.0x (Baseline risk)

## 🌿 Tobacco Agricultural Intelligence

### Seasonal Calendar (Pakistan)
- **December-February**: Nursery Stage
- **March-April**: Transplanting
- **April-May**: Vegetative Growth
- **June-September**: Flowering
- **August-October**: Harvesting
- **November**: Post-harvest/Field Preparation

### Risk Recommendations by Stage
- **Nursery**: Focus on temperature and humidity control
- **Transplanting**: Critical wind and rain protection
- **Flowering**: Comprehensive weather monitoring
- **Harvest**: Rain and humidity alerts for curing

## 📊 Technical Specifications

### Data Sources
- **Primary**: OpenWeatherMap API (3.0)
- **Refresh Rate**: 30 minutes automatic cache
- **Coverage**: Real-time + 7-day forecasts
- **Accuracy**: Regional weather station data

### Performance Features
- **Caching**: 30-minute API response caching
- **Auto-refresh**: Background data updates
- **Error Handling**: Graceful degradation for API failures
- **Mobile Optimization**: Responsive design for field use

## 🚨 Troubleshooting

### Common Issues

1. **Dashboard not loading**
   - Check internet connection
   - Verify all dependencies installed
   - Restart with: `streamlit run enhanced_dashboard_with_alerts.py`

2. **Missing weather data**
   - API key is embedded and should work automatically
   - Check if OpenWeatherMap service is available
   - Try manual refresh in the sidebar

3. **Charts not displaying**
   - Ensure plotly>=5.15.0 is installed
   - Clear browser cache and refresh
   - Check JavaScript is enabled

## 📄 Files Description

- `enhanced_dashboard_with_alerts.py`: Main dashboard application
- `app.py`: Render deployment entry point
- `requirements.txt`: Python dependencies
- `README.md`: This documentation

## 🌍 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly with real weather data
5. Submit a pull request

## 📞 Support

For agricultural questions or technical support:
- **Technical Issues**: Create a GitHub issue
- **Agricultural Guidance**: Consult local extension services
- **Emergency Weather**: Contact Pakistan Meteorological Department

## 📄 License

This project is designed for agricultural monitoring and educational purposes. Built for tobacco farmers and agricultural advisors in Pakistan.

---

**🌾 Empowering Pakistani tobacco farmers with intelligent weather insights** 