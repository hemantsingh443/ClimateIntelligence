import requests
import pandas as pd
import streamlit as st
import os
from datetime import datetime, timedelta
import random
import math
import json
import io
import zipfile
from api_integrations import OpenWeatherAPI, NOAAAPI, WorldBankAPI, NewsDataAPI
import numpy as np
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

# Initialize API clients
news_api = NewsDataAPI()
weather_api = OpenWeatherAPI()
noaa_api = NOAAAPI()
world_bank_api = WorldBankAPI()

# API Keys
NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
NOAA_API_TOKEN = os.getenv("NOAA_API_TOKEN", "VhYxCHiiOUNEgVHGgCXkSfebkcCHYdyB")

def get_noaa_climate_data(dataset_id, start_date, end_date):
    """Fetch climate data from NOAA API V2"""
    try:
        headers = {
            'token': NOAA_API_TOKEN
        }
        url = f"https://www.ncdc.noaa.gov/cdo-web/api/v2/data"
        params = {
            'datasetid': dataset_id,
            'startdate': start_date,
            'enddate': end_date,
            'limit': 1000
        }
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to fetch NOAA data: {str(e)}")
        return None

# News functions
@st.cache_data(ttl=3600)
def fetch_climate_news(next_page=None, page_size=10):
    """
    Fetch climate news articles from NewsData API with pagination support
    
    Args:
        next_page: Pagination token from previous response
        page_size: Number of articles per page (max 10 for free plan)
        
    Returns:
        Tuple of (articles list, next page token, total results)
    """
    try:
        data = news_api.get_climate_news(next_page=next_page, size=page_size)
        
        if data.get('status') == 'success':
            return (
                data.get('results', []),
                data.get('nextPage'),
                data.get('totalResults', 0)
            )
        else:
            st.error(f"API Error: {data.get('message', 'Unknown error')}")
            return [], None, 0
            
    except Exception as e:
        st.error(f"Failed to fetch news: {str(e)}")
        return [], None, 0

# Weather functions
@st.cache_data(ttl=1800)
def fetch_weather(location):
    """Fetch real weather data for a location from OpenWeatherMap API"""
    try:
        data = weather_api.get_current_weather(location)
        if not data.get('status') == 'error':
            return data
        else:
            st.error(f"Could not find location: {location}")
            return None
    except Exception as e:
        st.error(f"Failed to fetch weather data: {str(e)}")
        return None

@st.cache_data(ttl=1800)
def fetch_forecast(location):
    """Fetch 5-day weather forecast from OpenWeatherMap API"""
    try:
        data = weather_api.get_forecast(location)
        if not data.get('status') == 'error':
            return data
        else:
            st.error(f"Could not find location for forecast: {location}")
            return None
    except Exception as e:
        st.error(f"Failed to fetch forecast data: {str(e)}")
        return None
        
