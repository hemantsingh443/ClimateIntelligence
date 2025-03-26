import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
from api_integrations import WorldBankAPI, NOAAAPI, OpenWeatherAPI
from utils import get_climate_indicators, noaa_api, world_bank_api

def plot_temperature_chart(df):
    """Create a temperature anomaly chart using real-time data"""
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
    """Create a CO2 concentration chart using real-time data"""
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
    """Create a sea level rise chart using real-time data"""
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
    """Create a chart of extreme weather events over time using real-time data"""
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
    """Create an air quality chart for a location using real-time data"""
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

def create_temperature_chart():
    """Create a chart showing temperature trends"""
    try:
        # Get historical temperature data from World Bank
        temp_data = world_bank_api.get_climate_indicators()
        if not temp_data or 'Forest area' not in temp_data:
            st.error("Unable to fetch temperature data")
            return None
            
        # Process the data
        data = temp_data['Forest area']
        if len(data) < 2 or not isinstance(data[1], list):
            st.error("Invalid temperature data format")
            return None
            
        # Create dataframe
        df = pd.DataFrame(data[1])
        df['date'] = pd.to_datetime(df['date'])
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        
        # Create the chart
        fig = px.line(df, x='date', y='value', 
                     title='Global Temperature Anomaly',
                     labels={'value': 'Temperature Anomaly (°C)',
                            'date': 'Year'})
        return fig
    except Exception as e:
        st.error(f"Error creating temperature chart: {str(e)}")
        return None

def create_co2_chart():
    """Create a chart showing CO2 concentration trends"""
    try:
        # Get CO2 data from World Bank
        co2_data = world_bank_api.get_climate_indicators()
        if not co2_data or 'CO2 emissions' not in co2_data:
            st.error("Unable to fetch CO2 data")
            return None
            
        # Process the data
        data = co2_data['CO2 emissions']
        if len(data) < 2 or not isinstance(data[1], list):
            st.error("Invalid CO2 data format")
            return None
            
        # Create dataframe
        df = pd.DataFrame(data[1])
        df['date'] = pd.to_datetime(df['date'])
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        
        # Create the chart
        fig = px.line(df, x='date', y='value',
                     title='CO2 Emissions',
                     labels={'value': 'CO2 (metric tons per capita)',
                            'date': 'Year'})
        return fig
    except Exception as e:
        st.error(f"Error creating CO2 chart: {str(e)}")
        return None

def create_sea_level_chart(lat=51.5074, lon=-0.1278):
    """Create a chart showing sea level trends"""
    try:
        # Get sea level data from NOAA
        noaa_data = noaa_api.get_climate_data(lat, lon)
        if not isinstance(noaa_data, dict) or 'properties' not in noaa_data:
            st.error("Unable to fetch sea level data")
            return None
            
        properties = noaa_data['properties']
        if 'error' in properties:
            st.warning(f"NOAA data not available: {properties['error']}")
            return None
            
        if 'data' not in properties or not isinstance(properties['data'], dict):
            st.error("Invalid sea level data format")
            return None
            
        data = properties['data'].get('results', [])
        if not data:
            st.error("No sea level data available")
            return None
            
        # Create dataframe
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        
        # Create the chart
        fig = px.line(df, x='date', y='value',
                     title='Sea Level Change',
                     labels={'value': 'Sea Level (mm)',
                            'date': 'Date'})
        return fig
    except Exception as e:
        st.error(f"Error creating sea level chart: {str(e)}")
        return None

