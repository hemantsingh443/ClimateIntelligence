# Climate Intelligence Dashboard

A comprehensive climate monitoring and analysis dashboard that provides real-time climate data, risk assessments, and environmental insights.

## Features

- Real-time climate data visualization
- Air quality monitoring
- Weather forecasting
- Climate risk assessment
- Historical climate trends
- News integration for climate-related updates

## APIs Integrated

- OpenWeather API - Weather data and forecasts
- World Bank Climate Data API - Historical climate indicators
- NewsData API - Climate-related news
- OpenAQ API - Air quality data
- NASA GISS - Temperature data
- NOAA - Climate data

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ClimateIntelligence.git
cd ClimateIntelligence
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with your API keys:
```
NEWSDATA_API_KEY=your_newsdata_api_key
OPENWEATHER_API_KEY=your_openweather_api_key
NOAA_API_TOKEN=your_noaa_api_token
```

## Usage

Run the Streamlit app:
```bash
streamlit run app.py
```

The dashboard will be available at `http://localhost:8501`

## Project Structure

```
ClimateIntelligence/
├── app.py                  # Main Streamlit application
├── api_integrations.py     # API integration classes
├── utils.py               # Utility functions
├── pages/                 # Streamlit pages
│   ├── climate_data.py    # Climate data visualization
│   ├── climate_risk.py    # Risk assessment
│   ├── climate_analysis.py # Trend analysis
│   └── news.py           # Climate news
├── requirements.txt       # Project dependencies
└── README.md             # Project documentation
```

## Data Sources

- Global temperature data: NASA GISS Surface Temperature Analysis
- CO2 concentration: NOAA Global Monitoring Laboratory
- Sea level data: CSIRO and NASA Satellite Altimetry
- Climate events: EM-DAT and NOAA Billion-Dollar Weather and Climate Disasters
- Air quality: OpenAQ and WHO Global Ambient Air Quality Database

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/improvement`)
3. Make changes and commit (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/improvement`)
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- World Bank for climate data
- OpenWeather for weather data
- NewsData for news integration
- OpenAQ for air quality data
- NASA and NOAA for climate indicators 