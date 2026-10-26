import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import folium
from streamlit_folium import st_folium

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="BridgeBox",
    page_icon="B",
    layout="wide"
)

# ---------------- TITLE ----------------
st.title("BridgeBox")
st.subheader("Emergency Risk & Relocation Decision Support System")

st.caption(
    "Risk Identification → Capacity Assessment → Relocation Priority → Emergency Communication"
)

# ---------------- SAMPLE LOCATIONS ----------------
locations = pd.DataFrame({
    "Location": [
        "Village A", "Village B", "Village C",
        "Village D", "Village E"
    ],
    "Latitude": [13.0827, 13.0950, 13.0700, 13.1100, 13.0600],
    "Longitude": [80.2707, 80.2800, 80.2600, 80.2500, 80.2900],
    "Shelter": ["Shelter A", "Shelter B", "Shelter C", "Shelter D", "Shelter E"],
    "Shelter Capacity": [800, 500, 1000, 600, 750]
})

# ---------------- SIDEBAR ----------------
st.sidebar.header("Select Location")

selected_location = st.sidebar.selectbox(
    "Habitation",
    locations["Location"]
)

row = locations[locations["Location"] == selected_location].iloc[0]

st.sidebar.subheader("Environmental Data")

rainfall = st.sidebar.slider("Rainfall (mm)", 0, 500, 180)
water_level = st.sidebar.slider("Water Level (m)", 0.0, 10.0, 4.2)
elevation = st.sidebar.slider("Elevation (m)", 0, 500, 120)
slope = st.sidebar.slider("Slope (°)", 0, 45, 18)

st.sidebar.subheader("Community Data")

population = st.sidebar.number_input(
    "Population at Risk",
    min_value=0,
    max_value=10000,
    value=1250
)

road_access = st.sidebar.slider(
    "Road Accessibility (%)",
    0,
    100,
    60
)

historical_risk = st.sidebar.slider(
    "Historical Hazard Risk (%)",
    0,
    100,
    70
)

# ---------------- ML MODEL ----------------
# Synthetic training data for prototype demonstration

np.random.seed(42)

n = 1000

training_data = pd.DataFrame({
    "rainfall": np.random.uniform(0, 500, n),
    "water_level": np.random.uniform(0, 10, n),
    "elevation": np.random.uniform(0, 500, n),
    "slope": np.random.uniform(0, 45, n),
    "road_access": np.random.uniform(0, 100, n),
    "historical_risk": np.random.uniform(0, 100, n)
})

training_data["risk"] = (
    training_data["rainfall"] * 0.12 +
    training_data["water_level"] * 5 +
    (500 - training_data["elevation"]) * 0.03 +
    training_data["slope"] * 0.4 +
    (100 - training_data["road_access"]) * 0.15 +
    training_data["historical_risk"] * 0.3
)

training_data["risk"] = training_data["risk"].clip(0, 100)

X = training_data.drop(columns=["risk"])
y = training_data["risk"]

model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)

model.fit(X, y)

# ---------------- RISK CALCULATION ----------------

input_data = pd.DataFrame([{
    "rainfall": rainfall,
    "water_level": water_level,
    "elevation": elevation,
    "slope": slope,
    "road_access": road_access,
    "historical_risk": historical_risk
}])

risk_score = float(model.predict(input_data)[0])
risk_score = min(max(risk_score, 0), 100)

if risk_score < 25:
    risk_level = "LOW"
elif risk_score < 50:
    risk_level = "MEDIUM"
elif risk_score < 75:
    risk_level = "HIGH"
else:
    risk_level = "CRITICAL"

# ---------------- CAPACITY ----------------

safe_capacity = int(row["Shelter Capacity"])
capacity_gap = max(population - safe_capacity, 0)

if risk_level == "CRITICAL" or capacity_gap > 300:
    relocation_priority = "IMMEDIATE"
elif risk_level == "HIGH" or capacity_gap > 100:
    relocation_priority = "HIGH"
elif risk_level == "MEDIUM":
    relocation_priority = "MODERATE"
else:
    relocation_priority = "LOW"

# ---------------- METRICS ----------------

st.markdown("### Current Risk Status")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Risk Score",
    f"{risk_score:.0f}/100"
)

col2.metric(
    "Risk Level",
    risk_level
)

col3.metric(
    "Population at Risk",
    population
)

col4.metric(
    "Capacity Gap",
    capacity_gap
)

# ---------------- MAIN TABS ----------------

