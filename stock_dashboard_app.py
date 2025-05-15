
import streamlit as st
import requests
import pandas as pd
import numpy as np
import sqlite3
import openai
import yfinance as yf

# Load your API keys here
FMP_KEY = "your_fmp_api_key"
FINNHUB_KEY = "your_finnhub_api_key"
IEX_KEY = "your_iex_cloud_key"
OPENAI_KEY = "your_openai_api_key"
openai.api_key = OPENAI_KEY

# SQLite caching setup
conn = sqlite3.connect("stock_cache.db")
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS cache (
    ticker TEXT PRIMARY KEY,
    fmp_data TEXT,
    finnhub_news TEXT,
    sentiment TEXT,
    bull_bear TEXT
)""")
conn.commit()

st.set_page_config(page_title="📈 Stock Intelligence Dashboard", layout="wide")

st.title("📈 Stock Intelligence Dashboard")
company_input = st.text_input("Enter a company name or ticker (US/UK/EU):")

def get_ticker_from_name(name):
    url = f"https://financialmodelingprep.com/api/v3/search?query={name}&limit=1&apikey={FMP_KEY}"
    res = requests.get(url).json()
    return res[0]['symbol'] if res else name

if company_input:
    ticker = get_ticker_from_name(company_input)
    st.subheader(f"Data for: `{ticker}`")

    # Show logo
    try:
        logo_url = f"https://cloud.iexapis.com/stable/stock/{ticker}/logo?token={IEX_KEY}"
        logo = requests.get(logo_url).json().get('url', None)
        if logo:
            st.image(logo, width=100)
    except:
        pass

    # Get historical data
    stock = yf.Ticker(ticker)
    hist = stock.history(period="5y")
    for ma in [7, 28, 50, 100, 200]:
        hist[f"MA_{ma}"] = hist["Close"].rolling(ma).mean()

    # Smart charting
    st.subheader("📊 Price Trend with Moving Averages")
    for ma in [7, 50, 100, 200]:
        y = hist[["Close", f"MA_{ma}"]].dropna()
        min_val = y.min().min()
        max_val = y.max().max()
        y_range = [min_val * 0.9, max_val * 1.1]
        st.write(f"### {ma}-Day Moving Average")
        st.line_chart(y)

    # Pull income statement from FMP
    st.subheader("💵 5-Year Income Statement")
    inc_url = f"https://financialmodelingprep.com/api/v3/income-statement/{ticker}?limit=5&apikey={FMP_KEY}"
    inc_data = requests.get(inc_url).json()
    if isinstance(inc_data, list):
        df_inc = pd.DataFrame(inc_data).set_index("date")[["revenue", "ebitda", "netIncome"]]
        st.dataframe(df_inc)

    # News headlines
    st.subheader("📰 Latest News Headlines")
    news_url = f"https://finnhub.io/api/v1/company-news?symbol={ticker}&from=2024-01-01&to=2025-01-01&token={FINNHUB_KEY}"
    news_data = requests.get(news_url).json()
    for article in news_data[:5]:
        st.markdown(f"- [{article['headline']}]({article['url']})")

    # Sentiment
    st.subheader("📈 Market Sentiment")
    sent_url = f"https://finnhub.io/api/v1/news-sentiment?symbol={ticker}&token={FINNHUB_KEY}"
    sentiment = requests.get(sent_url).json()
    st.write(sentiment.get('sentiment', 'No sentiment data found'))

    # Bull & Bear Case from GPT
    st.subheader("🧠 Bull & Bear Drivers (12 Months)")
    try:
        gpt_prompt = f"What are the main bull and bear case drivers for {ticker} stock over the next 12 months?"
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": gpt_prompt}]
        )
        bull_bear = response['choices'][0]['message']['content']
        st.markdown(bull_bear)
    except Exception as e:
        st.warning(f"Could not fetch GPT analysis: {e}")
