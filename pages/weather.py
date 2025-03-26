import streamlit as st
import utils
import folium
from streamlit_folium import folium_static
import pandas as pd
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Weather | Climate Insights",
    page_icon="🌤️",
    layout="wide"
)

# Page header
st.title("Weather Details")
st.write("Current weather conditions and forecast for your selected location.")

# Sidebar components
with st.sidebar:
    st.title("Climate Insights")
    
    # Dark/light mode toggle
    theme_toggle = st.toggle("Dark Mode", value=True if st.session_state.theme == 'dark' else False)
    if theme_toggle:
        st.session_state.theme = 'dark'
    else:
        st.session_state.theme = 'light'
    
    # Location search
    st.subheader("Search Location")
    location_input = st.text_input("Enter city name", value=st.session_state.location)
    if st.button("Search") or location_input != st.session_state.location:
        st.session_state.location = location_input
        st.rerun()
    
    # Navigation
    st.subheader("Navigation")
    st.page_link("app.py", label="Home", icon="🏠")
    st.page_link("pages/news.py", label="Climate News", icon="📰")
    st.page_link("pages/weather.py", label="Weather", icon="🌤️")
    st.page_link("pages/climate_analysis.py", label="Climate Analysis", icon="📊")
    st.page_link("pages/climate_risk.py", label="Climate Risk Factors", icon="⚠️")
    
    st.divider()
    st.caption("© 2023 Climate Insights")

# Main content
location = st.session_state.location

# Current weather section
st.subheader(f"Current Weather in {location}")

try:
    weather_data = utils.fetch_weather(location)
    
    if weather_data and weather_data.get('cod') != '404':
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Main weather stats
            main_weather = weather_data.get('weather', [{}])[0]
            temp = weather_data.get('main', {}).get('temp', 0)
            feels_like = weather_data.get('main', {}).get('feels_like', 0)
            humidity = weather_data.get('main', {}).get('humidity', 0)
            pressure = weather_data.get('main', {}).get('pressure', 0)
            wind_speed = weather_data.get('wind', {}).get('speed', 0)
            
            # Display temperature prominently
            st.markdown(f"### {temp:.1f}°C")
            st.write(f"Feels like {feels_like:.1f}°C")
            st.write(f"**{main_weather.get('description', 'Unknown').title()}**")
            
            # Weather details
            st.markdown("#### Details")
            details_col1, details_col2 = st.columns(2)
            
            with details_col1:
                st.write(f"Humidity: {humidity}%")
                st.write(f"Wind: {wind_speed} m/s")
            
            with details_col2:
                st.write(f"Pressure: {pressure} hPa")
                
                # Convert Unix timestamp to readable time
                sunrise = weather_data.get('sys', {}).get('sunrise', 0)
                sunset = weather_data.get('sys', {}).get('sunset', 0)
                
                if sunrise and sunset:
                    sunrise_time = datetime.fromtimestamp(sunrise).strftime('%H:%M')
                    sunset_time = datetime.fromtimestamp(sunset).strftime('%H:%M')
                    st.write(f"Sunrise: {sunrise_time}")
                    st.write(f"Sunset: {sunset_time}")
        
        with col2:
            # Weather map
            if weather_data.get('coord'):
                lat = weather_data['coord']['lat']
                lon = weather_data['coord']['lon']
                
                # Create a map centered at the location
                m = folium.Map(location=[lat, lon], zoom_start=10)
                
                # Add a marker for the location
                folium.Marker(
                    [lat, lon],
                    popup=f"{location}: {temp:.1f}°C, {main_weather.get('description', 'Unknown').title()}",
                    tooltip=location
                ).add_to(m)
                
                # Display the map
                folium_static(m)
            else:
                st.warning("Map data not available")
    else:
        st.error(f"Could not find weather data for '{location}'. Please try another location.")
        # Show a placeholder image
        st.image("https://images.unsplash.com/photo-1472145246862-b24cf25c4a36", use_column_width=True)

except Exception as e:
    st.error(f"An error occurred while fetching weather data: {str(e)}")
    # Show a placeholder image
    st.image("https://images.unsplash.com/photo-1488812690953-601000f207e4", use_column_width=True)

# Weather forecast section
st.subheader("5-Day Forecast")

try:
    forecast_data = utils.fetch_forecast(location)
    
    if forecast_data and forecast_data.get('cod') != '404':
        # Process forecast data
        forecast_list = forecast_data.get('list', [])
        
        if forecast_list:
            # Create a container for the forecast cards
            forecast_container = st.container()
            
            with forecast_container:
                cols = st.columns(5)
                
                # Get one forecast per day (noon time)
                daily_forecasts = []
                seen_dates = set()
                
                for forecast in forecast_list:
                    dt = datetime.fromtimestamp(forecast['dt'])
                    date_str = dt.strftime('%Y-%m-%d')
                    
                    # Only take one forecast per day
                    if date_str not in seen_dates:
                        seen_dates.add(date_str)
                        daily_forecasts.append(forecast)
                        
                        # Stop after 5 days
                        if len(daily_forecasts) >= 5:
                            break
                
                # Display each day's forecast
                for i, forecast in enumerate(daily_forecasts[:5]):
                    with cols[i]:
                        dt = datetime.fromtimestamp(forecast['dt'])
                        date_str = dt.strftime('%a, %b %d')
                        weather = forecast['weather'][0]
                        temp = forecast['main']['temp']
                        
                        st.write(f"**{date_str}**")
                        st.write(f"{temp:.1f}°C")
                        st.write(f"{weather['description'].title()}")
        else:
            st.warning("Forecast data not available")
    else:
        st.error(f"Could not find forecast data for '{location}'. Please try another location.")

except Exception as e:
    st.error(f"An error occurred while fetching forecast data: {str(e)}")

# Climate impact on this region
st.subheader("Climate Change Impact on this Region")

# This would ideally come from a real climate data API specific to the region
st.write("""
This section would provide information about how climate change is specifically
affecting the selected region, including historical temperature trends, notable
extreme weather events, and projected climate risks.
""")

# Display a relevant climate change image
st.image("https://images.unsplash.com/photo-1579003593419-98f949b9398f", use_column_width=True)

# Show regional climate data
data_tab1, data_tab2 = st.tabs(["Temperature Trends", "Precipitation Changes"])

with data_tab1:
    st.write("Historical temperature trends for this region compared to global averages")
    
    # This would be actual data from a climate API in a production app
    years = list(range(1960, 2023))
    temp_anomalies = [(-0.2 + 0.03 * i + (0.01 * i**1.5)/100) for i in range(len(years))]
    
    # Add some natural variability
    import random
    temp_anomalies = [t + random.uniform(-0.2, 0.2) for t in temp_anomalies]
    
    # Create dataframe
    df = pd.DataFrame({
        "Year": years,
        "Temperature Anomaly (°C)": temp_anomalies
    })
    
    # Plot
    st.line_chart(df.set_index("Year"))

with data_tab2:
    st.write("Precipitation changes in this region over time")
    
    # This would be actual data from a climate API in a production app
    years = list(range(1960, 2023))
    precip_changes = [(0 + 0.1 * i + random.uniform(-5, 5)) for i in range(len(years))]
    
    # Create dataframe
    df = pd.DataFrame({
        "Year": years,
        "Precipitation Change (%)": precip_changes
    })
    
    # Plot
    st.line_chart(df.set_index("Year"))