tab1, tab2, tab3, tab4 = st.tabs([
    "Risk Assessment",
    "GIS Risk Map",
    "Relocation",
    "Emergency Communication"
])

# ==========================================================
# TAB 1 - RISK ASSESSMENT
# ==========================================================

with tab1:

    st.header("AI/ML Risk Assessment")

    st.write(
        "The model analyses environmental, geographical and historical "
        "information to generate a vulnerability score."
    )

    data_display = pd.DataFrame({
        "Parameter": [
            "Rainfall",
            "Water Level",
            "Elevation",
            "Slope",
            "Road Accessibility",
            "Historical Hazard Risk"
        ],
        "Value": [
            f"{rainfall} mm",
            f"{water_level} m",
            f"{elevation} m",
            f"{slope}°",
            f"{road_access}%",
            f"{historical_risk}%"
        ]
    })

    st.dataframe(
        data_display,
        use_container_width=True,
        hide_index=True
    )

    st.progress(int(risk_score))

    st.subheader(f"Risk Classification: {risk_level}")

    if risk_level == "CRITICAL":
        st.error("Immediate intervention and relocation assessment required.")
    elif risk_level == "HIGH":
        st.warning("High vulnerability detected. Prepare relocation.")
    elif risk_level == "MEDIUM":
        st.info("Moderate vulnerability. Continuous monitoring required.")
    else:
        st.success("Low vulnerability detected.")

# ==========================================================
# TAB 2 - GIS MAP
# ==========================================================

with tab2:

    st.header("GIS Vulnerability Map")

    m = folium.Map(
        location=[row["Latitude"], row["Longitude"]],
        zoom_start=13
    )

    # Add habitation markers

    for _, location in locations.iterrows():

        if location["Location"] == selected_location:
            color = "red"
        else:
            color = "green"

        folium.Marker(
            location=[
                location["Latitude"],
                location["Longitude"]
            ],
            popup=(
                f"<b>{location['Location']}</b><br>"
                f"Shelter: {location['Shelter']}<br>"
                f"Capacity: {location['Shelter Capacity']}"
            ),
            icon=folium.Icon(color=color)
        ).add_to(m)

    st_folium(
        m,
        width=1000,
        height=500
    )

    st.info(
        "Red marker: selected/high-risk habitation | "
        "Green markers: other locations/safe points"
    )

# ==========================================================
# TAB 3 - RELOCATION
# ==========================================================

with tab3:

    st.header("Carrying Capacity & Relocation Priority")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Population at Risk",
        population
    )

    col2.metric(
        "Available Safe Capacity",
        safe_capacity
    )

    col3.metric(
        "Capacity Gap",
        capacity_gap
    )

    st.divider()

    st.subheader("Relocation Decision")

    st.write(
        f"**Affected Habitation:** {selected_location}"
    )

    st.write(
        f"**Relocation Priority:** {relocation_priority}"
    )

    st.write(
        f"**Recommended Shelter:** {row['Shelter']}"
    )

    if relocation_priority == "IMMEDIATE":
        st.error(
            "IMMEDIATE RELOCATION REQUIRED"
        )
    elif relocation_priority == "HIGH":
        st.warning(
            "HIGH PRIORITY RELOCATION"
        )
    else:
        st.info(
            "Relocation monitoring recommended."
        )

# ==========================================================
# TAB 4 - COMMUNICATION
# ==========================================================

with tab4:

    st.header("BridgeBox Emergency Communication")

    st.write(
        "Emergency decisions can be transmitted through "
        "LoRa/RF when Internet or cellular networks are unavailable."
    )

    message = st.text_area(
        "Emergency Message",
        value=(
            f"WARNING: {selected_location} has been classified as "
            f"{risk_level} risk. Relocation priority: "
            f"{relocation_priority}. Proceed to {row['Shelter']}."
        )
    )

    if st.button("SEND EMERGENCY ALERT"):

        st.success(
            "Emergency alert prepared for BridgeBox LoRa/RF transmission."
        )

        st.code(
            f"""
BRIDGEBOX MESSAGE
-------------------------
Location: {selected_location}
Risk: {risk_level}
Risk Score: {risk_score:.0f}/100
Priority: {relocation_priority}

Message:
{message}

Communication: LoRa / RF
Status: READY FOR TRANSMISSION
            """
        )

# ---------------- FOOTER ----------------

st.divider()

st.caption(
    "BridgeBox | AI-assisted Risk Assessment • GIS • "
    "Carrying Capacity • Relocation • LoRa/RF Communication"
)