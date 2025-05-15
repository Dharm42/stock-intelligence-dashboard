
import streamlit as st
import requests
import pandas as pd
import numpy as np
import sqlite3
import openai
import yfinance as yf
from datetime import date, timedelta

# --- CONFIG ---
FMP_KEY = st.secrets["api"]["fmp_key"]
FINNHUB_KEY = st.secrets["api"]["finnhub_key"]
IEX_KEY = st.secrets["api"]["iex_key"]
OPENAI_KEY = st.secrets["api"]["openai_key"]
openai.api_key = OPENAI_KEY

# --- CACHING ---
def get_connection():
    return sqlite3.connect("stock_cache.db", check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS cache (
        ticker TEXT PRIMARY KEY,
        fmp_data TEXT,
        finnhub_news TEXT,
        sentiment TEXT,
        bull_bear TEXT
    )""")
    conn.commit()
    conn.close()

init_db()

# --- UI SETUP ---
st.set_page_config(page_title="📈 Stock Intelligence Dashboard", layout="wide")
st.title("📈 Stock Intelligence Dashboard")
company_input = st.text_input("Enter a company name or ticker (US/UK/EU):")

def get_ticker_from_name(name):
    try:
        url = f"https://financialmodelingprep.com/api/v3/search?query={name}&limit=1&apikey={FMP_KEY}"
        res = requests.get(url).json()
        return res[0]['symbol'] if res else name
    except:
        return name

def show_logo(ticker):
    try:
        logo_url = f"https://cloud.iexapis.com/stable/stock/{ticker}/logo?token={IEX_KEY}"
        logo = requests.get(logo_url).json().get('url')
        if logo:
            st.image(logo, width=100)
    except:
        pass

def smart_chart(df, label):
    y_data = df.dropna()
    if y_data.empty: return
    min_val = y_data.min().min()
    max_val = y_data.max().max()
    st.line_chart(y_data, use_container_width=True)

if company_input:
    ticker = get_ticker_from_name(company_input)
    st.subheader(f"Data for: `{ticker}`")
    show_logo(ticker)

    # HISTORICAL CHART
    stock = yf.Ticker(ticker)
    hist = stock.history(period="5y")
    for ma in [7, 28, 50, 100, 200]:
        hist[f"MA_{ma}"] = hist["Close"].rolling(ma).mean()

    st.subheader("📊 Price Trend with Moving Averages")
    for ma in [7, 50, 100, 200]:
        st.write(f"### {ma}-Day Moving Average")
        smart_chart(hist[["Close", f"MA_{ma}"]], f"{ma}-Day MA")

    # INCOME STATEMENT
    st.subheader("💵 5-Year Income Statement")
    try:
        inc_url = f"https://financialmodelingprep.com/api/v3/income-statement/{ticker}?limit=5&apikey={FMP_KEY}"
        inc_data = requests.get(inc_url).json()
        if isinstance(inc_data, list):
            df_inc = pd.DataFrame(inc_data).set_index("date")[["revenue", "ebitda", "netIncome"]]
            st.dataframe(df_inc)
    except Exception as e:
        st.warning(f"Could not load income statement: {e}")

    # NEWS
    st.subheader("📰 Latest News Headlines")
    today = date.today()
    last_year = today - timedelta(days=365)
    try:
        news_url = f"https://finnhub.io/api/v1/company-news?symbol={ticker}&from={last_year}&to={today}&token={FINNHUB_KEY}"
        news_data = requests.get(news_url).json()
        if news_data:
            for article in news_data[:5]:
                st.markdown(f"- [{article['headline']}]({article['url']})")
        else:
            st.info("No recent news found.")
    except Exception as e:
        st.warning(f"Could not fetch news: {e}")

    # SENTIMENT
    st.subheader("📈 Market Sentiment")
    try:
        sent_url = f"https://finnhub.io/api/v1/news-sentiment?symbol={ticker}&token={FINNHUB_KEY}"
        sentiment = requests.get(sent_url).json()
        st.write(sentiment.get('sentiment', 'No sentiment data found'))
    except Exception as e:
        st.warning(f"Could not fetch sentiment: {e}")

    # BULL/BEAR CASE GPT
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
        st.warning(f"GPT analysis error: {e}")
