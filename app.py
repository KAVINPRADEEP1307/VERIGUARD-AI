import streamlit as st
import pandas as pd
import random
import time
import math
import requests
import sqlite3
from sklearn.tree import DecisionTreeClassifier

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="VeriGuard AI 🚨", layout="centered")

# ------------------ UI STYLE ------------------
st.markdown("""
<style>
.stApp {
    background-color: #0E1117;
    color: white;
}
.block-container {
    max-width: 500px;
    margin: auto;
}
.stButton>button {
    width: 100%;
    border-radius: 10px;
    background-color: #00FFCC;
    color: black;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ------------------ TITLE ------------------
st.title("🚨 VeriGuard AI")
st.caption("AI Emergency Assistant")
st.success("🟢 System Active")

# ------------------ INPUT ------------------
st.subheader("📥 Enter Emergency Details")

name = st.text_input("👤 Name")
location = st.text_input("📍 Location")

symptom = st.selectbox(
    "⚠️ Select Symptom",
    ["Chest Pain", "Accident", "Fever", "Headache", "Minor Injury"]
)

analyze = st.button("🚀 Analyze")

# ------------------ DATABASE ------------------
conn = sqlite3.connect("emergency.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS cases (
    name TEXT,
    location TEXT,
    symptom TEXT,
    severity TEXT,
    hospital TEXT
)
""")
conn.commit()

# ------------------ ML MODEL ------------------
X = [[1,0,0],[1,1,0],[0,1,0],[0,0,1],[0,0,1]]
y = ["Critical","Critical","Moderate","Low","Low"]

model = DecisionTreeClassifier()
model.fit(X, y)

def encode(symptom):
    if symptom == "Chest Pain":
        return [1,0,0]
    elif symptom == "Accident":
        return [1,1,0]
    elif symptom == "Fever":
        return [0,1,0]
    else:
        return [0,0,1]

# ------------------ HOSPITAL API ------------------
def get_hospitals(lat, lon):
    url = "http://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    node[amenity=hospital](around:3000,{lat},{lon});
    out;
    """
    res = requests.get(url, params={'data': query})
    data = res.json()

    hospitals = []
    for e in data['elements'][:5]:
        name = e['tags'].get('name', 'Hospital')
        h_lat = e['lat']
        h_lon = e['lon']
        dist = math.sqrt((lat-h_lat)**2 + (lon-h_lon)**2) * 111

        hospitals.append({
            "name": name,
            "lat": h_lat,
            "lon": h_lon,
            "distance": round(dist, 2)
        })
    return hospitals

# ------------------ AMBULANCE ------------------
def move(start_lat, start_lon, end_lat, end_lon):
    steps = 20
    path = []
    for i in range(steps):
        lat = start_lat + (end_lat-start_lat) * i / steps
        lon = start_lon + (end_lon-start_lon) * i / steps
        path.append((lat, lon))
    return path

# ------------------ MAIN ------------------
if analyze:

    if name == "" or location == "":
        st.warning("⚠️ Please enter all details")
    else:

        severity = model.predict([encode(symptom)])[0]
        st.subheader(f"🧠 Severity: {severity}")

        if severity == "Critical":
            st.error("🚨 CRITICAL EMERGENCY 🚨")
        elif severity == "Moderate":
            st.warning("⚠️ Moderate Condition")
        else:
            st.success("🙂 Low Risk")

        # Fake location
        lat = 13.0827 + random.uniform(-0.01, 0.01)
        lon = 80.2707 + random.uniform(-0.01, 0.01)

        hospital_list = get_hospitals(lat, lon)

        if hospital_list:
            nearest = min(hospital_list, key=lambda x: x['distance'])
            hospital = nearest['name']
        else:
            hospital = "No hospital found"

        st.write(f"🏥 Assigned Hospital: {hospital}")

        # Save to DB
        cursor.execute(
            "INSERT INTO cases VALUES (?, ?, ?, ?, ?)",
            (name, location, symptom, severity, hospital)
        )
        conn.commit()

        # Hospitals
        st.subheader("🏥 Nearby Hospitals")
        for h in hospital_list:
            st.write(f"{h['name']} - {h['distance']} km")

        # Map
        st.subheader("📍 Map")
        map_data = pd.DataFrame({
            "lat": [lat] + [h['lat'] for h in hospital_list],
            "lon": [lon] + [h['lon'] for h in hospital_list]
        })
        st.map(map_data)

        # Navigation
        maps_url = f"https://www.google.com/maps/dir/{lat},{lon}/{nearest['lat']},{nearest['lon']}"
        st.markdown(f"[🗺️ Navigate to Hospital]({maps_url})")

        # Ambulance
        st.subheader("🚑 Ambulance Tracking")
        path = move(lat, lon, nearest['lat'], nearest['lon'])

        placeholder = st.empty()
        for p in path:
            df = pd.DataFrame({"lat": [p[0]], "lon": [p[1]]})
            placeholder.map(df)
            time.sleep(0.2)

        # Dashboard
        st.subheader("📊 Dashboard")
        chart = pd.DataFrame({
            "Critical": [random.randint(5,15)],
            "Moderate": [random.randint(10,20)],
            "Low": [random.randint(15,30)]
        })
        st.bar_chart(chart)

# ------------------ HISTORY ------------------
st.subheader("📊 Case History")
data = cursor.execute("SELECT * FROM cases").fetchall()
df = pd.DataFrame(data, columns=["Name","Location","Symptom","Severity","Hospital"])
st.dataframe(df)

st.caption("🚀 Built for Hackathon")
