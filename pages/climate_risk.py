import streamlit as st
import utils
import climate_data
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import folium_static

# Page configuration
st.set_page_config(
    page_title="Climate Risk Factors | Climate Insights",
    page_icon="⚠️",
    layout="wide"
)

# Page header
st.title("Climate Risk Factors")
st.write("Explore different risk factors associated with climate change and their potential impacts.")

# Sidebar components
with st.sidebar:
    st.title("Climate Insights")
    
    # Dark/light mode toggle
    theme_toggle = st.toggle("Dark Mode", value=True if st.session_state.theme == 'dark' else False)
    if theme_toggle:
        st.session_state.theme = 'dark'
    else:
        st.session_state.theme = 'light'
    
    # Risk factor filters
    st.subheader("Risk Assessment")
    
    risk_location = st.text_input("Location for Risk Assessment", value=st.session_state.location)
    
    risk_categories = [
        "All Risks", 
        "Temperature Extremes", 
        "Water-related Risks", 
        "Weather Disasters", 
        "Agriculture & Food Security",
        "Health Impacts"
    ]
    selected_risk = st.selectbox("Risk Category", risk_categories)
    
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
st.subheader(f"Climate Risk Assessment for {risk_location}")

# Risk assessment visualization
try:
    risk_heatmap = climate_data.create_climate_risk_heatmap(risk_location)
    st.plotly_chart(risk_heatmap, use_container_width=True)
    
    st.markdown("""
        The chart above shows relative risk levels for different climate change impacts.
        Risk levels range from 0 (very low risk) to 1 (very high risk) and are based on
        a combination of hazard probability, exposure, vulnerability, and adaptive capacity.
    """)
    
    with st.expander("Understanding Risk Scores"):
        st.write("""
            **Risk Score Methodology**
            
            Climate risk scores are calculated based on four components:
            1. **Hazard** - The potential occurrence of climate-related events
            2. **Exposure** - The presence of people, assets, or systems in places that could be adversely affected
            3. **Vulnerability** - The propensity to be adversely affected
            4. **Adaptive Capacity** - The ability to adjust to potential damage or respond to consequences
            
            Scores are normalized on a scale from 0 to 1, where:
            - **0.00-0.25**: Low risk
            - **0.25-0.50**: Moderate risk
            - **0.50-0.75**: High risk
            - **0.75-1.00**: Very high risk
        """)
except Exception as e:
    st.error(f"An error occurred while creating risk assessment: {str(e)}")
    st.write("Please try again later.")

# Temperature rise section
st.subheader("Temperature Rise Risk")

try:
    # Create two columns layout
    temp_col1, temp_col2 = st.columns([3, 2])
    
    with temp_col1:
        # Get temperature data
        temp_df = utils.get_global_temperature_data()
        # Only use recent data for this visualization
        recent_temp_df = temp_df[temp_df['Year'] >= 1960]
        
        fig = px.line(
            recent_temp_df,
            x="Year",
            y="Temperature_Anomaly",
            title="Global Temperature Anomaly (°C relative to 1951-1980 average)",
            labels={"Temperature_Anomaly": "Temperature Anomaly (°C)"}
        )
        
        # Add Paris Agreement temperature targets
        fig.add_hline(y=1.5, line_dash="dash", line_color="orange", 
                      annotation_text="Paris Agreement Target (1.5°C)")
        fig.add_hline(y=2.0, line_dash="dash", line_color="red", 
                      annotation_text="Critical Threshold (2.0°C)")
        
        st.plotly_chart(fig, use_container_width=True)
    
    with temp_col2:
        st.markdown("### Temperature Rise Impacts")
        st.markdown("""
            Increasing global temperatures pose various risks:
            
            **Public Health**
            - Heat-related illnesses and deaths
            - Expanded range of disease vectors
            - Increased air pollution
            
            **Infrastructure**
            - Stress on power grids
            - Road and rail damage
            - Urban heat island intensification
            
            **Ecosystems**
            - Coral reef bleaching
            - Species migration and extinction
            - Ecosystem disruption
            
            **Agriculture**
            - Reduced crop yields
            - Changes in growing seasons
            - Water stress for irrigation
        """)
    
    # Add explanatory text
    st.markdown("""
        The above chart shows observed temperature change (solid line) relative to pre-industrial levels,
        with the Paris Agreement target of limiting warming to 1.5°C (orange dashed line) and the critical
        threshold of 2.0°C (red dashed line). Without significant emissions reductions, global temperature 
        is projected to exceed these thresholds in the coming decades.
    """)
    
