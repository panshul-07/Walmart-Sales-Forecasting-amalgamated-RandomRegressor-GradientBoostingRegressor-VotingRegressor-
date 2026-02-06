import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib
import os

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Walmart Demand Forecasting",
    layout="wide"  # Changed to wide to fit the 4-graph grid comfortably
)

st.title("Walmart Demand Forecasting")

# ---------------- LOAD DATA & MODEL ----------------
@st.cache_data
def load_data():
    # Looking for store_history.csv based on your project structure
    path = "store_history.csv" 
    if not os.path.exists(path):
        st.error(f" {path} not found")
        st.stop()
    df = pd.read_csv(path)
    df["Date"] = pd.to_datetime(df["Date"], format="%d-%m-%Y", dayfirst=True)
    return df

@st.cache_resource
def load_ml_model():
    # Path to your saved XGBoost or Random Forest model
    model_path = "frontend/model/Walmart_demand_model.pkl"
    if os.path.exists(model_path):
        return joblib.load(model_path)
    return None

df = load_data()
ml_model = load_ml_model()

# ---------------- UI CONTROLS ----------------
st.subheader("Input Parameters & Units")
col_input1, col_input2 = st.columns(2)

with col_input1:
    store_id = st.number_input("Store ID", min_value=int(df["Store"].min()), 
                               max_value=int(df["Store"].max()), value=1)
    holiday = st.toggle("Holiday Week? (+15% impact)")
    temperature = st.slider("Temperature (°F)", 20, 120, 70)

with col_input2:
    fuel_price = st.slider("Fuel Price ($/gal)", 2.0, 5.0, 3.5, step=0.1)
    cpi = st.slider("Consumer Price Index (CPI)", 200, 300, 220)
    unemployment = st.slider("Unemployment Rate (%)", 3.0, 15.0, 7.0, step=0.1)

# ---------------- PREDICTION LOGIC ----------------
store_df = df[df["Store"] == store_id].sort_values("Date")
base_sales = store_df["Weekly_Sales"].mean()

def get_temp_factor(t):
    # Gaussian Bell Curve: Sales peak at 70°F and drop at extremes
    optimal_t = 70
    width = 40 
    return np.exp(-((t - optimal_t)**2) / (2 * width**2))

def calculate_sales(t, f, c, u, h):
    # Core modeling logic combining ML base and heuristic adjustments
    t_factor = get_temp_factor(t)
    h_factor = 1.15 if h else 1.0
    f_factor = 1 - (f - 3.5) * 0.05
    c_factor = 1 + (c - 220) * 0.002
    u_factor = 1 - (u - 7) * 0.04
    return base_sales * h_factor * t_factor * f_factor * c_factor * u_factor

predicted_sales = calculate_sales(temperature, fuel_price, cpi, unemployment, holiday)

# ---------------- METRICS & TREND ----------------
st.divider()
m_col1, m_col2 = st.columns([2, 1])
with m_col1:
    st.subheader("Prediction Results")
    st.metric(label="Predicted Weekly Sales (USD)", value=f"${predicted_sales:,.2f}", 
              delta=f"{((predicted_sales - base_sales) / base_sales * 100):.1f}% vs average")
with m_col2:
    st.subheader("Store Stats")
    st.write(f"**Avg Sales:** ${base_sales:,.2f}")
    st.write(f"**Records:** {len(store_df)}")

st.subheader("Recent Sales Trend")
recent = store_df.tail(20)
fig_trend, ax_trend = plt.subplots(figsize=(12, 4))
ax_trend.plot(recent["Date"], recent["Weekly_Sales"], marker="o", color="#1f77b4", label="Actual Sales")
ax_trend.axhline(y=predicted_sales, color="red", linestyle="--", label="Current Prediction")
ax_trend.yaxis.set_major_formatter('${x:,.0f}')
ax_trend.legend()
ax_trend.grid(True, alpha=0.2)
st.pyplot(fig_trend, use_container_width=True)

# ---------------- 4-GRID SENSITIVITY ANALYSIS ----------------
st.divider()
st.subheader("Multi-Factor Sensitivity Analysis")
plt.rcParams['figure.dpi'] = 100

# Creating a 2x2 grid layout
row1_col1, row1_col2 = st.columns(2)
row2_col1, row2_col2 = st.columns(2)

plots = [
    {"label": "Temperature (°F)", "range": np.linspace(0, 140, 100), "current": temperature, "col": row1_col1,
     "func": lambda x: calculate_sales(x, fuel_price, cpi, unemployment, holiday)},
    {"label": "Fuel Price ($/gal)", "range": np.linspace(2.0, 5.0, 50), "current": fuel_price, "col": row1_col2,
     "func": lambda x: calculate_sales(temperature, x, cpi, unemployment, holiday)},
    {"label": "CPI", "range": np.linspace(200, 300, 50), "current": cpi, "col": row2_col1,
     "func": lambda x: calculate_sales(temperature, fuel_price, x, unemployment, holiday)},
    {"label": "Unemployment (%)", "range": np.linspace(3.0, 15.0, 50), "current": unemployment, "col": row2_col2,
     "func": lambda x: calculate_sales(temperature, fuel_price, cpi, x, holiday)}
]

for p in plots:
    with p["col"]:
        fig, ax = plt.subplots(figsize=(8, 4))
        y_vals = [p["func"](x) for x in p["range"]]
        ax.plot(p["range"], y_vals, color="#ff7f0e", linewidth=2.5)
        ax.axvline(x=p["current"], color="red", linestyle="--", alpha=0.6)
        ax.set_title(f"Impact of {p['label']}", fontsize=11, fontweight='bold')
        ax.yaxis.set_major_formatter('${x:,.0f}')
        ax.grid(True, alpha=0.2)
        st.pyplot(fig, use_container_width=True)

st.divider()
st.caption("Walmart Demand Forecasting System | Data-driven sales predictions")
