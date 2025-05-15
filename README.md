
# Streamlit Stock Intelligence Dashboard (v2)

## Features
- Smart ticker detection from company name (US/UK/EU)
- 5-year income statements via Financial Modeling Prep
- Real-time news & sentiment from Finnhub
- Company logo display via IEX Cloud
- Bull & Bear drivers generated using GPT-4
- SQLite caching to reduce API calls
- Autoscaled graphs with moving averages

## Setup Instructions
1. Add your API keys in `stock_dashboard_app.py`:
   - `FMP_KEY`, `FINNHUB_KEY`, `IEX_KEY`, `OPENAI_KEY`
2. Install Python & dependencies:
```bash
pip install -r requirements.txt
```
3. Run the app:
```bash
streamlit run stock_dashboard_app.py
```

Deploy it via [Streamlit Cloud](https://streamlit.io/cloud).
