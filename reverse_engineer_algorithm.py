#!/usr/bin/env python3
"""
Reverse engineering script to figure out what algorithm could produce 
"Dust (High)" for all the user's data points
"""

# User's data - all showing "Dust (High)"
test_data = [
    {"time": "21:00", "temp": 31.9, "wind": 8.1, "humidity": 37, "rain": 0.0, "clouds": 0, "pressure": 998},
    {"time": "22:00", "temp": 31.8, "wind": 8.8, "humidity": 39, "rain": 0.0, "clouds": 0, "pressure": 998},
    {"time": "23:00", "temp": 31.7, "wind": 9.8, "humidity": 37, "rain": 0.0, "clouds": 0, "pressure": 998},
    {"time": "00:00", "temp": 30.8, "wind": 9.6, "humidity": 39, "rain": 0.0, "clouds": 0, "pressure": 998},
    {"time": "01:00", "temp": 30.4, "wind": 9.6, "humidity": 38, "rain": 0.0, "clouds": 0, "pressure": 997},
    {"time": "02:00", "temp": 29.9, "wind": 9.4, "humidity": 39, "rain": 0.0, "clouds": 0, "pressure": 997},
    {"time": "03:00", "temp": 29.5, "wind": 7.5, "humidity": 41, "rain": 0.0, "clouds": 0, "pressure": 997}  # Problematic
]

print("🔍 REVERSE ENGINEERING DUST RISK ALGORITHM")
print("=" * 60)
print("Trying to figure out what conditions could produce 'Dust (High)' for ALL entries")
print()

# Analyze the data ranges
winds = [d["wind"] for d in test_data]
humidities = [d["humidity"] for d in test_data]
pressures = [d["pressure"] for d in test_data]
temps = [d["temp"] for d in test_data]

print("📊 DATA ANALYSIS:")
print(f"Wind Range: {min(winds):.1f} - {max(winds):.1f} m/s")
print(f"Humidity Range: {min(humidities)}% - {max(humidities)}%")
print(f"Pressure Range: {min(pressures)} - {max(pressures)} hPa")
print(f"Temperature Range: {min(temps):.1f}°C - {max(temps):.1f}°C")
print()

print("🔍 POSSIBLE ALGORITHMS THAT COULD PRODUCE 'DUST (HIGH)':")
print()

# Test Algorithm 1: Very loose wind-based
print("1️⃣ ALGORITHM: Wind > 7 m/s = High Risk")
print("   Logic: if wind > 7: return 'High'")
all_match_1 = all(d["wind"] > 7 for d in test_data)
print(f"   Result: {'✅ MATCHES' if all_match_1 else '❌ FAILS'}")
if not all_match_1:
    failures = [d["time"] for d in test_data if d["wind"] <= 7]
    print(f"   Failures: {failures}")
print()

# Test Algorithm 2: Combination with low thresholds
print("2️⃣ ALGORITHM: Wind > 6 AND Humidity < 45")
print("   Logic: if wind > 6 and humidity < 45: return 'High'")
all_match_2 = all(d["wind"] > 6 and d["humidity"] < 45 for d in test_data)
print(f"   Result: {'✅ MATCHES' if all_match_2 else '❌ FAILS'}")
if not all_match_2:
    failures = [f"{d['time']} (W:{d['wind']}, H:{d['humidity']})" for d in test_data if not (d["wind"] > 6 and d["humidity"] < 45)]
    print(f"   Failures: {failures}")
print()

# Test Algorithm 3: Simple humidity threshold
print("3️⃣ ALGORITHM: Humidity < 45% = High Risk")
print("   Logic: if humidity < 45: return 'High'")
all_match_3 = all(d["humidity"] < 45 for d in test_data)
print(f"   Result: {'✅ MATCHES' if all_match_3 else '❌ FAILS'}")
if not all_match_3:
    failures = [f"{d['time']} (H:{d['humidity']}%)" for d in test_data if d["humidity"] >= 45]
    print(f"   Failures: {failures}")
print()

# Test Algorithm 4: Temperature-based
print("4️⃣ ALGORITHM: Temperature > 29°C = High Risk")
print("   Logic: if temp > 29: return 'High'")
all_match_4 = all(d["temp"] > 29 for d in test_data)
print(f"   Result: {'✅ MATCHES' if all_match_4 else '❌ FAILS'}")
if not all_match_4:
    failures = [f"{d['time']} (T:{d['temp']}°C)" for d in test_data if d["temp"] <= 29]
    print(f"   Failures: {failures}")
print()

