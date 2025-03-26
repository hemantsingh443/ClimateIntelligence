import requests
import pandas as pd
import streamlit as st
import os
from datetime import datetime, timedelta
import random

# API Keys
WEATHER_API_KEY = os.getenv("NEXT_PUBLIC_NEWS_API_KEY", "c28b54fbca1e4410ae6a5b00e620c12b")
NEWS_API_KEY = os.getenv("WEATHER_API_KEY", "pub_7577456a90f479845e6c02b6f3cc900976226")

# News functions
@st.cache_data(ttl=3600)
def fetch_climate_news(page=1, page_size=10):
    """Fetch climate news articles from News API"""
    try:
        url = f"https://newsdata.io/api/1/news?apikey={WEATHER_API_KEY}&q=climate%20change&language=en&page={page}&size={page_size}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data.get('status') == 'success':
            return data.get('results', [])
        else:
            st.error(f"API Error: {data.get('message', 'Unknown error')}")
            return []
    except requests.RequestException as e:
        st.error(f"Failed to fetch news: {str(e)}")
        return []

# Weather functions
@st.cache_data(ttl=1800)
def fetch_weather(location):
    """Fetch current weather for a location"""
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={NEWS_API_KEY}&units=metric"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Failed to fetch weather data: {str(e)}")
        return None

@st.cache_data(ttl=1800)
def fetch_forecast(location):
    """Fetch 5-day weather forecast for a location"""
    try:
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={location}&appid={NEWS_API_KEY}&units=metric"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Failed to fetch forecast data: {str(e)}")
        return None
        
# Climate data functions
@st.cache_data(ttl=86400)
def get_climate_indicators():
    """Get current global climate indicators"""
    try:
        # This would ideally call an actual climate data API
        # For now, return reasonable representative values
        global_temp = 1.1  # °C above pre-industrial levels
        co2_level = 418   # parts per million
        sea_level = 3.4   # mm/year rise
        
        return global_temp, co2_level, sea_level
    except Exception as e:
        st.error(f"Failed to fetch climate indicators: {str(e)}")
        return 0, 0, 0

@st.cache_data(ttl=86400)
def get_global_temperature_data():
    """Get historical global temperature anomaly data"""
    try:
        # In a real application, this would call an actual climate data API
        # For demo, generate realistic data based on known trends
        years = list(range(1880, 2023))
        
        # Generate temperature anomalies with an increasing trend
        base_values = [(-0.4 + 0.01 * i) for i in range(len(years))]
        # Add some natural variability
        anomalies = [base + random.uniform(-0.15, 0.15) for base in base_values]
        
        # More recent years have higher anomalies (accelerating warming)
        for i in range(len(years)-50, len(years)):
            anomalies[i] += (i - (len(years)-50)) * 0.01
            
        df = pd.DataFrame({
            'Year': years,
            'Temperature_Anomaly': anomalies
        })
        
        return df
    except Exception as e:
        st.error(f"Failed to fetch temperature data: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=86400)
def get_co2_data():
    """Get historical CO2 concentration data"""
    try:
        # In a real application, this would call an actual climate data API
        years = list(range(1960, 2023))
        
        # Generate CO2 concentration with increasing trend
        # Starting around 315 ppm in 1960 to about 415 ppm in 2022
        base_values = [315 + (i*1.5) for i in range(len(years))]
        # Add seasonal variations
        co2_values = [base + random.uniform(-1, 1) for base in base_values]
        
        # Accelerating in recent decades
        for i in range(len(years)-30, len(years)):
            co2_values[i] += (i - (len(years)-30)) * 0.05
            
        df = pd.DataFrame({
            'Year': years,
            'CO2_Concentration': co2_values
        })
        
        return df
    except Exception as e:
        st.error(f"Failed to fetch CO2 data: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=86400)
def get_sea_level_data():
    """Get historical sea level rise data"""
    try:
        # In a real application, this would call an actual climate data API
        years = list(range(1900, 2023))
        
        # Generate sea level rise with increasing trend
        # More accelerated rise in recent decades
        base_values = []
        for i, year in enumerate(years):
            if year < 1970:
                base_values.append(i * 0.1)  # Slower rise before 1970
            elif year < 1990:
                base_values.append((1970-1900) * 0.1 + (year-1970) * 0.15)  # Medium rise 1970-1990
            else:
                base_values.append((1970-1900) * 0.1 + (1990-1970) * 0.15 + (year-1990) * 0.3)  # Faster rise after 1990
        
        # Add some variability
        sea_level_values = [base + random.uniform(-0.5, 0.5) for base in base_values]
            
        df = pd.DataFrame({
            'Year': years,
            'Sea_Level_Rise': sea_level_values
        })
        
        return df
    except Exception as e:
        st.error(f"Failed to fetch sea level data: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=86400)
def get_climate_events_data():
    """Get data on extreme climate events over time"""
    try:
        # In a real application, this would call an actual climate data API
        years = list(range(1980, 2023))
        
        # Generate data with increasing trend for extreme events
        base_floods = [10 + i * 0.3 + random.uniform(-3, 3) for i in range(len(years))]
        base_droughts = [8 + i * 0.2 + random.uniform(-2, 2) for i in range(len(years))]
        base_storms = [12 + i * 0.25 + random.uniform(-3, 3) for i in range(len(years))]
        base_wildfires = [5 + i * 0.35 + random.uniform(-1, 2) for i in range(len(years))]
        
        # Make events increase more dramatically in recent years
        for i in range(len(years)-20, len(years)):
            factor = (i - (len(years)-20)) * 0.1
            base_floods[i] += factor * 2
            base_droughts[i] += factor * 1.8
            base_storms[i] += factor * 1.5
            base_wildfires[i] += factor * 2.5
            
        df = pd.DataFrame({
            'Year': years,
            'Floods': base_floods,
            'Droughts': base_droughts,
            'Storms': base_storms,
            'Wildfires': base_wildfires
        })
        
        return df
    except Exception as e:
        st.error(f"Failed to fetch climate events data: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=86400)
def get_air_quality_data(location="Global"):
    """Get air quality data for a location or global average"""
    try:
        # In a real application, this would call an actual air quality data API
        years = list(range(2000, 2023))
        
        # Generate PM2.5 data with generally improving trend for developed nations
        # but with significant variation by location
        if location.lower() in ["global", "world", "earth"]:
            # Global average stays relatively flat with slight improvement
            base_values = [25 - (i * 0.1) + random.uniform(-1, 1) for i in range(len(years))]
        elif location.lower() in ["us", "usa", "united states", "europe", "eu", "uk"]:
            # Developed regions show improvement
            base_values = [20 - (i * 0.4) + random.uniform(-1, 1) for i in range(len(years))]
            # Ensure we don't go too low
            base_values = [max(5, val) for val in base_values]
        elif location.lower() in ["china", "india", "asia"]:
            # First increases then decreases in recent years
            base_values = []
            for i, year in enumerate(years):
                if year < 2010:
                    base_values.append(30 + (i * 1) + random.uniform(-2, 2))
                else:
                    peak = base_values[-1]
                    base_values.append(peak - ((year-2010) * 1.2) + random.uniform(-2, 2))
        else:
            # Default pattern for other locations
            base_values = [18 - (i * 0.2) + random.uniform(-2, 2) for i in range(len(years))]
            
        df = pd.DataFrame({
            'Year': years,
            'PM2.5': base_values
        })
        
        return df
    except Exception as e:
        st.error(f"Failed to fetch air quality data: {str(e)}")
        return pd.DataFrame()