# Climate data functions
@st.cache_data(ttl=86400)
def get_climate_indicators(location="London"):
    """Get current climate indicators from various sources"""
    try:
        # Get World Bank data
        wb_data = world_bank_api.get_climate_indicators()
        
        # Initialize default values
        global_temp = 0
        co2_level = 0
        sea_level = 0
        
        # Process CO2 data
        co2_data = wb_data.get("CO2 emissions", [])
        if co2_data and len(co2_data) > 1 and isinstance(co2_data[1], list) and co2_data[1]:
            # Sort by date to get the most recent value
            sorted_data = sorted(co2_data[1], key=lambda x: x.get('date', ''), reverse=True)
            latest_co2 = next((item for item in sorted_data if item.get('value') is not None), None)
            if latest_co2:
                try:
                    co2_level = float(latest_co2.get('value', 0))
                except (ValueError, TypeError):
                    st.warning("Invalid CO2 data format")
                    co2_level = 0
            
        # Get temperature data
        temp_data = wb_data.get("Forest area", [])
        if temp_data and len(temp_data) > 1 and isinstance(temp_data[1], list) and temp_data[1]:
            # Sort by date to get the most recent value
            sorted_data = sorted(temp_data[1], key=lambda x: x.get('date', ''), reverse=True)
            latest_temp = next((item for item in sorted_data if item.get('value') is not None), None)
            if latest_temp:
                try:
                    global_temp = float(latest_temp.get('value', 0))
                except (ValueError, TypeError):
                    st.warning("Invalid temperature data format")
                    global_temp = 0
            
        # For non-US locations, use alternative sea level data source
        try:
            # Use global sea level rise data from satellite altimetry
            current_year = datetime.now().year
            url = "https://climate.nasa.gov/vital-signs/sea-level/data.json"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and data:
                    # Get the most recent measurement
                    latest = data[-1]
                    if isinstance(latest, dict) and 'value' in latest:
                        sea_level = float(latest['value'])
            else:
                # Fallback to estimated global average sea level rise
                # Current rate is approximately 3.3 mm per year since 1993
                years_since_1993 = current_year - 1993
                sea_level = 3.3 * years_since_1993  # Approximate cumulative rise in mm
                
        except Exception as e:
            st.warning(f"Using estimated sea level data: {str(e)}")
            # Use conservative estimate if all else fails
            sea_level = 100  # Approximate cumulative rise since 1900 in mm
        
        return global_temp, co2_level, sea_level
    except Exception as e:
        st.error(f"Error fetching climate indicators: {str(e)}")
        return 0, 0, 0

@st.cache_data(ttl=86400)
def get_global_temperature_data():
    """Get historical global temperature anomaly data from NASA GISS"""
    try:
        # NASA GISS Surface Temperature Analysis (GISTEMP) data
        url = "https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv"
        
        # Read directly from NASA's CSV file
        df = pd.read_csv(url, skiprows=1)
        
        # Process the data - first column is Year, Jan-Dec are monthly anomalies, then annual average
        # Keep only Year and annual mean columns
        if 'Year' in df.columns and 'J-D' in df.columns:
            df = df[['Year', 'J-D']]
            df = df.rename(columns={'J-D': 'Temperature_Anomaly'})
            
            # Convert to numeric, replacing non-numeric values with NaN
            df['Temperature_Anomaly'] = pd.to_numeric(df['Temperature_Anomaly'], errors='coerce')
            
            # Convert temperature anomalies from 100ths of a degree to degrees
            df['Temperature_Anomaly'] = df['Temperature_Anomaly'] / 100
            
            # Filter out incomplete years (where annual mean is missing)
            df = df.dropna()
            
            # Convert Year to integer
            df['Year'] = df['Year'].astype(int)
            
            return df
        else:
            st.warning("NASA temperature data format has changed. Falling back to backup source.")
            # Fallback to Berkeley Earth data
            url = "https://berkeley-earth-temperature.s3.amazonaws.com/Global/Land_and_Ocean_summary.txt"
            
            # This file has a complex header, so we'll read it directly and parse
            response = requests.get(url)
            if response.status_code == 200:
                lines = response.text.splitlines()
                data_lines = []
                data_start = False
                
                for line in lines:
                    if line.startswith("% Year"):
                        data_start = True
                        continue
                    if data_start and line and not line.startswith("%"):
                        data_lines.append(line)
                
                # Parse the data
                years = []
                temps = []
                for line in data_lines:
                    parts = line.split()
                    if len(parts) >= 2:
                        years.append(int(float(parts[0])))
                        temps.append(float(parts[1]))
                
                df = pd.DataFrame({
                    'Year': years,
                    'Temperature_Anomaly': temps
                })
                
                return df
            else:
                raise Exception(f"Failed to fetch backup temperature data: {response.status_code}")
    except Exception as e:
        st.error(f"Failed to fetch temperature data: {str(e)}")
        # Return an empty DataFrame with the expected columns
        return pd.DataFrame(columns=['Year', 'Temperature_Anomaly'])