# Test Algorithm 5: Multiple loose conditions
print("5️⃣ ALGORITHM: Wind > 6 OR Humidity < 45 OR Temp > 29")
print("   Logic: if wind > 6 or humidity < 45 or temp > 29: return 'High'")
all_match_5 = all(d["wind"] > 6 or d["humidity"] < 45 or d["temp"] > 29 for d in test_data)
print(f"   Result: {'✅ MATCHES' if all_match_5 else '❌ FAILS'}")
print()

# Test Algorithm 6: Very inclusive dust conditions
print("6️⃣ ALGORITHM: Wind > 5 AND (Humidity < 50 OR Temp > 25)")
print("   Logic: if wind > 5 and (humidity < 50 or temp > 25): return 'High'")
all_match_6 = all(d["wind"] > 5 and (d["humidity"] < 50 or d["temp"] > 25) for d in test_data)
print(f"   Result: {'✅ MATCHES' if all_match_6 else '❌ FAILS'}")
print()

# Test Algorithm 7: Pressure + other factors
print("7️⃣ ALGORITHM: Pressure < 1000 AND Wind > 5")
print("   Logic: if pressure < 1000 and wind > 5: return 'High'")
all_match_7 = all(d["pressure"] < 1000 and d["wind"] > 5 for d in test_data)
print(f"   Result: {'✅ MATCHES' if all_match_7 else '❌ FAILS'}")
print()

# Check what happens if we ignore 03:00 (the problematic entry)
print("🔍 SPECIAL ANALYSIS: IGNORING 03:00 ENTRY")
print("What if 03:00 is an error and other entries follow a pattern?")
print()

filtered_data = [d for d in test_data if d["time"] != "03:00"]

print("📊 DATA WITHOUT 03:00:")
winds_f = [d["wind"] for d in filtered_data]
humidities_f = [d["humidity"] for d in filtered_data]
print(f"Wind Range: {min(winds_f):.1f} - {max(winds_f):.1f} m/s")
print(f"Humidity Range: {min(humidities_f)}% - {max(humidities_f)}%")
print()

print("8️⃣ ALGORITHM (No 03:00): Wind > 8 = High Risk")
all_match_8 = all(d["wind"] > 8 for d in filtered_data)
print(f"   Result: {'✅ MATCHES' if all_match_8 else '❌ FAILS'}")
print()

print("9️⃣ ALGORITHM (No 03:00): Wind > 8 AND Humidity < 40")
all_match_9 = all(d["wind"] > 8 and d["humidity"] < 40 for d in filtered_data)
print(f"   Result: {'✅ MATCHES' if all_match_9 else '❌ FAILS'}")
print()

print("=" * 60)
print("🎯 CONCLUSIONS:")
print()

# Summary of working algorithms
working_algorithms = []
if all_match_1: working_algorithms.append("Wind > 7 m/s")
if all_match_2: working_algorithms.append("Wind > 6 AND Humidity < 45")
if all_match_3: working_algorithms.append("Humidity < 45%")
if all_match_4: working_algorithms.append("Temperature > 29°C")
if all_match_5: working_algorithms.append("Wind > 6 OR Humidity < 45 OR Temp > 29")
if all_match_6: working_algorithms.append("Wind > 5 AND (Humidity < 50 OR Temp > 25)")
if all_match_7: working_algorithms.append("Pressure < 1000 AND Wind > 5")

if working_algorithms:
    print(f"✅ ALGORITHMS THAT COULD EXPLAIN YOUR DATA:")
    for i, alg in enumerate(working_algorithms, 1):
        print(f"   {i}. {alg}")
    print()
    print("🔥 MOST LIKELY EXPLANATION:")
    print("   Your system is using a much simpler/looser algorithm")
    print("   than what's in the current codebase files.")
else:
    print("❌ NO SIMPLE ALGORITHM EXPLAINS ALL YOUR DATA")
    print("   This suggests either:")
    print("   1. Complex multi-factor algorithm not reverse-engineerable")
    print("   2. Manual assignment of 'High' risk")
    print("   3. Bug in the system")
    print("   4. Data corruption or misinterpretation")

print()
print("🚨 THE 03:00 PROBLEM:")
print("   Wind: 7.5 m/s, Humidity: 41%, Temp: 29.5°C")
print("   This entry is borderline on most thresholds")
print("   If it truly shows 'High', the algorithm is very aggressive")

print()
print("🔍 NEXT STEPS:")
print("   1. Check what exact Python file is running your dashboard")
print("   2. Look for any recent code changes")
print("   3. Check if there are any config files with thresholds")
print("   4. Test the dashboard manually to see current behavior") 