import streamlit as st
import utils
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Climate News | Climate Insights",
    page_icon="📰",
    layout="wide"
)

# Initialize session state variables if they don't exist
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'
    
if 'location' not in st.session_state:
    st.session_state.location = "London"
    
if 'news_next_page' not in st.session_state:
    st.session_state.news_next_page = None

# Page header
st.title("Climate News")
st.write("Stay informed with the latest news and articles about climate change from around the world.")

# Sidebar components for news filtering
with st.sidebar:
    st.title("Climate Insights")
    
    # Dark/light mode toggle
    theme_toggle = st.toggle("Dark Mode", value=True if st.session_state.theme == 'dark' else False)
    if theme_toggle:
        st.session_state.theme = 'dark'
    else:
        st.session_state.theme = 'light'
    
    # News filters
    st.subheader("Filter News")
    news_categories = ["All", "Policy", "Science", "Technology", "Economics", "Impacts"]
    selected_category = st.selectbox("Category", news_categories)
    
    date_options = ["Any time", "Past 24 hours", "Past week", "Past month"]
    selected_date = st.selectbox("Timeframe", date_options)
    
    # Navigation
    st.subheader("Navigation")
    st.page_link("app.py", label="Home", icon="🏠")
    st.page_link("pages/news.py", label="Climate News", icon="📰")
    st.page_link("pages/weather.py", label="Weather", icon="🌤️")
    st.page_link("pages/climate_analysis.py", label="Climate Analysis", icon="📊")
    st.page_link("pages/climate_risk.py", label="Climate Risk Factors", icon="⚠️")
    
    st.divider()
    st.caption("© 2023 Climate Insights")

# News content area
try:
    # Fetch news with pagination
    articles, next_page, total_results = utils.fetch_climate_news(
        next_page=st.session_state.news_next_page
    )
    
    if total_results > 0:
        st.write(f"Found {total_results} articles about climate change")
    
    # Display articles
    for article in articles:
        with st.container():
            # Article title with link
            title = article.get('title', 'No title available')
            link = article.get('link', '#')
            st.markdown(f"### [{title}]({link})")
            
            # Article metadata
            col1, col2 = st.columns([3, 1])
            with col1:
                source = article.get('source_id', 'Unknown source')
                date = article.get('pubDate', 'Unknown date')
                st.caption(f"Source: {source} | Published: {date}")
            
            # Article description
            description = article.get('description', 'No description available')
            st.write(description)
            
            # Keywords/categories if available
            keywords = article.get('keywords', [])
            if keywords:
                st.caption(f"Keywords: {', '.join(keywords)}")
            
            st.divider()

    # Pagination controls
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        if next_page:
            if st.button("Load More Articles"):
                st.session_state.news_next_page = next_page
                st.rerun()
        else:
            st.write("No more articles available")

    # Reset pagination button
    with col3:
        if st.session_state.news_next_page:
            if st.button("Back to First Page"):
                st.session_state.news_next_page = None
                st.rerun()

except Exception as e:
    st.error(f"An error occurred while fetching news: {str(e)}")
    st.write("Please try again later or check your internet connection.")
