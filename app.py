import streamlit as st
import os
from datetime import datetime
import utils
import shutil

# Page configuration
st.set_page_config(
    page_title="Climate Insights",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

# Initialize session state variables if they don't exist
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'
    
if 'location' not in st.session_state:
    st.session_state.location = "London"

def switch_theme(theme):
    """Switch between light and dark themes by copying the appropriate config file."""
    if theme == 'dark':
        shutil.copy('.streamlit/config_dark.toml', '.streamlit/config.toml')
    else:
        shutil.copy('.streamlit/config_light.toml', '.streamlit/config.toml')

# Sidebar
with st.sidebar:
    st.title("Climate Insights")
    
    # Dark/light mode toggle
    st.write("Theme changes require page refresh")
    col1, col2 = st.columns([3, 1])
    with col1:
        theme_toggle = st.toggle("Dark Mode", value=True if st.session_state.theme == 'dark' else False)
    with col2:
        if st.button("↻", help="Refresh page to apply theme"):
            st.rerun()
    if theme_toggle:
        if st.session_state.theme != 'dark':
            st.session_state.theme = 'dark'
            switch_theme('dark')
    else:
        if st.session_state.theme != 'light':
            st.session_state.theme = 'light'
            switch_theme('light')
    
    # Location input
    st.subheader("Search Location")
    location = st.text_input("Enter location", value=st.session_state.location)
    if location != st.session_state.location:
        st.session_state.location = location
    
    # Navigation
    st.subheader("Navigation")
    pages = {
        "🏠 Home": "app.py",
        "📰 Climate News": "pages/news.py",
        "🌤️ Weather": "pages/weather.py",
        "📊 Climate Analysis": "pages/climate_analysis.py",
        "⚠️ Climate Risk Factors": "pages/climate_risk.py"
    }
    
    for page_name, page_path in pages.items():
        if st.button(page_name, use_container_width=True):
            st.switch_page(page_path)
    
    st.divider()
    st.caption("© 2023 Climate Insights")

# Main content
st.title("Climate Insights")
st.subheader("Tracking Our Changing Planet")

# Overview section
col1, col2 = st.columns([2, 1])

with col1:
    st.write("""
    Welcome to Climate Insights, your comprehensive platform for staying informed about 
    climate change, weather patterns, and environmental analytics. Explore news, weather data, 
    and visual insights about our changing planet.
    """)
    
    # Featured cards
    st.subheader("Quick Access")
    
    card1, card2, card3 = st.columns(3)
    
    with card1:
        st.image("https://images.unsplash.com/photo-1493243350443-9e3048ce7288", use_container_width=True)
        st.markdown("### Latest News")
        st.write("Get updated with the latest climate news from around the world.")
        if st.button("Read News", key="news_btn"):
            st.switch_page("pages/news.py")
        
    with card2:
        st.image("https://images.unsplash.com/photo-1535025075092-5a1cf795130b", use_container_width=True)
        st.markdown("### Weather Details")
        st.write(f"Current weather for {st.session_state.location} and forecast.")
        if st.button("Check Weather", key="weather_btn"):
            st.switch_page("pages/weather.py")
        
    with card3:
        st.image("https://images.unsplash.com/photo-1551288049-bebda4e38f71", use_container_width=True)
        st.markdown("### Climate Analysis")
        st.write("Visualizations to understand climate trends and patterns.")
        if st.button("View Analysis", key="analysis_btn"):
            st.switch_page("pages/climate_analysis.py")

with col2:
    # Current date and time
    now = datetime.now()
    st.markdown(f"### {now.strftime('%A, %B %d, %Y')}")
    
    # Key stats
    st.markdown("### Global Climate Indicators")
    
    try:
        global_temp, co2_level, sea_level = utils.get_climate_indicators()
        
        st.metric("Global Temperature Anomaly", f"{global_temp}°C", "+0.02°C")
        st.metric("Atmospheric CO₂", f"{co2_level} ppm", "+2.5 ppm")
        st.metric("Sea Level Rise", f"{sea_level} mm/year", "+0.1 mm")
    except Exception as e:
        st.error(f"Unable to fetch climate indicators: {str(e)}")
        st.metric("Global Temperature Anomaly", "Loading...", "")
        st.metric("Atmospheric CO₂", "Loading...", "")
        st.metric("Sea Level Rise", "Loading...", "")

# Featured climate impacts section
st.subheader("Climate Change Impacts")
impacts_col1, impacts_col2, impacts_col3 = st.columns(3)

with impacts_col1:
    st.image("https://images.unsplash.com/photo-1499244571948-7ccddb3583f1", use_container_width=True)
    st.markdown("#### Rising Sea Levels")
    st.write("Coastal communities face increasing challenges from rising seas.")

with impacts_col2:
    st.image("https://images.unsplash.com/photo-1562155955-1cb2d73488d7", use_container_width=True)
    st.markdown("#### Extreme Weather")
    st.write("More frequent and intense storms, floods, and droughts.")

with impacts_col3:
    st.image("https://images.unsplash.com/photo-1561553590-267fc716698a", use_container_width=True)
    st.markdown("#### Biodiversity Loss")
    st.write("Ecosystems struggle to adapt to rapid climate changes.")

# Call to action
st.divider()
st.markdown("### Start Exploring Climate Data")
st.write("Navigate to different sections using the sidebar to explore more insights.")
