import streamlit as st
import pandas as pd
from prophet import Prophet
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

@st.cache_data
def load_data():
    df = pd.read_excel("final_cashless_payments_inr.xlsx")
    df['Date'] = pd.to_datetime(df['Date'])
    df = df[df['Platform'].isin(['UPI', 'IMPS', 'NETC'])]
    df['Platform'] = df['Platform'].replace({'NETC': 'FASTag'})
    monthly = df.groupby(['Date', 'Platform'])['Amount_INR'].sum().reset_index()
    pivot_df = monthly.pivot(index='Date', columns='Platform', values='Amount_INR').fillna(0)
    pivot_df['Combined'] = pivot_df.sum(axis=1)
    return pivot_df

def forecast_data(df, category):
    df = df[[category]].reset_index().rename(columns={'Date': 'ds', category: 'y'})
    model = Prophet(yearly_seasonality=True)
    model.fit(df)
    future = model.make_future_dataframe(periods=120, freq='M')
    forecast = model.predict(future)
    return forecast

def get_insights(series):
    max_val = series.max()
    min_val = series.min()
    pct_growth = ((series[-1] - series[0]) / series[0]) * 100
    return max_val, min_val, pct_growth

def format_currency(value):
    """Format large numbers in INR with appropriate suffixes"""
    if value >= 1e12:
        return f"₹{value/1e12:.2f}T"
    elif value >= 1e9:
        return f"₹{value/1e9:.2f}B"
    elif value >= 1e7:
        return f"₹{value/1e7:.2f}Cr"
    elif value >= 1e5:
        return f"₹{value/1e5:.2f}L"
    else:
        return f"₹{value:,.0f}"

# Updated Color Scheme - Yellow, Yellow-Green, Dark Green
COLORS = {
    'UPI': {
        'primary': '#FFD700',      # Bright yellow
        'secondary': '#FFC107',    # Amber yellow
        'light': '#FFEB3B',       # Light yellow
        'gradient': 'rgba(255, 215, 0, 0.3)',
    },
    'IMPS': {
        'primary': '#9ACD32',      # Yellow green
        'secondary': '#ADFF2F',    # Green yellow
        'light': '#CDDC39',       # Lime
        'gradient': 'rgba(154, 205, 50, 0.3)',
    },
    'FASTag': {
        'primary': '#006400',      # Dark green
        'secondary': '#228B22',    # Forest green
        'light': '#32CD32',       # Lime green
        'gradient': 'rgba(0, 100, 0, 0.3)',
    },
    'Combined': {
        'primary': '#2d2d5a',      # Deep purple
        'secondary': '#4a4a8a',    # Medium purple
        'light': '#6b6bb7',       # Light purple
        'gradient': 'rgba(45, 45, 90, 0.3)',
    }
}

# Load data
df = load_data()

st.title("Cashless Economy in India (2016–2035)")
st.markdown("*Tracking the digital transformation of India's payment ecosystem*")

view_mode = st.radio("Choose Mode", ["Combined Overview", "Category-wise Analysis & Forecast"])

