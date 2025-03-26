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
    
if 'news_page' not in st.session_state:
    st.session_state.news_page = 1

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
    # Initialize pagination
    if 'news_page' not in st.session_state:
        st.session_state.news_page = 1
    
    # Fetch news
    news_articles = utils.fetch_climate_news(page=st.session_state.news_page)
    
    if not news_articles:
        st.warning("No news articles found. Please try again later.")
    else:
        st.write(f"Showing {len(news_articles)} results")
        
        # Display news articles in a grid
        for i in range(0, len(news_articles), 2):
            col1, col2 = st.columns(2)
            
            # First article in the row
            with col1:
                if i < len(news_articles):
                    article = news_articles[i]
                    
                    # Article card with image
                    with st.container():
                        st.subheader(article.get('title', 'No title available'))
                        
                        # Display publication info
                        source = article.get('source_id', 'Unknown source')
                        pub_date = article.get('pubDate', 'Unknown date')
                        st.caption(f"{source} • {pub_date}")
                        
                        # Article image if available
                        if article.get('image_url'):
                            st.image(article['image_url'], use_container_width=True)
                        else:
                            # Use a stock image if no image available
                            st.image("https://images.unsplash.com/photo-1460925895917-afdab827c52f", use_container_width=True)
                        
                        # Article description
                        description = article.get('description', 'No description available')
                        if description:
                            # Limit to a reasonable length
                            if len(description) > 200:
                                description = description[:200] + "..."
                            st.write(description)
                        
                        # Link to full article
                        if article.get('link'):
                            st.markdown(f"[Read full article]({article['link']})")
                    
                    st.divider()
            
            # Second article in the row
            with col2:
                if i + 1 < len(news_articles):
                    article = news_articles[i + 1]
                    
                    # Article card with image
                    with st.container():
                        st.subheader(article.get('title', 'No title available'))
                        
                        # Display publication info
                        source = article.get('source_id', 'Unknown source')
                        pub_date = article.get('pubDate', 'Unknown date')
                        st.caption(f"{source} • {pub_date}")
                        
                        # Article image if available
                        if article.get('image_url'):
                            st.image(article['image_url'], use_container_width=True)
                        else:
                            # Use a stock image if no image available
                            st.image("https://images.unsplash.com/photo-1542744173-05336fcc7ad4", use_container_width=True)
                        
                        # Article description
                        description = article.get('description', 'No description available')
                        if description:
                            # Limit to a reasonable length
                            if len(description) > 200:
                                description = description[:200] + "..."
                            st.write(description)
                        
                        # Link to full article
                        if article.get('link'):
                            st.markdown(f"[Read full article]({article['link']})")
                    
                    st.divider()
        
        # Pagination controls
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col1:
            if st.session_state.news_page > 1:
                if st.button("← Previous"):
                    st.session_state.news_page -= 1
                    st.rerun()
        
        with col2:
            st.write(f"Page {st.session_state.news_page}")
        
        with col3:
            if len(news_articles) >= 10:  # Assuming we have more pages
                if st.button("Next →"):
                    st.session_state.news_page += 1
                    st.rerun()

except Exception as e:
    st.error(f"An error occurred while fetching news: {str(e)}")
    st.write("Please try again later or check your internet connection.")