@st.cache_data(ttl=86400)
def get_co2_data():
    """Get historical CO2 concentration data from NOAA"""
    try:
        # NOAA Global Monitoring Laboratory - Mauna Loa CO2 annual mean data
        url = "https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_annmean_mlo.txt"
        
        response = requests.get(url)
        if response.status_code == 200:
            # Parse the data file - it's a fixed-width text file
            lines = response.text.splitlines()
            
            years = []
            co2_values = []
            
            for line in lines:
                # Skip comments and headers
                if not line.startswith('#') and len(line.strip()) > 0:
                    parts = line.split()
                    if len(parts) >= 2:
                        try:
                            year = int(parts[0])
                            co2 = float(parts[1])
                            years.append(year)
                            co2_values.append(co2)
                        except (ValueError, IndexError):
                            # Skip lines that can't be parsed
                            continue
            
            df = pd.DataFrame({
                'Year': years,
                'CO2_Concentration': co2_values
            })
            
            return df
        else:
            # Fallback to Scripps CO2 Program data
            url = "https://scrippsco2.ucsd.edu/assets/data/atmospheric/stations/in_situ_co2/monthly/monthly_in_situ_co2_mlo.csv"
            
            response = requests.get(url)
            if response.status_code == 200:
                # Parse the data file
                lines = response.text.splitlines()
                
                # Find where data begins
                data_start = 0
                for i, line in enumerate(lines):
                    if 'yr,mn,date' in line.lower():
                        data_start = i + 1
                        break
                
                # Extract data
                years = []
                co2_values = []
                year_averages = {}
                
                for i in range(data_start, len(lines)):
                    parts = lines[i].split(',')
                    if len(parts) >= 3:
                        try:
                            year = int(float(parts[0]))
                            # Use the interpolated value if available (column 4)
                            co2 = float(parts[3]) if len(parts) > 3 and parts[3].strip() else None
                            
                            if co2 is not None:
                                if year not in year_averages:
                                    year_averages[year] = []
                                year_averages[year].append(co2)
                        except (ValueError, IndexError):
                            continue
                
                # Calculate annual averages
                for year, values in year_averages.items():
                    if values:
                        years.append(year)
                        co2_values.append(sum(values) / len(values))
                
                df = pd.DataFrame({
                    'Year': years,
                    'CO2_Concentration': co2_values
                })
                
                # Sort by year
                df = df.sort_values('Year')
                
                return df
            else:
                raise Exception(f"Failed to fetch CO2 data: {response.status_code}")
    except Exception as e:
        st.error(f"Failed to fetch CO2 data: {str(e)}")
        # Return an empty DataFrame with the expected columns
        return pd.DataFrame(columns=['Year', 'CO2_Concentration'])

