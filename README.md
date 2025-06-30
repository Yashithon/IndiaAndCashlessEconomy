# India and the Rise of Cashless Economy-AI-powered Analysing(2016-2025) and Forecasting of Digital Payments Using Time Series Modeling(2016-2035)

This project presents a data-driven dashboard that analyzes and forecasts the evolution of India’s digital payment platforms — UPI, IMPS, and FASTag — from 2016 to 2025, with projections up to 2035. It uses actual transaction data collected from NPCI and applies machine learning-based time series forecasting using Facebook Prophet. The visual interface is built using Streamlit.

## Project Objectives

- Analyze real transaction data from 2016–2025
- Forecast digital payment trends up to 2035
- Visualize patterns and growth across UPI, IMPS, and FASTag
- Provide insights into India’s shift toward a cashless economy

## Technologies Used

- **pandas**: Data cleaning, aggregation, pivoting
- **numpy**: Growth calculations and numerical processing
- **plotly**: Interactive line and area charts
- **prophet**: Forecasting model for time series data
- **streamlit**: Frontend UI and interactive dashboard

## What Is Prophet?

Prophet is an open-source machine learning model developed by Facebook specifically for time series forecasting. It:
- Detects and models growth trends and seasonality
- Handles missing data and outliers well
- Provides confidence intervals on predictions
- Can identify trend change points automatically

### Key Equations Behind Prophet

Prophet decomposes a time series into:
y(t) = g(t) + s(t) + ε(t)

markdown
Copy
Edit
Where:
- `g(t)`: Trend function (linear or logistic)
- `s(t)`: Seasonality (modeled using Fourier series)
- `ε(t)`: Random noise (assumed normally distributed)

## Features

### 1. Combined Overview

- Visualizes UPI, IMPS, and FASTag growth from 2016 to 2025
- Layered area plots with line graphs for better understanding
- Color-coded and styled for clarity

### 2. Category-Wise Drilldown

- Select payment type (e.g., UPI) and year
- View monthly transaction trends
- See peak, lowest, and year-over-year growth stats

### 3. AI Forecasting (2025–2035)

- Ten-year prediction for combined and individual platforms
- Confidence interval shown as shaded regions
- Based on learned historical patterns

## Usage

### Run Locally

Clone the repository and run the app with Streamlit:

```bas
Data Source
NPCI Product Statistics (https://www.npci.org.in/statistics)

All data was manually compiled into a structured Excel file for analysis.

Results
UPI shows exponential growth post-2019

IMPS demonstrates steady, reliable expansion

FASTag adoption increased rapidly post-2020

Forecasts suggest continued digital acceleration through 2035

Limitations
Forecasting assumes no economic or policy disruptions

External factors (like GDP, literacy, internet penetration) are not modeled

Limited to three payment platforms

Possible Improvements
Add other digital channels (AePS, BBPS, NACH)

Incorporate external regressors (economic indicators)

Extend dashboard with state-wise breakdown (if data available)

Author
Yashashvi Bagdwal
Email: yashashvibagdwal@gmail.com
This project is intended for educational purposes and demonstrates how machine learning and visualization can be combined to explore national-scale fintech data trends.


