from setuptools import setup, find_packages

setup(
    name="climate-intelligence",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.12.3",
    install_requires=[
        "requests>=2.31.0",
        "pandas>=2.2.0",
        "streamlit>=1.32.0",
        "plotly>=5.19.0",
        "python-dotenv>=1.0.1",
        "folium>=0.15.1",
        "streamlit-folium>=0.18.0",
        "numpy>=1.26.4",
        "matplotlib>=3.8.3",
        "seaborn>=0.13.2",
        "altair>=5.2.0",
        "geopy>=2.4.1",
        "scikit-learn>=1.4.1.post1"
    ],
) 