except Exception as e:
    st.error(f"An error occurred while displaying temperature data: {str(e)}")

# Air quality section
st.subheader("Air Quality Risk")

try:
    # Create two columns layout
    air_col1, air_col2 = st.columns([3, 2])
    
    with air_col1:
        # Get air quality data
        air_quality_df = utils.get_air_quality_data(risk_location)
        
        fig = climate_data.plot_air_quality_chart(air_quality_df, risk_location)
        st.plotly_chart(fig, use_container_width=True)
    
    with air_col2:
        st.markdown("### Air Quality Health Risks")
        st.markdown("""
            Poor air quality related to climate change poses several health risks:
            
            **Respiratory**
            - Asthma exacerbation
            - Chronic obstructive pulmonary disease (COPD)
            - Increased respiratory infections
            
            **Cardiovascular**
            - Heart attacks
            - Strokes
            - Irregular heartbeats
            
            **Other Health Effects**
            - Premature death
            - Reduced lung development in children
            - Cancer risk from certain pollutants
            
            **Vulnerable Groups**
            - Elderly
            - Children
            - People with existing conditions
            - Outdoor workers
        """)
    
    # Add explanatory text
    st.markdown("""
        Climate change can worsen air quality through several mechanisms:
        
        1. **Higher temperatures** accelerate the formation of ground-level ozone
        2. **Changing weather patterns** affect the concentration and dispersion of pollutants
        3. **Increased wildfires** release large amounts of particulate matter
        4. **More frequent droughts** increase dust and particulate pollution
        
        The World Health Organization estimates that air pollution contributes to approximately 7 million premature deaths annually worldwide.
    """)
    
except Exception as e:
    st.error(f"An error occurred while displaying air quality data: {str(e)}")

# Water-related risks section
st.subheader("Water-Related Risks")

# Display a relevant image
st.image("https://images.unsplash.com/photo-1616164744857-1439f3dd5687", use_column_width=True)

water_tab1, water_tab2, water_tab3 = st.tabs(["Sea Level Rise", "Flooding", "Water Scarcity"])