if view_mode == "Combined Overview":
    st.subheader("Growth of UPI + IMPS + FASTag (2016–2025)")
    
    # Clean line chart without circular markers
    fig = go.Figure()
    
    platforms = ['UPI', 'IMPS', 'FASTag']
    line_styles = ['solid', 'dash', 'dot']
    
    for i, platform in enumerate(platforms):
        colors = COLORS[platform]
        
        # Add gradient fill
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df[platform],
            fill='tozeroy',
            fillcolor=colors['gradient'],
            mode='none',
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # Add clean line without markers
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df[platform],
            mode='lines',
            name=platform,
            line=dict(
                color=colors['primary'], 
                width=5, 
                dash=line_styles[i]
            ),
            hovertemplate=f'<b>{platform}</b><br>' +
                         'Date: %{x}<br>' +
                         'Value: %{customdata}<br>' +
                         '<extra></extra>',
            customdata=[format_currency(val) for val in df[platform]]
        ))
    
    fig.update_layout(
        title={
            'text': "Digital Payment Platforms Growth Over Time",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#1a1a1a', 'family': 'Arial Black'}
        },
        xaxis_title="Timeline",
        yaxis_title="Transaction Volume (INR)",
        template="plotly_white",
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=12, color='#2d2d2d')
        ),
        margin=dict(t=100, b=60, l=80, r=80),
        height=550,
        plot_bgcolor='rgba(248, 249, 250, 0.8)',
        paper_bgcolor='white'
    )
    
    # Enhanced axis styling
    fig.update_yaxes(
        tickformat=',.0s',
        ticksuffix='',
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(200, 200, 200, 0.3)',
        tickfont=dict(color='#4a4a4a')
    )
    
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(200, 200, 200, 0.3)',
        tickfont=dict(color='#4a4a4a')
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("#### How to Read the Graph:")
    st.write("This visualization shows the monthly transaction volumes for each digital payment platform:")
    st.write("- **UPI (Bright Yellow)**: Unified Payments Interface showing explosive growth post-2019")
    st.write("- **IMPS (Yellow-Green)**: Immediate Payment Service with steady growth")
    st.write("- **FASTag (Dark Green)**: Electronic toll collection system growth")
    st.write("- **Gradient fills** highlight individual platform contributions")
    st.write("- **Line patterns** (solid, dashed, dotted) provide visual distinction")
    
    st.subheader("Combined Forecast (2025–2035)")
    forecast = forecast_data(df, 'Combined')
    
    # Enhanced forecast chart with clean lines
    fig2 = go.Figure()
    
    combined_colors = COLORS['Combined']
    
    # Historical data - clean line
    historical_mask = forecast['ds'] <= df.index.max()
    fig2.add_trace(go.Scatter(
        x=forecast[historical_mask]['ds'],
        y=forecast[historical_mask]['yhat'],
        mode='lines',
        name='Historical Trend',
        line=dict(color=combined_colors['primary'], width=5),
        hovertemplate='Historical<br>Date: %{x}<br>Value: %{customdata}<extra></extra>',
        customdata=[format_currency(val) for val in forecast[historical_mask]['yhat']]
    ))
    
    # Forecast data - clean dashed line
    future_mask = forecast['ds'] > df.index.max()
    fig2.add_trace(go.Scatter(
        x=forecast[future_mask]['ds'],
        y=forecast[future_mask]['yhat'],
        mode='lines',
        name='Forecast',
        line=dict(color=combined_colors['light'], width=5, dash='dash'),
        hovertemplate='Forecast<br>Date: %{x}<br>Value: %{customdata}<extra></extra>',
        customdata=[format_currency(val) for val in forecast[future_mask]['yhat']]
    ))
    
    # Enhanced confidence intervals
    fig2.add_trace(go.Scatter(
        x=forecast[future_mask]['ds'],
        y=forecast[future_mask]['yhat_upper'],
        fill=None,
        mode='lines',
        line_color='rgba(0,0,0,0)',
        showlegend=False
    ))
    
    fig2.add_trace(go.Scatter(
        x=forecast[future_mask]['ds'],
        y=forecast[future_mask]['yhat_lower'],
        fill='tonexty',
        mode='lines',
        line_color='rgba(0,0,0,0)',
        name='Confidence Interval',
        fillcolor=combined_colors['gradient']
    ))
    
    fig2.update_layout(
        title={
            'text': "Total Digital Payments Forecast: Path to 2035",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#1a1a1a', 'family': 'Arial Black'}
        },
        xaxis_title="Timeline",
        yaxis_title="Predicted Transaction Volume (INR)",
        template="plotly_white",
        hovermode='x unified',
        height=550,
        plot_bgcolor='rgba(248, 249, 250, 0.8)',
        paper_bgcolor='white',
        margin=dict(t=100, b=60, l=80, r=80),
        legend=dict(
            font=dict(size=12, color='#2d2d2d')
        ),
        annotations=[
            dict(
                x=forecast[future_mask]['ds'].iloc[0],
                y=max(forecast['yhat']) * 0.8,
                text="Forecast Period",
                showarrow=True,
                arrowhead=2,
                arrowcolor=combined_colors['primary'],
                bgcolor=combined_colors['gradient'],
                bordercolor=combined_colors['primary'],
                font=dict(color=combined_colors['primary'])
            )
        ]
    )
    
    fig2.update_yaxes(
        tickformat=',.0s',
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(200, 200, 200, 0.3)',
        tickfont=dict(color='#4a4a4a')
    )
    
    fig2.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(200, 200, 200, 0.3)',
        tickfont=dict(color='#4a4a4a')
    )
    
    st.plotly_chart(fig2, use_container_width=True)

