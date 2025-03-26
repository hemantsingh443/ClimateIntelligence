import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from utils import get_climate_indicators, noaa_api, world_bank_api

def analyze_temperature_trends():
    """Analyze and visualize temperature trends"""
    try:
        # Get historical temperature data
        temp_data = world_bank_api.get_climate_indicators()
        if not temp_data or 'Forest area' not in temp_data:
            st.error("Unable to fetch temperature data for trend analysis")
            return None, None
            
        # Process the data
        data = temp_data['Forest area']
        if not data or len(data) < 2 or not isinstance(data[1], list) or not data[1]:
            st.error("Invalid or empty temperature data format")
            return None, None
            
        # Create dataframe
        df = pd.DataFrame(data[1])
        
        # Check if required columns exist
        if 'date' not in df.columns or 'value' not in df.columns:
            st.error("Missing required columns in temperature data")
            return None, None
            
        # Convert and clean data
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        
        # Drop any rows with NaN values
        df = df.dropna(subset=['date', 'value'])
        
        # Sort by date
        df = df.sort_values('date')
        
        # Check if we have enough data points after cleaning
        if len(df) < 2:
            st.error("Insufficient valid data points for trend analysis")
            return None, None
            
        # Calculate trends
        total_change = df['value'].iloc[-1] - df['value'].iloc[0]
        avg_change = total_change / (len(df) - 1)
        
        # Create trend visualization
        fig = px.line(df, x='date', y='value',
                     title='Temperature Trend Analysis',
                     labels={'value': 'Temperature Anomaly (°C)',
                            'date': 'Year'})
        
        # Add trend line (only if we have enough data points)
        if len(df) >= 5:
            fig.add_scatter(x=df['date'], 
                          y=df['value'].rolling(window=min(5, len(df))).mean(),
                          name='5-Year Moving Average',
                          line=dict(color='red', dash='dash'))
        
        return fig, {
            'total_change': total_change,
            'avg_annual_change': avg_change,
            'current_value': df['value'].iloc[-1],
            'start_year': df['date'].iloc[0].year,
            'end_year': df['date'].iloc[-1].year
        }
    except Exception as e:
        st.error(f"Error analyzing temperature trends: {str(e)}")
        return None, None

def analyze_co2_trends():
    """Analyze and visualize CO2 emission trends"""
    try:
        # Get CO2 data
        co2_data = world_bank_api.get_climate_indicators()
        if not co2_data or 'CO2 emissions' not in co2_data:
            st.error("Unable to fetch CO2 data for trend analysis")
            return None, None
            
        # Process the data
        data = co2_data['CO2 emissions']
        if len(data) < 2 or not isinstance(data[1], list):
            st.error("Invalid CO2 data format for trend analysis")
            return None, None
            
        # Create dataframe
        df = pd.DataFrame(data[1])
        df['date'] = pd.to_datetime(df['date'])
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        
        # Calculate trends
        if len(df) >= 2:
            total_change = df['value'].iloc[-1] - df['value'].iloc[0]
            avg_change = total_change / (len(df) - 1)
            
            # Create trend visualization
            fig = px.line(df, x='date', y='value',
                         title='CO2 Emissions Trend Analysis',
                         labels={'value': 'CO2 (metric tons per capita)',
                                'date': 'Year'})
            
            # Add trend line
            fig.add_scatter(x=df['date'], 
                          y=df['value'].rolling(window=5).mean(),
                          name='5-Year Moving Average',
                          line=dict(color='red', dash='dash'))
            
            return fig, {
                'total_change': total_change,
                'avg_annual_change': avg_change,
                'current_value': df['value'].iloc[-1],
                'start_year': df['date'].iloc[0].year,
                'end_year': df['date'].iloc[-1].year
            }
        else:
            st.error("Insufficient data points for trend analysis")
            return None, None
    except Exception as e:
        st.error(f"Error analyzing CO2 trends: {str(e)}")
        return None, None

def analyze_sea_level_trends(lat=51.5074, lon=-0.1278):
    """Analyze and visualize sea level trends"""
    try:
        # Get sea level data
        noaa_data = noaa_api.get_climate_data(lat, lon)
        if not isinstance(noaa_data, dict) or 'properties' not in noaa_data:
            st.error("Unable to fetch sea level data for trend analysis")
            return None, None
            
        properties = noaa_data['properties']
        if 'error' in properties:
            st.warning(f"NOAA data not available: {properties['error']}")
            return None, None
            
        if 'data' not in properties or not isinstance(properties['data'], dict):
            st.error("Invalid sea level data format for trend analysis")
            return None, None
            
        data = properties['data'].get('results', [])
        if not data:
            st.error("No sea level data available for trend analysis")
            return None, None
            
        # Create dataframe
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        
        # Calculate trends
        if len(df) >= 2:
            total_change = df['value'].iloc[-1] - df['value'].iloc[0]
            time_diff = (df['date'].iloc[-1] - df['date'].iloc[0]).days / 365.25
            avg_change = total_change / time_diff if time_diff > 0 else 0
            
            # Create trend visualization
            fig = px.line(df, x='date', y='value',
                         title='Sea Level Trend Analysis',
                         labels={'value': 'Sea Level (mm)',
                                'date': 'Date'})
            
            # Add trend line
            fig.add_scatter(x=df['date'], 
                          y=df['value'].rolling(window=12).mean(),
                          name='12-Month Moving Average',
                          line=dict(color='red', dash='dash'))
            
            return fig, {
                'total_change': total_change,
                'avg_annual_change': avg_change,
                'current_value': df['value'].iloc[-1],
                'start_date': df['date'].iloc[0].date(),
                'end_date': df['date'].iloc[-1].date()
            }
        else:
            st.error("Insufficient data points for trend analysis")
            return None, None
    except Exception as e:
        st.error(f"Error analyzing sea level trends: {str(e)}")
        return None, None

def get_climate_summary(location="Global"):
    """Generate a summary of climate analysis"""
    try:
        # Get current indicators
        temp, co2, sea_level = get_climate_indicators()
        
        # Get trend analyses
        temp_fig, temp_stats = analyze_temperature_trends()
        co2_fig, co2_stats = analyze_co2_trends()
        sea_fig, sea_stats = analyze_sea_level_trends()
        
        summary = {
            'current': {
                'temperature': temp,
                'co2_level': co2,
                'sea_level': sea_level
            },
            'trends': {
                'temperature': temp_stats if temp_stats else {},
                'co2': co2_stats if co2_stats else {},
                'sea_level': sea_stats if sea_stats else {}
            },
            'visualizations': {
                'temperature': temp_fig,
                'co2': co2_fig,
                'sea_level': sea_fig
            }
        }
        
        return summary
    except Exception as e:
        st.error(f"Error generating climate summary: {str(e)}")
        return None 