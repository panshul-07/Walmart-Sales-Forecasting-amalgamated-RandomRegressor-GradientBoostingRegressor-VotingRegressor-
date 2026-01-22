import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io

st.set_page_config(
    page_title="Walmart Demand Forecasting",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
        .kpi-card {
            background-color: #111;
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #222;
        }
        .kpi-title {
            font-size: 14px;
            color: #aaa;
        }
        .kpi-value {
            font-size: 32px;
            font-weight: 600;
        }
        .section {
            margin-top: 40px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Walmart Demand Forecasting")

@st.cache_data
def load_data():
    if "csv_data" not in st.secrets:
        st.error("csv_data missing in Streamlit Secrets")
        st.stop()
    df = pd.read_csv(io.StringIO(st.secrets["csv_data"]))
    df.columns = df.columns.str.strip()
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)
    return df

df = load_data()

# ---------------- SIDEBAR ----------------
st.sidebar.header("Input Parameters")

store_id = st.sidebar.number_input(
    "Store",
    min_value=int(df["Store"].min()),
    max_value=int(df["Store"].max()),
    value=int(df["Store"].min())
)

holiday_flag = st.sidebar.toggle("Holiday Week")
temperature = st.sidebar.slider("Temperature (°F)", 20.0, 120.0, 70.0)
fuel_price = st.sidebar.slider("Fuel Price ($/gal)", 2.0, 5.0, 3.5)
cpi = st.sidebar.slider("CPI", 200.0, 300.0, 220.0)
unemployment = st.sidebar.slider("Unemployment Rate (%)", 3.0, 15.0, 7.0)

# ---------------- MODEL ----------------
store_df = df[df["Store"] == store_id].sort_values("Date")
avg_sales = store_df["Weekly_Sales"].mean()

CONST = avg_sales
COEF_HOLIDAY = 6634.0369
COEF_FUEL = 11830.0
COEF_CPI = -9.8499
COEF_UNEMP = -418.9919
TEMP_OPTIMAL = 70.0
TEMP_CURVATURE = -196.8391

def temp_effect(t):
    return TEMP_CURVATURE * (t - TEMP_OPTIMAL) ** 2

def base_prediction():
    return (
        CONST
        + COEF_HOLIDAY * int(holiday_flag)
        + COEF_FUEL * fuel_price
        + COEF_CPI * cpi
        + COEF_UNEMP * unemployment
    )

predicted_sales = base_prediction() + temp_effect(temperature)

# ---------------- KPI SECTION ----------------
st.markdown('<div class="section"></div>', unsafe_allow_html=True)

k1, k2, k3 = st.columns(3)

with k1:
    st.markdown(
        f"<div class='kpi-card'><div class='kpi-title'>Predicted Weekly Sales</div>"
        f"<div class='kpi-value'>${predicted_sales:,.0f}</div></div>",
        unsafe_allow_html=True
    )

with k2:
    st.markdown(
        f"<div class='kpi-card'><div class='kpi-title'>Average Store Sales</div>"
        f"<div class='kpi-value'>${avg_sales:,.0f}</div></div>",
        unsafe_allow_html=True
    )

with k3:
    delta = ((predicted_sales - avg_sales) / avg_sales) * 100
    st.markdown(
        f"<div class='kpi-card'><div class='kpi-title'>Change vs Average</div>"
        f"<div class='kpi-value'>{delta:.2f}%</div></div>",
        unsafe_allow_html=True
    )

# ---------------- TREND ----------------
st.markdown('<div class="section"></div>', unsafe_allow_html=True)
st.subheader("Recent Sales Trend")

recent = store_df.tail(20)

fig, ax = plt.subplots(figsize=(12, 4))
ax.plot(recent["Date"], recent["Weekly_Sales"], color="#4da6ff", marker="o")
ax.axhline(predicted_sales, linestyle="--", color="#ff4d4d", label="Prediction")
ax.legend()
ax.grid(alpha=0.2)
ax.set_facecolor("#0e1117")
fig.patch.set_facecolor("#0e1117")
ax.yaxis.set_major_formatter('${x:,.0f}')
st.pyplot(fig, use_container_width=True)

# ---------------- SENSITIVITY ----------------
st.markdown('<div class="section"></div>', unsafe_allow_html=True)
st.subheader("Sensitivity Analysis")

def plot_sensitivity(x, y, current_x, title, xlabel):
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(x, y, color="#00e5ff", linewidth=2)
    ax.fill_between(x, y, color="#00e5ff", alpha=0.15)
    ax.axvline(current_x, color="#ff4d4d", linestyle="--")
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.grid(alpha=0.2)
    ax.set_facecolor("#0e1117")
    fig.patch.set_facecolor("#0e1117")
    ax.yaxis.set_major_formatter('${x:,.0f}')
    return fig

c1, c2 = st.columns(2)

# Temperature
t_range = np.linspace(20, 120, 100)
t_sales = base_prediction() + temp_effect(t_range)
with c1:
    st.pyplot(plot_sensitivity(t_range, t_sales, temperature,
              "Temperature Sensitivity", "Temperature (°F)"))

# Fuel
f_range = np.linspace(2, 5, 100)
f_sales = predicted_sales + COEF_FUEL * (f_range - fuel_price)
with c2:
    st.pyplot(plot_sensitivity(f_range, f_sales, fuel_price,
              "Fuel Price Sensitivity", "Fuel ($/gal)"))

# CPI
c_range = np.linspace(200, 300, 100)
c_sales = predicted_sales + COEF_CPI * (c_range - cpi)
with c1:
    st.pyplot(plot_sensitivity(c_range, c_sales, cpi,
              "CPI Sensitivity", "CPI"))

# Unemployment
u_range = np.linspace(3, 15, 100)
u_sales = predicted_sales + COEF_UNEMP * (u_range - unemployment)
with c2:
    st.pyplot(plot_sensitivity(u_range, u_sales, unemployment,
              "Unemployment Sensitivity", "Unemployment (%)"))

st.caption("Walmart Demand Forecasting")