elif view_mode == "Category-wise Analysis & Forecast":
    category = st.selectbox("Select Payment Type", ['UPI', 'IMPS', 'FASTag'])
    year = st.selectbox("Select Year", sorted(df.index.year.unique()))
    
    # Platform descriptions without icons
    platform_info = {
        'UPI': 'Unified Payments Interface - Real-time mobile payments',
        'IMPS': 'Immediate Payment Service - Instant bank transfers',
        'FASTag': 'Electronic Toll Collection - Highway payment system'
    }
    
    st.markdown(f"## {category} Analysis")
    st.markdown(f"*{platform_info[category]}*")
    
    # Get colors for selected category
    colors = COLORS[category]
    
    # Monthly view with clean styling
    monthly_data = df[df.index.year == year]
    
    fig = go.Figure()
    
    # Add area fill for visual appeal
    fig.add_trace(go.Scatter(
        x=monthly_data.index,
        y=monthly_data[category],
        fill='tozeroy',
        fillcolor=colors['gradient'],
        mode='none',
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Add clean line without markers
    fig.add_trace(go.Scatter(
        x=monthly_data.index,
        y=monthly_data[category],
        mode='lines',
        name=f'{category} Usage',
        line=dict(color=colors['primary'], width=5),
        hovertemplate=f'<b>{category} in {year}</b><br>' +
                     'Month: %{x|%B %Y}<br>' +
                     'Value: %{customdata}<br>' +
                     '<extra></extra>',
        customdata=[format_currency(val) for val in monthly_data[category]]
    ))
    
    fig.update_layout(
        title={
            'text': f"{category} Monthly Performance in {year}",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#1a1a1a', 'family': 'Arial Black'}
        },
        xaxis_title="Month",
        yaxis_title="Transaction Volume (INR)",
        template="plotly_white",
        height=500,
        showlegend=False,
        plot_bgcolor='rgba(248, 249, 250, 0.8)',
        paper_bgcolor='white',
        margin=dict(t=100, b=60, l=80, r=80)
    )
    
    fig.update_yaxes(
        tickformat=',.0s',
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(200, 200, 200, 0.3)',
        tickfont=dict(color='#4a4a4a')
    )
    
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(200, 200, 200, 0.3)',
        tickfont=dict(color='#4a4a4a')
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("#### Key Insights for Selected Year:")
    max_val, min_val, pct = get_insights(monthly_data[category])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Peak Value", format_currency(max_val), "Highest monthly volume")
    with col2:
        st.metric("Lowest Value", format_currency(min_val), "Minimum monthly volume")
    with col3:
        st.metric("Annual Growth", f"{pct:.2f}%", "Year-over-year change")
    
    # Full trend forecast
    st.subheader(f"{category} Forecast (2025–2035)")
    forecast = forecast_data(df, category)
    
    # Enhanced forecast visualization with clean lines
    fig2 = go.Figure()
    
    # Historical data - clean line
    historical_mask = forecast['ds'] <= df.index.max()
    fig2.add_trace(go.Scatter(
        x=forecast[historical_mask]['ds'],
        y=forecast[historical_mask]['yhat'],
        mode='lines',
        name='Historical Data',
        line=dict(color=colors['primary'], width=5),
        hovertemplate='Historical<br>Date: %{x}<br>Value: %{customdata}<extra></extra>',
        customdata=[format_currency(val) for val in forecast[historical_mask]['yhat']]
    ))
    
    # Forecast data - clean dashed line
    future_mask = forecast['ds'] > df.index.max()
    fig2.add_trace(go.Scatter(
        x=forecast[future_mask]['ds'],
        y=forecast[future_mask]['yhat'],
        mode='lines',
        name='Projected Growth',
        line=dict(color=colors['light'], width=5, dash='dash'),
        hovertemplate='Forecast<br>Date: %{x}<br>Value: %{customdata}<extra></extra>',
        customdata=[format_currency(val) for val in forecast[future_mask]['yhat']]
    ))
    
    # Enhanced confidence bands
    fig2.add_trace(go.Scatter(
        x=forecast[future_mask]['ds'],
        y=forecast[future_mask]['yhat_upper'],
        fill=None,
        mode='lines',
        line_color='rgba(0,0,0,0)',
        showlegend=False
    ))
    
    fig2.add_trace(go.Scatter(
        x=forecast[future_mask]['ds'],
        y=forecast[future_mask]['yhat_lower'],
        fill='tonexty',
        mode='lines',
        line_color='rgba(0,0,0,0)',
        name='Prediction Range',
        fillcolor=colors['gradient']
    ))
    
    fig2.update_layout(
        title={
            'text': f"{category} Future Trajectory: Growth Projection to 2035",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#1a1a1a', 'family': 'Arial Black'}
        },
        xaxis_title="Timeline",
        yaxis_title="Predicted Transaction Volume (INR)",
        template="plotly_white",
        hovermode='x unified',
        height=550,
        plot_bgcolor='rgba(248, 249, 250, 0.8)',
        paper_bgcolor='white',
        margin=dict(t=100, b=60, l=80, r=80),
        legend=dict(
            font=dict(size=12, color='#2d2d2d')
        )
    )
    
    fig2.update_yaxes(
        tickformat=',.0s',
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(200, 200, 200, 0.3)',
        tickfont=dict(color='#4a4a4a')
    )
    
    fig2.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(200, 200, 200, 0.3)',
        tickfont=dict(color='#4a4a4a')
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("#### Understanding the Forecast:")
    st.write("- **Solid line**: Historical performance showing actual growth patterns")
    st.write("- **Dashed line**: AI-powered predictions based on historical trends and seasonality")
    st.write("- **Shaded area**: Confidence interval indicating the range of possible outcomes")
    st.write("- **Upward trajectory**: Indicates projected continued growth in digital adoption")
    
    # Additional insights box
    with st.expander("Insights"):
        st.write(f"""
        **Prophet Forecasting Model Analysis for {category}:**
        - The model considers yearly seasonality patterns in payment behavior
        - Predictions account for historical growth trends and seasonal variations
        - Confidence intervals reflect uncertainty that increases over time
        - The forecast assumes continued digital adoption without major disruptions
        """)

st.markdown("---")
st.markdown("This is a personal project made for basic educational purposes.For an queries please contact yashashvibagdwal@gmail.com ")