def create_climate_risk_heatmap(location_data):
    """Create a heatmap showing climate risk factors"""
    try:
        # Get current climate indicators with default values
        temp, co2, sea_level = get_climate_indicators()
        
        # Get current weather data for additional context
        weather_data = None
        if isinstance(location_data, dict):
            weather_data = location_data.get('weather', {})
        else:
            location_data = {}
            
        # Define risk factors and their weights with validation
        risk_factors = {
            'Temperature': {
                'value': float(temp) if isinstance(temp, (int, float)) else 0,
                'weight': 0.25
            },
            'CO2 Levels': {
                'value': float(co2) if isinstance(co2, (int, float)) else 0,
                'weight': 0.25
            },
            'Sea Level': {
                'value': float(sea_level) if isinstance(sea_level, (int, float)) else 0,
                'weight': 0.25
            },
            'Climate Vulnerability': {
                'value': calculate_vulnerability_score(weather_data, location_data),
                'weight': 0.25
            }
        }
        
        # Calculate normalized risk scores (0-1 scale) with validation
        max_values = {
            'Temperature': 2.0,  # 2°C above pre-industrial levels
            'CO2 Levels': 450.0,  # ppm (parts per million)
            'Sea Level': 200.0,  # mm rise
            'Climate Vulnerability': 10.0  # vulnerability score
        }
        
        risk_scores = {}
        for factor, data in risk_factors.items():
            try:
                if factor == 'Climate Vulnerability':
                    # Vulnerability score is already normalized
                    risk_scores[factor] = data['value'] * data['weight']
                else:
                    normalized_value = min(max(data['value'] / max_values[factor], 0), 1.0)
                    risk_scores[factor] = normalized_value * data['weight']
            except (ZeroDivisionError, TypeError):
                risk_scores[factor] = 0
                st.warning(f"Could not calculate risk score for {factor}")
        
        # Create the heatmap data
        factors = list(risk_scores.keys())
        values = [[score] for score in risk_scores.values()]
        
        if not factors or not values:
            st.error("No valid risk factors to display")
            return None
        
        # Create the heatmap
        fig = go.Figure(data=go.Heatmap(
            z=values,
            y=factors,
            x=['Risk Score'],
            colorscale='RdYlGn_r',
            showscale=True,
            zmin=0,  # Set minimum value
            zmax=1   # Set maximum value
        ))
        
        # Add risk level annotations
        risk_levels = []
        total_risk = sum(risk_scores.values())
        
        if total_risk < 0.3:
            risk_level = "Low Risk"
            color = "green"
        elif total_risk < 0.6:
            risk_level = "Moderate Risk"
            color = "orange"
        else:
            risk_level = "High Risk"
            color = "red"
            
        fig.add_annotation(
            x=1.2,
            y=len(factors)/2,
            text=f"Overall: {risk_level}",
            showarrow=False,
            font=dict(size=14, color=color)
        )
        
        fig.update_layout(
            title='Climate Risk Assessment',
            yaxis_title='Risk Factors',
            xaxis_title='Risk Level',
            height=400,
            margin=dict(r=150)  # Make room for the overall risk label
        )
        
        return fig
    except Exception as e:
        st.error(f"Error creating climate risk heatmap: {str(e)}")
        return None

def calculate_vulnerability_score(weather_data, location_data):
    """Calculate a climate vulnerability score based on available data"""
    try:
        score = 5.0  # Start with a middle score
        
        if isinstance(weather_data, dict):
            # Temperature vulnerability
            if 'main' in weather_data:
                temp = weather_data['main'].get('temp', 0)
                if temp > 35:  # Very hot
                    score += 2
                elif temp < 0:  # Very cold
                    score += 1
                    
                humidity = weather_data['main'].get('humidity', 0)
                if humidity > 80:  # High humidity
                    score += 1
                elif humidity < 30:  # Very dry
                    score += 1
        
        # Location-based factors
        if isinstance(location_data, dict):
            # Coastal proximity
            if location_data.get('is_coastal', False):
                score += 1
                
            # Urban heat island effect
            if location_data.get('is_urban', False):
                score += 0.5
                
            # Historical extreme events
            extreme_events = location_data.get('extreme_events', 0)
            if extreme_events > 5:
                score += 1
        
        # Normalize score to 0-1 range
        return min(max(score / 10.0, 0), 1.0)
        
    except Exception as e:
        st.warning(f"Error calculating vulnerability score: {str(e)}")
        return 0.5  # Return middle score if calculation fails
