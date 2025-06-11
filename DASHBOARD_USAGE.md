# Weather Risk Assessment Dashboards

This project contains two versions of the Weather Risk Assessment Dashboard for Tobacco Cultivation in Pakistan.

## Files

### 1. `enhanced_dashboard.py` (Original)
- Complete weather monitoring dashboard for tobacco cultivation
- Single-region focused view with detailed analysis
- Original UI layout with all features

### 2. `enhanced_dashboard_with_alerts.py` (NEW - Enhanced Version)
- **All original functionality preserved exactly as-is**
- **NEW FEATURE**: District Alert Overview sidebar
- Color-coded alert indicators for all 4 districts (Mardan, Multan, Swabi, Charsadda)
- Quick visual status overview for all regions at a glance
- Summary statistics showing total alerts across all districts

## Key Differences

| Feature | Original Version | Enhanced Version |
|---------|-----------------|------------------|
| Main UI | ✅ Complete | ✅ Identical (unchanged) |
| Single District Analysis | ✅ Full details | ✅ Full details |
| Sidebar | Collapsed by default | **NEW: District alerts overview** |
| Multi-District View | ❌ None | ✅ **Color-coded alert cards** |
| Quick Status Check | ❌ Must check each region individually | ✅ **See all at once** |

## Enhanced Version Features

### District Alert Overview Sidebar
- **Real-time status** for all 4 tobacco regions
- **Color-coded indicators**:
  - 🚨 **RED**: Critical risk (3-4) - Immediate action needed
  - ⚠️ **ORANGE**: High risk (2) - Take protective measures
  - 🟡 **YELLOW**: Moderate risk (1) - Monitor closely  
  - ✅ **GREEN**: Safe (0) - Normal operations

### Alert Information Display
- Current risk level (0-4 scale)
- Number of forecast alerts
- Urgent alerts (next 24 hours)
- Current temperature, wind speed, humidity
- Overall summary with total statistics

### Quick Benefits
- **Instant overview**: See all district statuses without switching regions
- **Priority alerts**: Urgent warnings highlighted with 🔥 indicator
- **Real-time data**: Auto-refreshes every 30 minutes
- **Visual clarity**: Color coding makes risk levels immediately apparent

## How to Run

```bash
# Original version
streamlit run enhanced_dashboard.py

# Enhanced version with district alerts
streamlit run enhanced_dashboard_with_alerts.py
```

## When to Use Which Version

### Use Original Version When:
- Focused analysis of a single region
- Detailed meteorological analysis needed
- Prefer simpler, uncluttered interface

### Use Enhanced Version When:
- Managing multiple tobacco cultivation sites
- Need quick overview of all regional risks
- Want immediate visual alert status
- Coordinating district-wide operations

Both versions use the same weather data, risk calculations, and forecasting algorithms. The enhanced version simply adds the multi-district overview capability while preserving all original functionality. 