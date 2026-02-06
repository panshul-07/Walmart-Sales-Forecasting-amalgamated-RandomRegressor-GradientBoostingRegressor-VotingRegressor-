

## To install and run,
* run in a terminal of your choice 

    ```bash
    pip install -r requirements.txt
    ```

* then run 
     ```bash
     streamlit run frontend/streamlit_app.py
     ```
 
 # Walmart Demand Forecasting System

## Project Overview

This project implements an interactive demand forecasting system for Walmart stores using an **amalgamated ensemble of machine learning models** combined with a **Streamlit-based analytical dashboard**.

The system predicts **weekly sales** for individual Walmart stores and allows users to analyze how external and economic factors influence demand. The project emphasizes **accuracy, interpretability, and deployment readiness**, making it suitable for academic evaluation and real-world retail analytics use cases.

---

## Objectives

- Forecast weekly sales using ensemble machine learning
- Capture non-linear demand patterns in retail data
- Provide interpretable sensitivity analysis
- Build an interactive business-style dashboard
- Deploy the application on Streamlit Cloud

---

## Model Architecture

The forecasting engine is built using an **amalgamated ensemble regression approach** that combines multiple tree-based models to improve generalization and robustness.

### Models Used

#### XGBoost Regressor
- Captures complex non-linear feature interactions
- Performs exceptionally well on structured tabular data
- Includes regularization to prevent overfitting

#### Random Forest Regressor
- Uses bagging to reduce variance
- Produces stable baseline predictions
- Handles noisy retail data effectively

#### Gradient Boosting Regressor
- Learns from residual errors iteratively
- Improves accuracy over sequential stages
- Captures subtle demand trends

---

### Ensemble Strategy

Predictions from all models are combined using **averaging (voting regression)**.

Benefits:
- Reduced bias and variance
- Improved prediction stability
- Robust performance across scenarios

This approach mirrors industry-grade forecasting pipelines used in retail analytics.

---

## Dataset and Features

### Input Features

| Feature | Description |
|------|------------|
| Store | Store identifier |
| Date | Weekly timestamp |
| Holiday_Flag | Indicates holiday week |
| Temperature | Average weekly temperature (°F) |
| Fuel_Price | Fuel cost per gallon |
| CPI | Consumer Price Index |
| Unemployment | National unemployment rate |

---

## Feature Engineering

### Temperature Effect Modeling

Temperature impact is modeled using a **parabolic (quadratic) function**:

- Sales peak at an optimal temperature (~70°F)
- Extremely low or high temperatures reduce demand
- Reflects realistic consumer behavior

This improves realism over linear assumptions.

---

## Streamlit Dashboard Components

### KPI Cards
- Predicted Weekly Sales
- Average Store Sales
- Percentage Change vs Historical Average

---

### Recent Sales Trend
- Displays last 20 weeks of actual sales
- Overlays predicted sales
- Validates model behavior visually

---

### Sensitivity Analysis

Interactive sensitivity plots for:
- Temperature
- Fuel Price
- CPI
- Unemployment Rate

Each plot:
- Shows smooth response curves
- Highlights the current operating point
- Enables what-if analysis for decision making

---

## UI & Visualization Design

- Compatible with light and dark modes
- Business-dashboard style layout
- High-contrast plots for readability
- Minimal visual clutter
- Deployment-stable plotting approach

---

## Deployment

- Framework: Streamlit
- Hosting: Streamlit Cloud
- Secrets Management: Streamlit Secrets (CSV stored securely)
- Version Control: GitHub
- Python Version: 3.13

---



