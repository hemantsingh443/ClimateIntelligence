import streamlit as st
import utils
import climate_data
import pandas as pd
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="Climate Analysis | Climate Insights",
    page_icon="📊",
    layout="wide"
)

# Initialize session state variables if they don't exist
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'
    
if 'location' not in st.session_state:
    st.session_state.location = "London"

# Page header
st.title("Climate Analysis")
st.write("Explore data visualizations and insights about our changing climate.")

# Sidebar components
with st.sidebar:
    st.title("Climate Insights")
    
    # Dark/light mode toggle
    theme_toggle = st.toggle("Dark Mode", value=True if st.session_state.theme == 'dark' else False)
    if theme_toggle:
        st.session_state.theme = 'dark'
    else:
        st.session_state.theme = 'light'
    
    # Analysis filters
    st.subheader("Data Options")
    
    timeframe_options = ["1850-Present", "1900-Present", "1950-Present", "2000-Present"]
    selected_timeframe = st.selectbox("Timeframe", timeframe_options)
    
    display_options = ["Temperature", "CO2 Levels", "Sea Level", "All Indicators"]
    selected_display = st.selectbox("Display", display_options)
    
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
st.subheader("Global Climate Indicators")

try:
    # Get temperature data
    temp_df = utils.get_global_temperature_data()
    
    # Get CO2 data
    co2_df = utils.get_co2_data()
    
    # Get sea level data
    sea_level_df = utils.get_sea_level_data()
    
    # Filter data based on selected timeframe
    if selected_timeframe == "1900-Present":
        start_year = 1900
    elif selected_timeframe == "1950-Present":
        start_year = 1950
    elif selected_timeframe == "2000-Present":
        start_year = 2000
    else:
        start_year = 1850
    
    temp_df = temp_df[temp_df['Year'] >= start_year]
    co2_df = co2_df[co2_df['Year'] >= start_year]
    sea_level_df = sea_level_df[sea_level_df['Year'] >= start_year]
    
    # Display charts based on selected option
    if selected_display == "Temperature" or selected_display == "All Indicators":
        st.plotly_chart(climate_data.plot_temperature_chart(temp_df), use_container_width=True)
        
        # Add temperature information
        with st.expander("About Global Temperature Data"):
            st.write("""
                The global temperature anomaly represents how much warmer or cooler the Earth's surface 
                temperature is compared to a reference period (typically 1951-1980). A positive anomaly 
                indicates warming; a negative anomaly indicates cooling.
                
                Key observations:
                - The Earth has warmed by about 1.1°C since pre-industrial times
                - Warming has accelerated since the 1970s
                - The last decade has included the warmest years on record
                - The warming is primarily attributed to human activities, particularly greenhouse gas emissions
            """)
    
    if selected_display == "CO2 Levels" or selected_display == "All Indicators":
        st.plotly_chart(climate_data.plot_co2_chart(co2_df), use_container_width=True)
        
        # Add CO2 information
        with st.expander("About CO2 Concentration Data"):
            st.write("""
                Atmospheric carbon dioxide (CO₂) concentration is measured in parts per million (ppm). 
                CO₂ is the primary greenhouse gas contributing to global warming.
                
                Key observations:
                - Pre-industrial CO₂ levels were around 280 ppm
                - Current levels exceed 410 ppm
                - The rate of increase has accelerated over time
                - The current levels are higher than at any time in at least 800,000 years
                - The increase is primarily due to human activities, especially burning fossil fuels
            """)
    
    if selected_display == "Sea Level" or selected_display == "All Indicators":
        st.plotly_chart(climate_data.plot_sea_level_chart(sea_level_df), use_container_width=True)
        
        # Add sea level information
        with st.expander("About Sea Level Data"):
            st.write("""
                Sea level rise is measured relative to a reference point, typically the average in 1900.
                The rise is caused by two main factors: thermal expansion of seawater as it warms and
                the addition of water from melting ice sheets and glaciers.
                
                Key observations:
                - Global sea level has risen about 20-25 cm since 1900
                - The rate of rise has accelerated in recent decades
                - Current rate is approximately 3.4 mm per year
                - Projections indicate continued rise throughout the 21st century
                - Low-lying coastal areas and island nations are particularly vulnerable
            """)

    # Extreme events section
    st.subheader("Climate-Related Extreme Events")
    extreme_events_df = utils.get_climate_events_data()
    extreme_events_df = extreme_events_df[extreme_events_df['Year'] >= start_year]
    st.plotly_chart(climate_data.plot_extreme_events_chart(extreme_events_df), use_container_width=True)
    
    with st.expander("About Extreme Weather Events"):
        st.write("""
            This chart shows the global trend in different types of extreme weather events over time.
            Climate change is influencing the frequency and intensity of many extreme weather events.
            
            Key observations:
            - Most categories of extreme events have increased in frequency
            - Heatwaves have become more common and intense
            - Heavy precipitation events have increased in frequency and intensity in many regions
            - The economic costs of weather disasters have risen significantly
        """)

except Exception as e:
    st.error(f"An error occurred while fetching or displaying climate data: {str(e)}")
    st.write("Please try again later.")

# Regional climate comparison
st.subheader("Regional Climate Comparison")

