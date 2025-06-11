#!/usr/bin/env python3
"""
Test script to identify which dust risk algorithm is generating the user's data
Tests all three different algorithms found in the codebase with the exact data provided
"""

import pandas as pd
from datetime import datetime

# User's actual data
test_data = [
    {"time": "21:00", "temp": 31.9, "wind": 8.1, "humidity": 37, "rain": 0.0, "clouds": 0, "pressure": 998, "actual_result": "Dust (High)"},
    {"time": "22:00", "temp": 31.8, "wind": 8.8, "humidity": 39, "rain": 0.0, "clouds": 0, "pressure": 998, "actual_result": "Dust (High)"},
    {"time": "23:00", "temp": 31.7, "wind": 9.8, "humidity": 37, "rain": 0.0, "clouds": 0, "pressure": 998, "actual_result": "Dust (High)"},
    {"time": "00:00", "temp": 30.8, "wind": 9.6, "humidity": 39, "rain": 0.0, "clouds": 0, "pressure": 998, "actual_result": "Dust (High)"},
    {"time": "01:00", "temp": 30.4, "wind": 9.6, "humidity": 38, "rain": 0.0, "clouds": 0, "pressure": 997, "actual_result": "Dust (High)"},
    {"time": "02:00", "temp": 29.9, "wind": 9.4, "humidity": 39, "rain": 0.0, "clouds": 0, "pressure": 997, "actual_result": "Dust (High)"},
    {"time": "03:00", "temp": 29.5, "wind": 7.5, "humidity": 41, "rain": 0.0, "clouds": 0, "pressure": 997, "actual_result": "Dust (High)"}
]

# ============================================================================
# Algorithm 1: Enhanced Dashboard Version (enhanced_dashboard.py)
# ============================================================================
def calculate_dust_risk_enhanced(wind_speed, humidity, pressure, stage_multiplier=1.0, visibility=None, dew_point=None, temp=None, clouds=None):
    """Enhanced dashboard algorithm"""
    base_risk = 0
    
    # Primary condition check: Only proceed if basic dust storm conditions are met
    if wind_speed < 8 or humidity > 40 or pressure > 998:
        return 0  # No dust risk if basic conditions not met
    
    # Core dust storm risk assessment with realistic thresholds
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
            base_risk = min(4, base_risk + 1)
        
        # Dew point spread (if available) - indicates very dry air
        if temp is not None and dew_point is not None:
            temp_dew_spread = temp - dew_point
            if temp_dew_spread > 15:
                base_risk = min(4, base_risk + 1)
    
    # Conservative false positive exclusion
    if humidity > 50:
        base_risk = 0
    
    if wind_speed < 6:
        base_risk = 0
    
    if clouds is not None and clouds > 70 and wind_speed < 10:
        base_risk = 0
    
    # Apply stage multiplier conservatively and round to integer
    adjusted_risk = base_risk * stage_multiplier
    final_risk = min(4, round(adjusted_risk))
    
    return int(final_risk)

def get_risk_intensity_label_enhanced(risk_level):
    """Enhanced dashboard risk label"""
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

# ============================================================================
# Algorithm 2: Demo Version (demo.py)
# ============================================================================
def calculate_dust_risk_demo(wind_speed, humidity, pressure):
    """Demo version algorithm"""
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

def get_risk_intensity_label_demo(risk_level):
    """Demo version risk label"""
    risk_levels = ["No Risk", "Low Risk", "Moderate Risk", "High Risk", "Severe Risk"]
    return risk_levels[risk_level]

# ============================================================================
# Algorithm 3: Original Code Version (code.py)
# ============================================================================
def classify_weather_original(wind, humidity, temp, rain, clouds, pressure):
    """Original code.py algorithm"""
    
    # Step 1: Determine intensity based on wind speed only
    if wind > 15:
        intensity = "Severe"
    elif wind > 10:
        intensity = "Moderate"
    elif wind > 6:
        intensity = "Mild"
    else:
        intensity = "No or Low Risk"

    # Step 2: Check dust storm conditions
    if wind > 8 and humidity < 30 and pressure < 1005 and rain < 0.2:
        return f"Dust Storm Risk ({intensity})"
    
    return "Clear or Normal"

# ============================================================================
# Growth Stage Calculations
# ============================================================================
def get_current_growth_stage():
    """Get current growth stage (December = Nursery Stage)"""
    current_month = datetime.now().month
    if current_month >= 12 or current_month <= 2:
        return "Nursery Stage", 0.8
    # ... other stages would go here
    return "Unknown", 1.0

def calculate_stage_multiplier():
    """Calculate stage multiplier"""
    stage_multipliers = {
        "Nursery Stage": 0.8,
        "Transplanting": 1.5,
        "Vegetative Growth": 1.2,
        "Flowering": 1.4,
        "Topping Stage": 1.3,
        "Leaf Maturation": 1.6,
        "Harvest Period": 1.8,
        "Post-Harvest": 0.6
    }
    stage_name, _ = get_current_growth_stage()
    return stage_multipliers.get(stage_name, 1.0)

