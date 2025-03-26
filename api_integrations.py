import os
import requests
from datetime import datetime
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys from environment variables
NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
NOAA_API_KEY = os.getenv("NOAA_API_KEY")

class NewsDataAPI:
    def __init__(self):
        self.api_key = NEWSDATA_API_KEY
        self.base_url = "https://newsdata.io/api/1"

    def get_climate_news(self, query: str = "climate change", language: str = "en", next_page: str = None, size: int = 10) -> Dict[str, Any]:
        """
        Fetch climate-related news articles
        
        Args:
            query: Search query string
            language: Language code (e.g., 'en' for English)
            next_page: Pagination token from previous response
            size: Number of articles per page (max 10 for free plan)
        
        Returns:
            Dict containing news articles and pagination info
        """
        try:
            params = {
                "apikey": self.api_key,
                "q": query,
                "language": language,
                "size": min(size, 10)  # Ensure we don't exceed free plan limit
            }
            
            # Add next_page parameter if provided
            if next_page:
                params["page"] = next_page
            
            response = requests.get(f"{self.base_url}/latest", params=params)
            response.raise_for_status()
            data = response.json()
            
            # Add pagination info to the response
            if data.get("status") == "success":
                return {
                    "status": "success",
                    "results": data.get("results", []),
                    "nextPage": data.get("nextPage"),
                    "totalResults": data.get("totalResults", 0)
                }
            else:
                return {
                    "status": "error",
                    "message": data.get("message", "Unknown error"),
                    "results": []
                }
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching news: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "results": []
            }

class OpenWeatherAPI:
    def __init__(self):
        self.api_key = OPENWEATHER_API_KEY
        self.base_url = "https://api.openweathermap.org/data/2.5"

    def get_current_weather(self, city: str) -> Dict[str, Any]:
        """Get current weather data for a city"""
        try:
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric"
            }
            response = requests.get(f"{self.base_url}/weather", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather: {str(e)}")
            return {"status": "error", "message": str(e)}

    def get_forecast(self, city: str) -> Dict[str, Any]:
        """Get 5-day weather forecast for a city"""
        try:
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric"
            }
            response = requests.get(f"{self.base_url}/forecast", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching forecast: {str(e)}")
            return {"status": "error", "message": str(e)}

class NOAAAPI:
    def __init__(self):
        self.api_key = NOAA_API_KEY
        self.base_url = "https://api.weather.gov"
        self.global_url = "https://www.ncei.noaa.gov/cdo-web/api/v2"

    def is_us_location(self, lat: float, lon: float) -> bool:
        """Check if coordinates are within the US boundaries"""
        return (25.0 <= lat <= 49.5 and -124.5 <= lon <= -66.95) or \
               (lat >= 49.5 and -124.5 <= lon <= -67.4) or \
               (54.5 <= lat <= 71.5 and -168.0 <= lon <= -140.0)  # Alaska
               
    def get_climate_data(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Get climate data for a location. Uses NOAA Weather API for US locations
        and falls back to NOAA CDO Web Services for international locations.
        """
        try:
            if self.is_us_location(lat, lon):
                # Use Weather.gov API for US locations
                headers = {
                    "User-Agent": "ClimateIntelligence/1.0 (climate.insights@example.com)",
                    "Accept": "application/geo+json"
                }
                response = requests.get(
                    f"{self.base_url}/points/{lat},{lon}",
                    headers=headers
                )
                response.raise_for_status()
                return response.json()
            else:
                # Use NOAA's Climate Data Online Web Services for international locations
                headers = {
                    "token": self.api_key
                }
                
                # Get the nearest station data
                station_url = f"{self.global_url}/stations"
                params = {
                    "extent": f"{lat-1},{lon-1},{lat+1},{lon+1}",
                    "limit": 1
                }
                
                response = requests.get(station_url, headers=headers, params=params)
                response.raise_for_status()
                station_data = response.json()
                
                if station_data.get("results"):
                    station = station_data["results"][0]
                    station_id = station["id"]
                    
                    # Get recent data for this station
                    from datetime import datetime, timedelta
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=30)
                    
                    data_url = f"{self.global_url}/data"
                    params = {
                        "datasetid": "GHCND",  # Global Historical Climatology Network Daily
                        "stationid": station_id,
                        "startdate": start_date.strftime("%Y-%m-%d"),
                        "enddate": end_date.strftime("%Y-%m-%d"),
                        "limit": 1000
                    }
                    
                    response = requests.get(data_url, headers=headers, params=params)
                    response.raise_for_status()
                    
                    return {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [station["longitude"], station["latitude"]]
                        },
                        "properties": {
                            "station": station,
                            "data": response.json(),
                            "elevation": station.get("elevation", 0)
                        }
                    }
                else:
                    return {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [lon, lat]
                        },
                        "properties": {
                            "error": "No nearby weather stations found",
                            "elevation": 0
                        }
                    }
                    
        except requests.exceptions.RequestException as e:
            print(f"Error fetching NOAA data: {str(e)}")
            return {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                },
                "properties": {
                    "error": str(e),
                    "elevation": 0
                }
            }

class WorldBankAPI:
    def __init__(self):
        self.base_url = "https://api.worldbank.org/v2"

    def get_indicator_data(self, indicator_code: str, country: str = "all") -> Dict[str, Any]:
        """Get World Bank indicator data"""
        try:
            url = f"{self.base_url}/country/{country}/indicator/{indicator_code}"
            params = {
                "format": "json",
                "per_page": 1000
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching World Bank data: {str(e)}")
            return {"status": "error", "message": str(e)}

    def get_climate_indicators(self) -> Dict[str, Any]:
        """Get relevant climate indicators"""
        indicators = {
            "CO2 emissions": "EN.ATM.CO2E.KT",
            "Forest area": "AG.LND.FRST.ZS",
            "Renewable energy": "EG.FEC.RNEW.ZS",
            "Population growth": "SP.POP.GROW"
        }
        results = {}
        for name, code in indicators.items():
            results[name] = self.get_indicator_data(code)
        return results

# Example usage:
if __name__ == "__main__":
    # Test NewsData API
    news_api = NewsDataAPI()
    news_data = news_api.get_climate_news()
    print("News API Response:", json.dumps(news_data, indent=2))

    # Test OpenWeather API
    weather_api = OpenWeatherAPI()
    weather_data = weather_api.get_current_weather("London")
    print("Weather API Response:", json.dumps(weather_data, indent=2))

    # Test NOAA API
    noaa_api = NOAAAPI()
    noaa_data = noaa_api.get_climate_data(51.5074, -0.1278)  # London coordinates
    print("NOAA API Response:", json.dumps(noaa_data, indent=2))

    # Test World Bank API
    wb_api = WorldBankAPI()
    wb_data = wb_api.get_climate_indicators()
    print("World Bank API Response:", json.dumps(wb_data, indent=2)) 