try:
    regions = ["Global", "North America", "Europe", "Asia", "Africa", "South America", "Oceania"]
    selected_regions = st.multiselect("Select regions to compare", regions, default=["Global", "North America", "Asia"])
    
    if selected_regions:
        # This would ideally fetch real regional temperature data
        # For demo purposes, we'll create some representative data
        regional_data = []
        
        for region in selected_regions:
            years = list(range(1960, 2023))
            
            # Different baseline and trends for different regions
            if region == "Global":
                base = -0.2
                trend = 0.03
            elif region in ["North America", "Europe"]:
                base = -0.1
                trend = 0.04  # Warming faster than global average
            elif region == "Asia":
                base = -0.15
                trend = 0.045  # Warming even faster
            elif region == "Africa":
                base = -0.1
                trend = 0.035
            else:
                base = -0.15
                trend = 0.025
            
            # Generate temperature anomalies with appropriate trend
            temp_anomalies = [(base + trend * i + (0.01 * i**1.5)/100) for i in range(len(years))]
            
            # Add some natural variability
            import random
            temp_anomalies = [t + random.uniform(-0.2, 0.2) for t in temp_anomalies]
            
            # Add to dataset
            for year, temp in zip(years, temp_anomalies):
                regional_data.append({
                    "Year": year,
                    "Region": region,
                    "Temperature Anomaly (°C)": temp
                })
        
        # Create dataframe
        regional_df = pd.DataFrame(regional_data)
        
        # Plot regional comparison
        fig = px.line(
            regional_df,
            x="Year",
            y="Temperature Anomaly (°C)",
            color="Region",
            title="Regional Temperature Anomalies Comparison"
        )
        
        fig.update_layout(
            xaxis_title="Year",
            yaxis_title="Temperature Anomaly (°C)",
            legend_title="Region",
            hovermode="x unified"
        )
        
        st.plotly_chart(fig, use_container_width=True)

    # Add explanatory text
    st.markdown("""
        Different regions of the world are experiencing climate change at different rates. 
        Generally, land areas are warming faster than ocean regions, and the Arctic is 
        warming at roughly twice the global average rate.
    """)

except Exception as e:
    st.error(f"An error occurred while creating regional comparison: {str(e)}")

# Climate projection section
st.subheader("Future Climate Projections")
st.write("""
    Below are projections for future climate change under different emissions scenarios. 
    These projections are based on climate models that simulate how the Earth's climate 
    system responds to different levels of greenhouse gas emissions.
""")

# Display climate images
st.image("https://images.unsplash.com/photo-1526628953301-3e589a6a8b74", use_container_width=True)

# Create tabs for different scenarios
scenario_tab1, scenario_tab2, scenario_tab3 = st.tabs([
    "Low Emissions (SSP1-2.6)", 
    "Medium Emissions (SSP2-4.5)", 
    "High Emissions (SSP5-8.5)"
])

with scenario_tab1:
    st.write("""
        **Low Emissions Scenario (SSP1-2.6)**
        
        This scenario assumes strong mitigation actions to reduce greenhouse gas emissions:
        - Global temperature rise likely limited to 1.5-2.0°C by 2100
        - Sea level rise of approximately 30-60 cm by 2100
        - Moderate increase in extreme weather events
        - Requires rapid transition to renewable energy and carbon neutrality by 2050
    """)
    
    # Placeholder for projection chart
    years = list(range(2020, 2101))
    low_temp_projection = [(1.1 + 0.005 * i - 0.0001 * i**1.5) for i in range(len(years))]
    
    df = pd.DataFrame({
        "Year": years,
        "Temperature Increase (°C)": low_temp_projection
    })
    
    st.line_chart(df.set_index("Year"))

with scenario_tab2:
    st.write("""
        **Medium Emissions Scenario (SSP2-4.5)**
        
        This scenario assumes moderate mitigation actions:
        - Global temperature rise likely between 2.0-3.0°C by 2100
        - Sea level rise of approximately 40-80 cm by 2100
        - Significant increase in extreme weather events
        - Assumes partial implementation of climate policies
    """)
    
    # Placeholder for projection chart
    years = list(range(2020, 2101))
    med_temp_projection = [(1.1 + 0.012 * i) for i in range(len(years))]
    
    df = pd.DataFrame({
        "Year": years,
        "Temperature Increase (°C)": med_temp_projection
    })
    
    st.line_chart(df.set_index("Year"))

with scenario_tab3:
    st.write("""
        **High Emissions Scenario (SSP5-8.5)**
        
        This scenario assumes minimal mitigation actions:
        - Global temperature rise potentially exceeding 4.0°C by 2100
        - Sea level rise of approximately 60-110 cm by 2100
        - Severe increase in extreme weather events globally
        - Assumes continued heavy reliance on fossil fuels
    """)
    
    # Placeholder for projection chart
    years = list(range(2020, 2101))
    high_temp_projection = [(1.1 + 0.025 * i + 0.0003 * i**1.5) for i in range(len(years))]
    
    df = pd.DataFrame({
        "Year": years,
        "Temperature Increase (°C)": high_temp_projection
    })
    
    st.line_chart(df.set_index("Year"))
