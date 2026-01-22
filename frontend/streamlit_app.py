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

# ---------- GLOBAL STYLES ----------
st.markdown(
    """
    <style>
        .kpi-card {
            background-color: #111;
            padding: 20px;
            border-radius: 14px;
            border: 1px solid #222;
        }
        .kpi-title {
            font-size: 13px;
            color: #9ca3af;
        }
        .kpi-value {
            font-size: 32px;
            font-weight: 600;
            color: white;
        }
        .section {
            margin-top: 40px;
        }
        .stPyplot {
            transition: all 0.3s ease-in-out;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Walmart Demand Forecasting")

# ---------- DATA LOADING ----------
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

# ---------- SIDEBAR ----------
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

# ---------- MODEL ----------
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

# ---------- KPI CARDS ----------
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

# ---------- RECENT TREND ----------
st.markdown('<div class="section"></div>', unsafe_allow_html=True)
st.subheader("Recent Sales Trend")

recent = store_df.tail(20)

fig, ax = plt.subplots(figsize=(12, 4))
ax.plot(recent["Date"], recent["Weekly_Sales"], color="#4da6ff", linewidth=2.5, marker="o")
ax.fill_between(recent["Date"], recent["Weekly_Sales"], color="#4da6ff", alpha=0.08)
ax.axhline(predicted_sales, linestyle="--", color="#ff4d4d", label="Prediction")

ax.legend()
ax.grid(alpha=0.2)
ax.set_facecolor("#0e1117")
fig.patch.set_facecolor("#0e1117")
ax.yaxis.set_major_formatter('${x:,.0f}')

st.pyplot(fig, use_container_width=True)

# ---------- SENSITIVITY ----------
st.markdown('<div class="section"></div>', unsafe_allow_html=True)
st.subheader("Sensitivity Analysis")

st.markdown(
    f"<div style='color:#9ca3af; margin-bottom:12px;'>"
    f"Sales response around current operating point (${predicted_sales:,.0f})"
    f"</div>",
    unsafe_allow_html=True
)

def plot_sensitivity(x, y, current_x, title, xlabel):
    fig, ax = plt.subplots(figsize=(6, 4))

    ax.plot(x, y, color="#00e5ff", linewidth=2.5)

    for a in np.linspace(0.02, 0.12, 6):
        ax.fill_between(x, y, color="#00e5ff", alpha=a)

    current_y = np.interp(current_x, x, y)
    ax.scatter(current_x, current_y, s=120, color="#ff4d4d",
               edgecolors="white", linewidths=1.5, zorder=5)

    ax.annotate(
        f"${current_y:,.0f}",
        (current_x, current_y),
        xytext=(8, 8),
        textcoords="offset points",
        fontsize=10,
        color="white",
        weight="bold"
    )

    ax.axvline(current_x, color="#ff4d4d", linestyle="--", alpha=0.8)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.grid(alpha=0.2)

    ax.set_facecolor("#0e1117")
    fig.patch.set_facecolor("#0e1117")
    ax.yaxis.set_major_formatter('${x:,.0f}')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#333')
    ax.spines['bottom'].set_color('#333')

    return fig

c1, c2 = st.columns(2)

# Temperature
t = np.linspace(20, 120, 100)
with c1:
    st.pyplot(plot_sensitivity(
        t, base_prediction() + temp_effect(t),
        temperature, "Temperature Sensitivity", "Temperature (°F)"
    ))

# Fuel
f = np.linspace(2, 5, 100)
with c2:
    st.pyplot(plot_sensitivity(
        f, predicted_sales + COEF_FUEL * (f - fuel_price),
        fuel_price, "Fuel Price Sensitivity", "Fuel ($/gal)"
    ))

# CPI
c = np.linspace(200, 300, 100)
with c1:
    st.pyplot(plot_sensitivity(
        c, predicted_sales + COEF_CPI * (c - cpi),
        cpi, "CPI Sensitivity", "CPI"
    ))

# Unemployment
u = np.linspace(3, 15, 100)
with c2:
    st.pyplot(plot_sensitivity(
        u, predicted_sales + COEF_UNEMP * (u - unemployment),
        unemployment, "Unemployment Sensitivity", "Unemployment (%)"
    ))

st.caption("Walmart Demand Forecasting")
