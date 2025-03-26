import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

def plot_temperature_chart(df):
    """Create a temperature anomaly chart"""
    fig = px.line(
        df,
        x="Year",
        y="Temperature_Anomaly",
        title="Global Temperature Anomaly (°C relative to 1951-1980 average)",
        labels={"Temperature_Anomaly": "Temperature Anomaly (°C)"}
    )
    
    # Add a zero line for reference
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    
    # Add a trend line
    fig.add_traces(
        px.scatter(
            df, x="Year", y="Temperature_Anomaly", trendline="ols"
        ).data[1]
    )
    
    # Customize appearance
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Temperature Anomaly (°C)",
        hovermode="x unified",
        legend_title="",
        font=dict(family="Arial", size=12),
    )
    
    # Color based on values (blue for negative, red for positive)
    fig.update_traces(
        line=dict(color="#FF5252", width=2),
    )
    
    return fig

def plot_co2_chart(df):
    """Create a CO2 concentration chart"""
    fig = px.line(
        df,
        x="Year",
        y="CO2_Concentration",
        title="Atmospheric CO₂ Concentration (ppm)",
        labels={"CO2_Concentration": "CO₂ (ppm)"}
    )
    
    # Add a reference line for pre-industrial levels
    fig.add_hline(y=280, line_dash="dash", line_color="green", annotation_text="Pre-industrial level (280 ppm)")
    
    # Add a reference line for 350 ppm (often considered a "safe" target)
    fig.add_hline(y=350, line_dash="dash", line_color="orange", annotation_text="350 ppm threshold")
    
    # Customize appearance
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="CO₂ Concentration (ppm)",
        hovermode="x unified",
        legend_title="",
        font=dict(family="Arial", size=12),
    )
    
    fig.update_traces(
        line=dict(color="#FF9800", width=2),
    )
    
    return fig

def plot_sea_level_chart(df):
    """Create a sea level rise chart"""
    fig = px.line(
        df,
        x="Year",
        y="Sea_Level_Rise",
        title="Global Mean Sea Level Rise (mm since 1900)",
        labels={"Sea_Level_Rise": "Sea Level Rise (mm)"}
    )
    
    # Add a trend line
    fig.add_traces(
        px.scatter(
            df, x="Year", y="Sea_Level_Rise", trendline="ols"
        ).data[1]
    )
    
    # Customize appearance
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Sea Level Rise (mm)",
        hovermode="x unified",
        legend_title="",
        font=dict(family="Arial", size=12),
    )
    
    fig.update_traces(
        line=dict(color="#2196F3", width=2),
    )
    
    return fig

def plot_extreme_events_chart(df):
    """Create a chart of extreme weather events over time"""
    # Convert to long format for Plotly
    df_long = pd.melt(
        df,
        id_vars=['Year'],
        value_vars=['Floods', 'Droughts', 'Storms', 'Wildfires'],
        var_name='Event Type',
        value_name='Count'
    )
    
    fig = px.line(
        df_long,
        x="Year",
        y="Count",
        color="Event Type",
        title="Extreme Weather Events Over Time",
        labels={"Count": "Number of Events"}
    )
    
    # Customize appearance
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Number of Events",
        hovermode="x unified",
        legend_title="Event Type",
        font=dict(family="Arial", size=12),
    )
    
    # Custom colors for each event type
    colors = {"Floods": "#2196F3", "Droughts": "#FF9800", "Storms": "#9C27B0", "Wildfires": "#F44336"}
    
    for trace, event_type in zip(fig.data, ["Floods", "Droughts", "Storms", "Wildfires"]):
        trace.line.color = colors.get(event_type, "#000000")
        trace.line.width = 2
    
    return fig

def plot_air_quality_chart(df, location="Global"):
    """Create an air quality chart for a location"""
    fig = px.line(
        df,
        x="Year",
        y="PM2.5",
        title=f"Annual Average PM2.5 Concentration for {location}",
        labels={"PM2.5": "PM2.5 (μg/m³)"}
    )
    
    # Add WHO air quality guideline line
    fig.add_hline(y=5, line_dash="dash", line_color="green", annotation_text="WHO guideline (5 μg/m³)")
    
    # Add unhealthy threshold
    fig.add_hline(y=35, line_dash="dash", line_color="red", annotation_text="Unhealthy level (35 μg/m³)")
    
    # Customize appearance
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="PM2.5 Concentration (μg/m³)",
        hovermode="x unified",
        legend_title="",
        font=dict(family="Arial", size=12),
    )
    
    # Color based on air quality
    if df["PM2.5"].mean() > 25:
        line_color = "#F44336"  # Red for poor air quality
    elif df["PM2.5"].mean() > 10:
        line_color = "#FF9800"  # Orange for moderate air quality
    else:
        line_color = "#4CAF50"  # Green for good air quality
    
    fig.update_traces(
        line=dict(color=line_color, width=2),
    )
    
    return fig

def create_climate_risk_heatmap(location="Global"):
    """Create a climate risk heatmap for a location"""
    # These would be calculated from real data in a production app
    risks = {
        "Floods": random.uniform(0.1, 0.9),
        "Droughts": random.uniform(0.1, 0.9),
        "Heatwaves": random.uniform(0.1, 0.9),
        "Storms": random.uniform(0.1, 0.9),
        "Sea Level Rise": random.uniform(0.1, 0.9),
        "Water Scarcity": random.uniform(0.1, 0.9),
        "Agriculture Impact": random.uniform(0.1, 0.9),
        "Biodiversity Loss": random.uniform(0.1, 0.9),
    }
    
    # Sort risks by value
    sorted_risks = {k: v for k, v in sorted(risks.items(), key=lambda item: item[1], reverse=True)}
    
    # Create figure
    fig = go.Figure()
    
    # Add bar chart
    fig.add_trace(go.Bar(
        x=list(sorted_risks.values()),
        y=list(sorted_risks.keys()),
        orientation='h',
        marker=dict(
            color=[
                f'rgba({int(255*v)}, {int(255*(1-v))}, 0, 0.8)' 
                for v in sorted_risks.values()
            ],
            line=dict(width=0)
        )
    ))
    
    # Update layout
    fig.update_layout(
        title=f"Climate Risk Assessment for {location}",
        xaxis_title="Risk Level (0-1)",
        yaxis_title="Risk Category",
        height=500,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    
    # Add risk level indicators
    fig.add_shape(type="line", x0=0.25, y0=-0.5, x1=0.25, y1=len(risks)-0.5, 
                 line=dict(color="green", width=1, dash="dash"))
    fig.add_shape(type="line", x0=0.5, y0=-0.5, x1=0.5, y1=len(risks)-0.5, 
                 line=dict(color="orange", width=1, dash="dash"))
    fig.add_shape(type="line", x0=0.75, y0=-0.5, x1=0.75, y1=len(risks)-0.5, 
                 line=dict(color="red", width=1, dash="dash"))
    
    fig.add_annotation(x=0.25, y=len(risks), text="Low", showarrow=False, yshift=10)
    fig.add_annotation(x=0.5, y=len(risks), text="Medium", showarrow=False, yshift=10)
    fig.add_annotation(x=0.75, y=len(risks), text="High", showarrow=False, yshift=10)
    
    return fig
