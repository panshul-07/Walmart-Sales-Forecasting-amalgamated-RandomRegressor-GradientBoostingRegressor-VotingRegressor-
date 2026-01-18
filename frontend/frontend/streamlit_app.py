import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Walmart Demand Forecasting",
    layout="centered"
)

st.title("Walmart Demand Forecasting")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    path = "../data/store_history.csv"
    if not os.path.exists(path):
        st.error(" data/store_history.csv not found")
        st.stop()
    df = pd.read_csv(path)
    df["Date"] = pd.to_datetime(df["Date"], format="%d-%m-%Y", dayfirst=True)
    return df

df = load_data()

# ---------------- UI CONTROLS ----------------
st.subheader("Input Parameters & Units")

col1, col2 = st.columns(2)

with col1:
    store_id = st.number_input(
        "Store ID",
        min_value=int(df["Store"].min()),
        max_value=int(df["Store"].max()),
        value=int(df["Store"].iloc[0]),
        step=1
    )
    holiday = st.toggle("Holiday Week? (+15% impact)")
 
    temperature = st.slider("Temperature (°F)", 20, 120, 70)

with col2:
    fuel_price = st.slider("Fuel Price ($/gal)", 2.0, 5.0, 3.5, step=0.1)
    cpi = st.slider("Consumer Price Index (CPI)", 200, 300, 220)
    unemployment = st.slider("Unemployment Rate (%)", 3.0, 15.0, 7.0, step=0.1)

# ---------------- ECONOMIC EFFECT MODEL ----------------
store_df = df[df["Store"] == store_id].sort_values("Date")
if len(store_df) == 0:
    st.error(f"No data found for Store {store_id}")
    st.stop()

base_sales = store_df["Weekly_Sales"].mean()

# BELL CURVE CALCULATION
def get_temp_factor(t):
    optimal_t = 70
    width = 40 
    return np.exp(-((t - optimal_t)**2) / (2 * width**2))

temp_factor = get_temp_factor(temperature)
holiday_factor = 1.15 if holiday else 1.0
fuel_factor = 1 - (fuel_price - 3.5) * 0.05
cpi_factor = 1 + (cpi - 220) * 0.002
unemp_factor = 1 - (unemployment - 7) * 0.04

predicted_sales = (
    base_sales * holiday_factor * temp_factor * fuel_factor * cpi_factor * unemp_factor
)

# ---------------- PREDICTION DISPLAY ----------------
st.divider()
p_col1, p_col2 = st.columns([2, 1])

with p_col1:
    st.subheader("Prediction Results")
    st.metric(
        label="Predicted Weekly Sales (USD)",
        value=f"${predicted_sales:,.2f}",
        delta=f"{((predicted_sales - base_sales) / base_sales * 100):.1f}% vs historical avg"
    )

with p_col2:
    st.subheader("Store Stats")
    st.write(f"**Avg Sales:** ${base_sales:,.2f}")
    st.write(f"**Records:** {len(store_df)}")

# ---------------- RECENT SALES TREND ----------------
st.divider()
st.subheader("Recent Sales Trend")
recent = store_df.tail(20)
plt.rcParams['figure.dpi'] = 100
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(recent["Date"], recent["Weekly_Sales"], marker="o", color="#1f77b4", label="Actual Sales")
ax.axhline(y=predicted_sales, color="red", linestyle="--", label="Current Prediction")
ax.set_ylabel("Sales ($)")
ax.yaxis.set_major_formatter('${x:,.0f}')
ax.legend()
ax.grid(True, alpha=0.2)
st.pyplot(fig, use_container_width=True)

# ---------------- SENSITIVITY ANALYSIS ----------------
st.divider()
st.subheader("Sensitivity Analysis")
param_choice = st.selectbox(
    "Analyze Impact of:",
    ["Temperature (°F)", "Fuel Price ($/gal)", "CPI", "Unemployment (%)"]
)

fig2, ax2 = plt.subplots(figsize=(10, 4))

# Generate sensitivity data based on selected parameter
if param_choice == "Temperature (°F)":
    x_range = np.linspace(0, 140, 100)
    y_vals = [base_sales * holiday_factor * get_temp_factor(x) * fuel_factor * cpi_factor * unemp_factor for x in x_range]
    current_x = temperature
elif param_choice == "Fuel Price ($/gal)":
    x_range = np.linspace(2.0, 5.0, 50)
    y_vals = [base_sales * holiday_factor * temp_factor * (1 - (x - 3.5) * 0.05) * cpi_factor * unemp_factor for x in x_range]
    current_x = fuel_price
elif param_choice == "CPI":
    x_range = np.linspace(200, 300, 50)
    y_vals = [base_sales * holiday_factor * temp_factor * fuel_factor * (1 + (x - 220) * 0.002) * unemp_factor for x in x_range]
    current_x = cpi
else: # Unemployment
    x_range = np.linspace(3.0, 15.0, 50)
    y_vals = [base_sales * holiday_factor * temp_factor * fuel_factor * cpi_factor * (1 - (x - 7) * 0.04) for x in x_range]
    current_x = unemployment

ax2.plot(x_range, y_vals, color="#ff7f0e", linewidth=3)
ax2.axvline(x=current_x, color="red", linestyle="--", label=f"Current: {current_x}")
ax2.set_xlabel(param_choice)
ax2.set_ylabel("Predicted Sales ($)")
ax2.yaxis.set_major_formatter('${x:,.0f}')
ax2.legend()
ax2.grid(True, alpha=0.2)
st.pyplot(fig2, use_container_width=True)

st.divider()
st.caption("Walmart Demand Forecasting System | Data-driven sales predictions")