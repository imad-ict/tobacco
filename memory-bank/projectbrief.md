# Project Brief: Weather Risk Assessment Dashboard for Tobacco Cultivation

## Project Overview
A real-time weather monitoring and risk assessment dashboard specifically designed for tobacco cultivation in Pakistan. The dashboard provides critical weather insights and risk assessments for dust storms, hailstorms, and rain events that can impact tobacco crops.

## Core Requirements

### Target Regions
- Mardan (34.201°N, 72.050°E)
- Multan (30.157°N, 71.524°E) 
- Swabi (34.120°N, 72.470°E)
- Charsadda (34.150°N, 71.740°E)

### Key Features
1. **Real-time Weather Monitoring**: Current conditions and forecasts using OpenWeatherMap API
2. **Risk Assessment**: Automated scoring for dust, hail, and rain risks (0-4 scale)
3. **Regional Selection**: Dropdown to switch between tobacco cultivation regions
4. **Visual Dashboard**: Streamlit-based interface with gauges, charts, and data tables
5. **Agricultural Context**: Tobacco-specific risk messaging and growth stage tracking

### Risk Categories
- **Dust Storm Risk**: Based on wind speed, humidity, and pressure
- **Hail Storm Risk**: Based on temperature, precipitation, cloud cover, and wind
- **Rain Risk**: Based on precipitation intensity over time periods

### Success Criteria
- Real-time data updates from OpenWeatherMap API
- Accurate risk classification using agricultural thresholds
- Intuitive visual interface for farmers and agricultural advisors
- Mobile-responsive design for field use
- Clear risk messaging with actionable insights

## Technical Foundation
- **Backend**: Python with existing weather data fetching logic
- **Frontend**: Streamlit dashboard framework
- **Data Source**: OpenWeatherMap API (3.0 OneCall)
- **Visualization**: Plotly for gauges and charts
- **Data Processing**: Pandas for weather data manipulation 