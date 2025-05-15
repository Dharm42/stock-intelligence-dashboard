
# Streamlit Stock Intelligence Dashboard (Final Version)

## Setup Instructions

1. Add your API keys in a `.streamlit/secrets.toml` file like this:
```
[api]
fmp_key = "your_fmp_api_key"
finnhub_key = "your_finnhub_api_key"
iex_key = "your_iex_cloud_key"
openai_key = "your_openai_api_key"
```

2. Install requirements:
```
pip install -r requirements.txt
```

3. Run the app:
```
streamlit run stock_dashboard_app.py
```

## Notes
- SQLite is removed for Streamlit Cloud compatibility.
- Designed for deployment at https://streamlit.io/cloud.