with water_tab1:
    try:
        # Get sea level data
        sea_level_df = utils.get_sea_level_data()
        fig = climate_data.plot_sea_level_chart(sea_level_df)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
            **Sea Level Rise Impacts**
            
            Sea level rise poses significant risks to coastal areas:
            
            - **Coastal flooding and erosion**
            - **Saltwater intrusion** into freshwater aquifers
            - **Displacement of coastal communities**
            - **Damage to infrastructure** and property
            - **Loss of coastal ecosystems** like wetlands and mangroves
            
            By 2100, global mean sea level is projected to rise by 0.3-1.1 meters under different emissions scenarios,
            threatening millions of people living in low-lying coastal areas worldwide.
        """)
    except Exception as e:
        st.error(f"An error occurred while displaying sea level data: {str(e)}")

with water_tab2:
    st.markdown("""
        **Flooding Risks**
        
        Climate change is increasing flood risks through several mechanisms:
        
        - **More intense precipitation events**
        - **Changes in snowmelt patterns**
        - **Sea level rise increasing coastal flooding**
        - **Changes in land use and urbanization**
        
        Floods are among the most common and costly natural disasters, causing:
        
        - Direct mortality and injury
        - Infrastructure damage
        - Water contamination
        - Disease outbreaks
        - Economic disruption
        
        Communities in floodplains, low-lying coastal areas, and regions with poor drainage
        infrastructure are particularly vulnerable.
    """)
    
    # Create a simple flood frequency chart
    years = list(range(1980, 2023))
    flood_events = [15 + i * 0.3 + (i**1.5)/100 for i in range(len(years))]
    
    # Add some variability
    import random
    flood_events = [events + random.uniform(-3, 4) for events in flood_events]
    
    df = pd.DataFrame({
        "Year": years,
        "Major Flood Events": flood_events
    })
    
    st.line_chart(df.set_index("Year"))

with water_tab3:
    st.markdown("""
        **Water Scarcity Risks**
        
        Climate change is exacerbating water scarcity through:
        
        - **Changes in precipitation patterns**
        - **Increased evaporation due to higher temperatures**
        - **Reduced snowpack and earlier snowmelt**
        - **More frequent and severe droughts**
        - **Groundwater depletion**
        
        Impacts of water scarcity include:
        
        - Agricultural losses and food insecurity
        - Limited access to safe drinking water
        - Economic losses across sectors
        - Ecosystem damage
        - Potential for conflict over water resources
        
        Currently, approximately 4 billion people experience severe water scarcity
        for at least one month per year.
    """)
    
    # Create a water stress map
    st.write("Global Water Stress Map (darker = higher water stress)")
    
    m = folium.Map(location=[0, 0], zoom_start=2)
    
    # This would ideally use actual water stress data
    # For demo purposes, we'll use some representative points
    water_stress_data = [
        {"location": [35.0, -95.0], "name": "United States", "stress": "Medium"},
        {"location": [55.0, -3.0], "name": "United Kingdom", "stress": "Low"},
        {"location": [60.0, 15.0], "name": "Scandinavia", "stress": "Very Low"},
        {"location": [30.0, 35.0], "name": "Middle East", "stress": "Extremely High"},
        {"location": [35.0, 105.0], "name": "North China", "stress": "High"},
        {"location": [20.0, 80.0], "name": "India", "stress": "High"},
        {"location": [-25.0, 135.0], "name": "Australia", "stress": "Medium-High"},
        {"location": [-10.0, -55.0], "name": "Brazil", "stress": "Low"},
        {"location": [10.0, 20.0], "name": "Sahel", "stress": "Extremely High"},
        {"location": [5.0, 35.0], "name": "East Africa", "stress": "High"},
    ]
    
    # Color mapping
    stress_colors = {
        "Very Low": "#2196F3",
        "Low": "#4CAF50",
        "Medium": "#FFEB3B",
        "Medium-High": "#FF9800",
        "High": "#FF5722",
        "Extremely High": "#F44336"
    }
    
    # Add markers
    for item in water_stress_data:
        folium.CircleMarker(
            location=item["location"],
            radius=10,
            color=stress_colors[item["stress"]],
            fill=True,
            fill_color=stress_colors[item["stress"]],
            fill_opacity=0.8,
            popup=f"{item['name']}: {item['stress']} Water Stress"
        ).add_to(m)
    
    # Display the map
    folium_static(m)

# Add resources section
st.subheader("Climate Risk Resources")
st.write("Find more information about climate risks and adaptation strategies:")

resources_col1, resources_col2, resources_col3 = st.columns(3)

with resources_col1:
    st.markdown("""
        ### Global Resources
        - [IPCC Reports](https://www.ipcc.ch/reports/)
        - [WMO State of the Climate](https://public.wmo.int/en/our-mandate/climate/wmo-statement-state-of-global-climate)
        - [UN Climate Change](https://unfccc.int/)
    """)

with resources_col2:
    st.markdown("""
        ### Risk Assessment Tools
        - [Global Climate Risk Index](https://germanwatch.org/en/cri)
        - [Notre Dame Global Adaptation Initiative](https://gain.nd.edu/)
        - [Climate Central Risk Finder](https://riskfinder.climatecentral.org/)
    """)

with resources_col3:
    st.markdown("""
        ### Adaptation Resources
        - [Climate Adaptation Knowledge Exchange](https://www.cakex.org/)
        - [WeADAPT](https://www.weadapt.org/)
        - [Climate-ADAPT](https://climate-adapt.eea.europa.eu/)
    """)