@st.cache_data(ttl=86400)
def get_sea_level_data():
    """Get historical sea level rise data from CSIRO"""
    try:
        # CSIRO (Commonwealth Scientific and Industrial Research Organisation) sea level data
        url = "https://www.cmar.csiro.au/sealevel/downloads/church_white_gmsl_2011_up.zip"
        
        # Download and extract the zip file
        response = requests.get(url)
        if response.status_code == 200:
            import io
            import zipfile
            
            # Extract the zip file in memory
            z = zipfile.ZipFile(io.BytesIO(response.content))
            
            try:
                # Try different possible filenames for sea level data
                sea_level_files = [f for f in z.namelist() if 'gmsl' in f.lower()]
                if sea_level_files:
                    with z.open(sea_level_files[0]) as f:
                        lines = f.read().decode('utf-8').splitlines()
                        
                        years = []
                        sea_levels = []
                        
                        # Skip the header (first line)
                        for line in lines[1:]:
                            parts = line.split()
                            if len(parts) >= 2:
                                try:
                                    year = float(parts[0])
                                    # Convert to mm and use as the sea level rise value
                                    sea_level = float(parts[1])
                                    
                                    years.append(int(year))
                                    sea_levels.append(sea_level)
                                except (ValueError, IndexError):
                                    continue
                        
                        df = pd.DataFrame({
                            'Year': years,
                            'Sea_Level_Rise': sea_levels
                        })
                        
                        return df
                else:
                    raise Exception("No sea level files found in archive")
            except (KeyError, zipfile.BadZipFile):
                # If that file isn't in the zip, try an alternative
                raise Exception("Expected file not found in the zip archive")
        
        # Fall back to another source if CSIRO data is unavailable
        url = "https://climate.nasa.gov/system/internal_resources/details/original/121_Global_Sea_Level_Data_File.txt"
        response = requests.get(url)
        
        if response.status_code == 200:
            lines = response.text.splitlines()
            
            years = []
            sea_levels = []
            
            # Skip header lines
            for line in lines:
                if line.startswith('#') or not line.strip():
                    continue
                    
                parts = line.strip().split(',')
                if len(parts) >= 2:
                    try:
                        # Data is in format: year, sea_level_mm
                        year = float(parts[0])
                        sea_level = float(parts[1])
                        
                        years.append(int(year))
                        sea_levels.append(sea_level)
                    except (ValueError, IndexError):
                        continue
            
            df = pd.DataFrame({
                'Year': years,
                'Sea_Level_Rise': sea_levels
            })
            
            return df
        else:
            raise Exception(f"Failed to fetch sea level data: {response.status_code}")
            
    except Exception as e:
        st.error(f"Failed to fetch sea level data: {str(e)}")
        # Return an empty DataFrame with the expected columns
        return pd.DataFrame(columns=['Year', 'Sea_Level_Rise'])

