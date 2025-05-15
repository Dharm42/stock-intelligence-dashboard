
# Stock Intelligence Dashboard (Debugged)

## How to Run

1. **Create `secrets.toml` in `.streamlit` folder** (same level as app)

```
[api]
fmp_key = "your_fmp_api_key"
finnhub_key = "your_finnhub_api_key"
iex_key = "your_iex_cloud_key"
openai_key = "your_openai_api_key"
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Run the app:
```
streamlit run stock_dashboard_app.py
```

You can deploy this on [Streamlit Cloud](https://streamlit.io/cloud) using the same structure.
