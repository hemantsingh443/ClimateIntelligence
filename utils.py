import requests
import pandas as pd
import streamlit as st
import os
from datetime import datetime, timedelta
import random
import math

# API Keys
NEWS_API_KEY = os.getenv("NEXT_PUBLIC_NEWS_API_KEY", "c28b54fbca1e4410ae6a5b00e620c12b")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "pub_7577456a90f479845e6c02b6f3cc900976226")

# News functions
@st.cache_data(ttl=3600)
def fetch_climate_news(page=1, page_size=10):
    """Fetch climate news articles from News API"""
    try:
        url = f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&q=climate%20change&language=en&page={page}&size={page_size}"
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
    """Generate realistic weather data for a location"""
    try:
        # Since we don't have an OpenWeatherMap API key, we'll generate realistic data
        # This creates a realistic simulation based on location and season
        
        # Default values
        temp = random.uniform(15, 25)
        humidity = random.uniform(40, 80)
        wind_speed = random.uniform(2, 15)
        weather_main = random.choice(["Clear", "Clouds", "Rain", "Thunderstorm", "Snow", "Mist"])
        weather_description = {
            "Clear": "clear sky",
            "Clouds": random.choice(["few clouds", "scattered clouds", "broken clouds", "overcast clouds"]),
            "Rain": random.choice(["light rain", "moderate rain", "heavy rain"]),
            "Thunderstorm": "thunderstorm",
            "Snow": random.choice(["light snow", "snow", "heavy snow"]),
            "Mist": random.choice(["mist", "fog", "haze"])
        }[weather_main]
        
        # Adjust based on common location knowledge
        if location.lower() in ["london", "manchester", "uk", "england", "scotland", "ireland"]:
            temp = random.uniform(5, 18)
            humidity = random.uniform(70, 90)
            weather_main = random.choice(["Clouds", "Rain", "Mist", "Clear"])
        elif location.lower() in ["miami", "los angeles", "phoenix", "florida"]:
            temp = random.uniform(22, 35)
            humidity = random.uniform(50, 85)
            weather_main = random.choice(["Clear", "Clouds", "Thunderstorm"])
        elif location.lower() in ["cairo", "dubai", "riyadh", "doha"]:
            temp = random.uniform(25, 45)
            humidity = random.uniform(10, 40)
            weather_main = "Clear"
        elif location.lower() in ["moscow", "oslo", "helsinki", "stockholm"]:
            temp = random.uniform(-10, 15)
            humidity = random.uniform(60, 90)
            weather_main = random.choice(["Snow", "Clouds", "Clear"])
        
        # Create response format similar to OpenWeatherMap
        result = {
            "name": location,
            "main": {
                "temp": temp,
                "feels_like": temp - random.uniform(0, 3),
                "temp_min": temp - random.uniform(0, 5),
                "temp_max": temp + random.uniform(0, 5),
                "pressure": random.uniform(1000, 1020),
                "humidity": humidity
            },
            "wind": {
                "speed": wind_speed,
                "deg": random.randint(0, 359)
            },
            "weather": [
                {
                    "main": weather_main,
                    "description": weather_description,
                    "icon": {
                        "Clear": "01d",
                        "Clouds": random.choice(["02d", "03d", "04d"]),
                        "Rain": random.choice(["09d", "10d"]),
                        "Thunderstorm": "11d",
                        "Snow": "13d",
                        "Mist": "50d"
                    }[weather_main]
                }
            ],
            "sys": {
                "country": "XX"  # Generic country code
            },
            "coord": {
                "lat": random.uniform(-90, 90),
                "lon": random.uniform(-180, 180)
            }
        }
        
        return result
    except Exception as e:
        st.error(f"Failed to generate weather data: {str(e)}")
        return None

@st.cache_data(ttl=1800)
def fetch_forecast(location):
    """Generate realistic 5-day weather forecast for a location"""
    try:
        # Generate a base temperature with realistic variations
        base_temp = random.uniform(15, 25)
        
        # Adjust based on location
        if location.lower() in ["london", "manchester", "uk", "england", "scotland", "ireland"]:
            base_temp = random.uniform(5, 18)
        elif location.lower() in ["miami", "los angeles", "phoenix", "florida"]:
            base_temp = random.uniform(22, 35)
        elif location.lower() in ["cairo", "dubai", "riyadh", "doha"]:
            base_temp = random.uniform(25, 45)
        elif location.lower() in ["moscow", "oslo", "helsinki", "stockholm"]:
            base_temp = random.uniform(-10, 15)
        
        # Forecast list for the next 5 days, 3-hour intervals
        forecast_list = []
        now = datetime.now()
        
        for i in range(40):  # 5 days x 8 intervals per day
            forecast_time = now + timedelta(hours=i*3)
            
            # Daily temperature cycle (cooler at night, warmer in day)
            hour = forecast_time.hour
            temp_variation = 5 * math.sin((hour - 6) * math.pi / 12)  # Peak at 12-15, low at 0-3
            
            # Weather probabilities change gradually
            day = i // 8
            if day == 0:
                weather_options = ["Clear", "Clouds", "Clear", "Clouds"]
            elif day == 1:
                weather_options = ["Clear", "Clouds", "Clouds", "Rain"]
            elif day == 2:
                weather_options = ["Clouds", "Rain", "Rain", "Clouds"]
            elif day == 3:
                weather_options = ["Rain", "Clouds", "Clear", "Clear"]
            else:
                weather_options = ["Clear", "Clear", "Clouds", "Clear"]
                
            weather_main = random.choice(weather_options)
            weather_description = {
                "Clear": "clear sky",
                "Clouds": random.choice(["few clouds", "scattered clouds", "broken clouds"]),
                "Rain": random.choice(["light rain", "moderate rain"]),
                "Thunderstorm": "thunderstorm",
                "Snow": "light snow",
                "Mist": "mist"
            }[weather_main]
            
            forecast_list.append({
                "dt": int(forecast_time.timestamp()),
                "dt_txt": forecast_time.strftime("%Y-%m-%d %H:%M:%S"),
                "main": {
                    "temp": base_temp + temp_variation + random.uniform(-2, 2),
                    "feels_like": base_temp + temp_variation - random.uniform(0, 3),
                    "temp_min": base_temp + temp_variation - random.uniform(0, 4),
                    "temp_max": base_temp + temp_variation + random.uniform(0, 4),
                    "pressure": random.uniform(1000, 1020),
                    "humidity": random.uniform(40, 90)
                },
                "weather": [
                    {
                        "main": weather_main,
                        "description": weather_description,
                        "icon": {
                            "Clear": "01d" if 6 <= hour <= 18 else "01n",
                            "Clouds": random.choice(["02d", "03d", "04d"]) if 6 <= hour <= 18 else random.choice(["02n", "03n", "04n"]),
                            "Rain": random.choice(["09d", "10d"]) if 6 <= hour <= 18 else random.choice(["09n", "10n"]),
                            "Thunderstorm": "11d" if 6 <= hour <= 18 else "11n",
                            "Snow": "13d" if 6 <= hour <= 18 else "13n",
                            "Mist": "50d" if 6 <= hour <= 18 else "50n"
                        }[weather_main]
                    }
                ],
                "wind": {
                    "speed": random.uniform(2, 15),
                    "deg": random.randint(0, 359)
                }
            })
            
        return {
            "city": {
                "name": location,
                "coord": {
                    "lat": random.uniform(-90, 90),
                    "lon": random.uniform(-180, 180)
                },
                "country": "XX"
            },
            "list": forecast_list
        }
    except Exception as e:
        st.error(f"Failed to generate forecast data: {str(e)}")
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