@st.cache_data(ttl=86400)
def get_climate_events_data():
    """Get data on extreme climate events over time from EM-DAT via World Bank Climate Data API"""
    try:
        # EM-DAT disaster data via World Bank Climate Change Knowledge Portal
        url = "https://climateknowledgeportal.worldbank.org/api/data/get-download-dataset/historical/disaster/emdat/1980/2022/all"
        
        response = requests.get(url)
        if response.status_code == 200:
            # Parse the CSV data
            import io
            df_raw = pd.read_csv(io.StringIO(response.text))
            
            # Group by year and disaster type to get counts
            if 'Year' in df_raw.columns and 'Disaster Type' in df_raw.columns:
                # Count events by year and type
                events_by_year = df_raw.groupby(['Year', 'Disaster Type']).size().reset_index(name='Count')
                
                # Pivot the data to get disaster types as columns
                events_pivot = events_by_year.pivot_table(
                    index='Year', 
                    columns='Disaster Type', 
                    values='Count',
                    fill_value=0
                ).reset_index()
                
                # Rename columns to match our expected format
                column_mapping = {
                    'Flood': 'Floods',
                    'Drought': 'Droughts',
                    'Storm': 'Storms',
                    'Wildfire': 'Wildfires'
                }
                
                # Create a new DataFrame with the columns we need
                years = sorted(events_pivot['Year'].unique())
                result_data = {'Year': years}
                
                for disaster_type, column_name in column_mapping.items():
                    if disaster_type in events_pivot.columns:
                        result_data[column_name] = [
                            events_pivot[events_pivot['Year'] == year][disaster_type].iloc[0] 
                            if year in events_pivot['Year'].values else 0
                            for year in years
                        ]
                    else:
                        # If a disaster type isn't in the data, use zeros
                        result_data[column_name] = [0] * len(years)
                
                return pd.DataFrame(result_data)
            
            else:
                raise Exception("Unexpected data format from EM-DAT API")
                
        # Fallback to NOAA's Billion-Dollar Weather and Climate Disasters data
        url = "https://www.ncei.noaa.gov/access/billions/time-series.csv"
        
        response = requests.get(url)
        if response.status_code == 200:
            # Parse the CSV data
            import io
            df_noaa = pd.read_csv(io.StringIO(response.text))
            
            if 'Year' in df_noaa.columns:
                # Process NOAA data which has columns like 'Drought', 'Flooding', etc.
                years = sorted(df_noaa['Year'].unique())
                
                # Extract relevant columns
                result_data = {'Year': years}
                
                # Map NOAA columns to our categories
                column_mapping = {
                    'Flooding': 'Floods',
                    'Drought': 'Droughts',
                    'Tropical Cyclone': 'Storms',
                    'Severe Storm': 'Storms',
                    'Winter Storm': 'Storms',
                    'Wildfire': 'Wildfires'
                }
                
                # Initialize columns with zeros
                for column in ['Floods', 'Droughts', 'Storms', 'Wildfires']:
                    result_data[column] = [0] * len(years)
                
                # Sum up the events by category
                for noaa_col, our_col in column_mapping.items():
                    if noaa_col in df_noaa.columns:
                        for i, year in enumerate(years):
                            year_data = df_noaa[df_noaa['Year'] == year]
                            if not year_data.empty:
                                # Add the count to our category
                                result_data[our_col][i] += year_data[noaa_col].fillna(0).iloc[0]
                
                return pd.DataFrame(result_data)
            else:
                raise Exception("Unexpected data format from NOAA API")
        
        else:
            raise Exception(f"Failed to fetch climate events data: {response.status_code}")
            
    except Exception as e:
        st.error(f"Failed to fetch climate events data: {str(e)}")
        # Return an empty DataFrame with the expected columns
        return pd.DataFrame(columns=['Year', 'Floods', 'Droughts', 'Storms', 'Wildfires'])

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_air_quality_data(location="Global"):
    """Get air quality data for a location using real-time and historical sources"""
    try:
        # First try OpenAQ API for real-time data
        openaq_url = f"https://api.openaq.org/v2/locations"
        params = {
            'limit': 100,
            'page': 1,
            'offset': 0,
            'sort': 'desc',
            'radius': 1000,
            'order_by': 'lastUpdated',
            'parameter': 'pm25'
        }
        
        # Add location-specific parameters
        if location.lower() not in ["global", "world", "earth"]:
            params['location'] = location
            
        response = requests.get(openaq_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if 'results' in data and data['results']:
                # Process real-time measurements
                measurements = []
                current_year = datetime.now().year
                years = list(range(current_year - 5, current_year + 1))
                
                for result in data['results']:
                    if 'parameters' in result:
                        for param in result['parameters']:
                            if param.get('parameter') == 'pm25':
                                try:
                                    value = float(param.get('lastValue', 0))
                                    if value > 0:
                                        measurements.append(value)
                                except (ValueError, TypeError):
                                    continue
                
                if measurements:
                    # Calculate average PM2.5 for the location
                    current_pm25 = sum(measurements) / len(measurements)
                    
                    # Create historical trend based on available data and known reduction rates
                    pm25_values = []
                    for year in years:
                        if year == current_year:
                            pm25_values.append(current_pm25)
                        else:
                            # Estimate historical values using typical year-over-year changes
                            # Based on WHO data showing average annual changes
                            year_diff = current_year - year
                            historical_value = current_pm25 * (1 + (0.02 * year_diff))  # Assume 2% annual change
                            pm25_values.append(historical_value)
                    
                    df = pd.DataFrame({
                        'Year': years,
                        'PM2.5': pm25_values
                    })
                    
                    return df
        
        # If OpenAQ fails, try World Bank API
        wb_url = "http://api.worldbank.org/v2/country/all/indicator/EN.ATM.PM25.MC.M3"
        params = {
            'format': 'json',
            'per_page': 1000,
            'date': f"{datetime.now().year-5}:{datetime.now().year}"
        }
        
        response = requests.get(wb_url, params=params)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 1:
                records = []
                for item in data[1]:
                    try:
                        year = int(item['date'])
                        value = float(item['value'])
                        records.append({'Year': year, 'PM2.5': value})
                    except (ValueError, KeyError, TypeError):
                        continue
                
                if records:
                    df = pd.DataFrame(records)
                    df = df.sort_values('Year')
                    return df
        
        # If both APIs fail, use WHO Global Ambient Air Quality Database
        who_url = "https://www.who.int/data/gho/data/indicators/indicator-details/GHO/concentrations-of-fine-particulate-matter-(pm2-5)"
        response = requests.get(who_url)
        
        if response.status_code == 200:
            # Parse WHO data (XML format)
            try:
                soup = BeautifulSoup(response.content, 'xml')
                records = []
                
                for fact in soup.find_all('Fact'):
                    try:
                        year = int(fact.find('YEAR').text)
                        value = float(fact.find('Display').text)
                        records.append({'Year': year, 'PM2.5': value})
                    except (ValueError, AttributeError):
                        continue
                
                if records:
                    df = pd.DataFrame(records)
                    df = df.sort_values('Year')
                    return df
            except Exception as e:
                st.warning(f"Error parsing WHO data: {str(e)}")
        
        # If all APIs fail, return empty DataFrame
        st.warning("Could not fetch real-time air quality data. Please try again later.")
        return pd.DataFrame(columns=['Year', 'PM2.5'])
            
    except Exception as e:
        st.error(f"Failed to fetch air quality data: {str(e)}")
        return pd.DataFrame(columns=['Year', 'PM2.5'])

def get_weather_data(location: str):
    """Get weather data for a specific location"""
    try:
        weather_api = OpenWeatherAPI()
        current_weather = weather_api.get_current_weather(location)
        forecast = weather_api.get_forecast(location)
        
        return {
            "current": current_weather,
            "forecast": forecast
        }
    except Exception as e:
        print(f"Error fetching weather data: {str(e)}")
        return None

def get_climate_trends():
    """Get climate trends from World Bank data"""
    try:
        wb_api = WorldBankAPI()
        indicators = wb_api.get_climate_indicators()
        
        # Process the data into a format suitable for visualization
        trends = {
            "CO2_emissions": [],
            "Forest_area": [],
            "Renewable_energy": [],
            "Population_growth": []
        }
        
        for indicator, data in indicators.items():
            if isinstance(data, list):
                for entry in data:
                    if isinstance(entry, dict) and "value" in entry:
                        trends[indicator.replace(" ", "_")].append({
                            "year": entry.get("date", ""),
                            "value": entry.get("value", 0)
                        })
        
        return trends
    except Exception as e:
        print(f"Error fetching climate trends: {str(e)}")
        return None

def get_historical_data(start_year: int = 1960, end_year: int = 2020):
    """Get historical climate data"""
    try:
        wb_api = WorldBankAPI()
        indicators = wb_api.get_climate_indicators()
        
        # Create a DataFrame with historical data
        data = []
        for year in range(start_year, end_year + 1):
            year_data = {"Year": year}
            for indicator, values in indicators.items():
                if isinstance(values, list):
                    for entry in values:
                        if isinstance(entry, dict) and entry.get("date") == str(year):
                            year_data[indicator.replace(" ", "_")] = entry.get("value", 0)
            data.append(year_data)
        
        return pd.DataFrame(data)
    except Exception as e:
        print(f"Error fetching historical data: {str(e)}")
        return pd.DataFrame()

def get_climate_risk_assessment(location: str):
    """Get climate risk assessment for a location"""
    try:
        # Get weather data
        weather_data = get_weather_data(location)
        
        # Get climate trends
        trends = get_climate_trends()
        
        # Calculate risk factors
        risk_factors = {
            "temperature_risk": 0.5,
            "precipitation_risk": 0.5,
            "extreme_events_risk": 0.5,
            "sea_level_risk": 0.5
        }
        
        if weather_data and "current" in weather_data:
            current = weather_data["current"]
            if "main" in current:
                temp = current["main"].get("temp", 0)
                risk_factors["temperature_risk"] = min(1.0, max(0.0, (temp - 20) / 30))
        
        return risk_factors
    except Exception as e:
        print(f"Error calculating climate risk: {str(e)}")
        return None