# ============================================================================
# Test Function
# ============================================================================
def run_tests():
    print("🔍 DUST RISK ALGORITHM COMPARISON TEST")
    print("=" * 80)
    print("Testing user's data against all three algorithms found in codebase")
    print()
    
    # Get current stage info
    stage_name, _ = get_current_growth_stage()
    stage_multiplier = calculate_stage_multiplier()
    
    print(f"📅 Current Growth Stage: {stage_name}")
    print(f"🔢 Stage Multiplier: {stage_multiplier}x")
    print()
    
    # Headers
    print(f"{'Time':<6} {'Wind':<5} {'Hum':<4} {'Press':<5} | {'Enhanced':<12} {'Demo':<12} {'Original':<20} | {'User Result':<15}")
    print("-" * 88)
    
    # Test each data point
    for data in test_data:
        time = data["time"]
        wind = data["wind"]
        humidity = data["humidity"]
        pressure = data["pressure"]
        temp = data["temp"]
        rain = data["rain"]
        clouds = data["clouds"]
        actual = data["actual_result"]
        
        # Test Algorithm 1: Enhanced Dashboard
        risk1 = calculate_dust_risk_enhanced(
            wind, humidity, pressure, stage_multiplier, 
            visibility=None, dew_point=None, temp=temp, clouds=clouds
        )
        label1 = get_risk_intensity_label_enhanced(risk1)
        enhanced_result = f"{risk1} ({label1})"
        
        # Test Algorithm 2: Demo
        risk2 = calculate_dust_risk_demo(wind, humidity, pressure)
        label2 = get_risk_intensity_label_demo(risk2)
        demo_result = f"{risk2} ({label2.split()[0]})"  # Shorten label
        
        # Test Algorithm 3: Original
        original_result = classify_weather_original(wind, humidity, temp, rain, clouds, pressure)
        if "Dust Storm Risk" in original_result:
            original_short = original_result.replace("Dust Storm Risk", "Dust")
        else:
            original_short = "Clear/Normal"
        
        # Print results
        print(f"{time:<6} {wind:<5.1f} {humidity:<4} {pressure:<5} | {enhanced_result:<12} {demo_result:<12} {original_short:<20} | {actual:<15}")
    
    print("-" * 88)
    print()
    
    # Analysis
    print("🔍 ANALYSIS:")
    print()
    
    print("❌ Enhanced Dashboard Algorithm:")
    print("   - Most entries should return 0 or 1 due to strict conditions")
    print("   - 03:00 should definitely return 0 (fails basic conditions)")
    print("   - With 0.8x stage multiplier, even risk 1 becomes 0.8 → 1")
    print()
    
    print("❌ Demo Algorithm:")
    print("   - Most entries would return 1-2 (Low-Moderate Risk)")
    print("   - 03:00 would return 1 (wind > 4, humidity < 50)")
    print("   - Results don't match 'High' designation")
    print()
    
    print("❌ Original Code Algorithm:")
    print("   - Requires humidity < 30 for dust risk")
    print("   - All entries have humidity 37-41%, so should return 'Clear or Normal'")
    print("   - Doesn't match 'Dust (High)' results")
    print()
    
    print("🚨 CONCLUSION:")
    print("   None of the three algorithms in the codebase produce results")
    print("   that match your data showing 'Dust (High)' for all entries.")
    print()
    print("🔍 POSSIBLE EXPLANATIONS:")
    print("   1. Different algorithm version not in current codebase")
    print("   2. Manual interpretation/modification of results") 
    print("   3. Different parameter values being used")
    print("   4. Bug in the running system")
    print("   5. Data from a different source/timestamp")
    print()
    
    # Detailed analysis for problematic entry
    print("🚨 CRITICAL ISSUE - Entry 03:00:")
    problem_data = test_data[6]  # 03:00 entry
    print(f"   Wind: {problem_data['wind']} m/s, Humidity: {problem_data['humidity']}%, Pressure: {problem_data['pressure']} hPa")
    print("   - Enhanced: Should return 0 (fails wind < 8 OR humidity > 40)")
    print("   - Demo: Should return 1 (Low Risk)")
    print("   - Original: Should return 'Clear or Normal' (humidity not < 30)")
    print(f"   - Your Result: {problem_data['actual_result']}")
    print("   This entry proves the data is NOT from current codebase algorithms!")

# ============================================================================
# Additional Test: Try Different Stage Multipliers
# ============================================================================
def test_different_multipliers():
    print("\n" + "=" * 80)
    print("🔬 TESTING DIFFERENT STAGE MULTIPLIERS")
    print("Testing if different stage could explain 'High' results")
    print()
    
    # Test with harvest period multiplier (highest)
    harvest_multiplier = 1.8
    
    print(f"{'Time':<6} {'Wind':<5} {'Hum':<4} | {'Base Risk':<10} {'×1.8 Harvest':<12} {'Result':<10}")
    print("-" * 60)
    
    for data in test_data:
        wind = data["wind"]
        humidity = data["humidity"]
        pressure = data["pressure"]
        temp = data["temp"]
        clouds = data["clouds"]
        
        # Calculate base risk (enhanced algorithm)
        base_risk = calculate_dust_risk_enhanced(
            wind, humidity, pressure, 1.0,  # No multiplier
            visibility=None, dew_point=None, temp=temp, clouds=clouds
        )
        
        # Apply harvest multiplier
        harvest_risk = min(4, round(base_risk * harvest_multiplier))
        harvest_label = get_risk_intensity_label_enhanced(harvest_risk)
        
        print(f"{data['time']:<6} {wind:<5.1f} {humidity:<4} | {base_risk:<10} {harvest_risk:<12} {harvest_label:<10}")
    
    print()
    print("💡 Even with highest multiplier (1.8x Harvest Period):")
    print("   - Most entries: base risk 1 × 1.8 = 1.8 → 2 (Moderate)")
    print("   - Still doesn't explain 'High' (level 3) results")
    print("   - 03:00 entry: base risk 0 × 1.8 = 0 (should be No Risk)")

if __name__ == "__main__":
    run_tests()
    test_different_multipliers()
    
    print("\n" + "=" * 80)
    print("🎯 RECOMMENDATION:")
    print("Check which Python file is actually running to generate your data.")
    print("The current codebase algorithms don't match your results.")
    print("There may be a different version or modified algorithm being used.") 