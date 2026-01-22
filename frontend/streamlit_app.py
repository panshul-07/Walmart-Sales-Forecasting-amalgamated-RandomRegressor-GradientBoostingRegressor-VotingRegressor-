import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io
import os

st.set_page_config(
    page_title="Walmart Demand Forecasting",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
        .kpi-card {
            background: linear-gradient(145deg, #0f0f0f, #161616);
            padding: 22px;
            border-radius: 14px;
            border: 1px solid #222;
            box-shadow: 0 0 25px rgba(0,0,0,0.4);
        }
        .kpi-title {
            font-size: 14px;
            color: #aaa;
        }
        .kpi-value {
            font-size: 32px;
            font-weight: 600;
            margin-top: 6px;
        }
        .section {
            margin-top: 50px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Walmart Demand Forecasting")

# ---------------- DATA LOADING ----------------
@st.cache_data
def load_data():
    if "csv_data" in st.secrets:
        df = pd.read_csv(io.StringIO(st.secrets["csv_data"]))
    else:
        df = pd.read_csv("data/raw/store_history.csv")

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

# ---------------- MODEL (COEFF-BASED) ----------------
store_df = df[df["Store"] == store_id].sort_values("Date")
avg_sales = store_df["Weekly_Sales"].mean()

CONST = avg_sales
COEF_HOLIDAY = 6634.0369
COEF_FUEL = 11830.0
COEF_CPI = -9.8499
COEF_UNEMP = -418.9919
TEMP_OPTIMAL = 70.0
TEMP_CURVATURE = -196.8391

def temperature_effect(t):
    return TEMP_CURVATURE * (t - TEMP_OPTIMAL) ** 2

def predict_sales(temp, fuel, cpi_val, unemp):
    return (
        CONST
        + COEF_HOLIDAY * int(holiday_flag)
        + temperature_effect(temp)
        + COEF_FUEL * fuel
        + COEF_CPI * cpi_val
        + COEF_UNEMP * unemp
    )

predicted_sales = predict_sales(temperature, fuel_price, cpi, unemployment)

# ---------------- KPI CARDS ----------------
st.markdown('<div class="section"></div>', unsafe_allow_html=True)

k1, k2, k3 = st.columns(3)

with k1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Predicted Weekly Sales</div>
            <div class="kpi-value">${predicted_sales:,.0f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with k2:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Average Store Sales</div>
            <div class="kpi-value">${avg_sales:,.0f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with k3:
    delta = ((predicted_sales - avg_sales) / avg_sales) * 100
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Change vs Average</div>
            <div class="kpi-value">{delta:.2f}%</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------------- RECENT TREND (PLOTLY) ----------------
st.markdown('<div class="section"></div>', unsafe_allow_html=True)
st.subheader("Recent Sales Trend")

recent = store_df.tail(20)

fig_trend = go.Figure()

fig_trend.add_trace(go.Scatter(
    x=recent["Date"],
    y=recent["Weekly_Sales"],
    mode="lines+markers",
    name="Actual",
    line=dict(width=3)
))

fig_trend.add_hline(
    y=predicted_sales,
    line_dash="dash",
    line_color="red",
    annotation_text="Prediction",
    annotation_position="top right"
)

fig_trend.update_layout(
    template="plotly_dark",
    height=420,
    yaxis_tickprefix="$",
    yaxis_tickformat=",.0f"
)

st.plotly_chart(fig_trend, use_container_width=True)

# ---------------- SENSITIVITY ANALYSIS ----------------
st.markdown('<div class="section"></div>', unsafe_allow_html=True)
st.subheader("Sensitivity Analysis")

def sensitivity_plot(x, y, xlabel, vline):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, fill="tozeroy", line=dict(width=3)))
    fig.add_vline(x=vline, line_dash="dash", line_color="red")
    fig.update_layout(
        template="plotly_dark",
        height=350,
        xaxis_title=xlabel,
        yaxis_tickprefix="$",
        yaxis_tickformat=",.0f"
    )
    return fig

t_range = np.linspace(20, 120, 100)
f_range = np.linspace(2, 5, 80)
c_range = np.linspace(200, 300, 80)
u_range = np.linspace(3, 15, 80)

col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(
        sensitivity_plot(
            t_range,
            [predict_sales(t, fuel_price, cpi, unemployment) for t in t_range],
            "Temperature (°F)",
            temperature
        ),
        use_container_width=True
    )

with col2:
    st.plotly_chart(
        sensitivity_plot(
            f_range,
            [predict_sales(temperature, f, cpi, unemployment) for f in f_range],
            "Fuel Price ($/gal)",
            fuel_price
        ),
        use_container_width=True
    )

col3, col4 = st.columns(2)

with col3:
    st.plotly_chart(
        sensitivity_plot(
            c_range,
            [predict_sales(temperature, fuel_price, c, unemployment) for c in c_range],
            "CPI",
            cpi
        ),
        use_container_width=True
    )

with col4:
    st.plotly_chart(
        sensitivity_plot(
            u_range,
            [predict_sales(temperature, fuel_price, cpi, u) for u in u_range],
            "Unemployment Rate (%)",
            unemployment
        ),
        use_container_width=True
    )

st.caption("Walmart Demand Forecasting")
