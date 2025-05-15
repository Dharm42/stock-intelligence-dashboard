
import streamlit as st
import requests
import pandas as pd
import numpy as np
import openai
import yfinance as yf
from datetime import date, timedelta

# CONFIG
FMP_KEY = st.secrets["api"]["fmp_key"]
FINNHUB_KEY = st.secrets["api"]["finnhub_key"]
IEX_KEY = st.secrets["api"]["iex_key"]
OPENAI_KEY = st.secrets["api"]["openai_key"]
openai.api_key = OPENAI_KEY

# PAGE SETUP
st.set_page_config(page_title="📈 Stock Intelligence Dashboard", layout="wide")
st.markdown("## 📊 Stock Intelligence Dashboard")
st.markdown("Enter a stock name or ticker from **US, UK, or EU markets** to begin.")

# SMART TICKER LOOKUP
def get_ticker_from_name(name):
    try:
        url = f"https://financialmodelingprep.com/api/v3/search?query={name}&limit=1&apikey={FMP_KEY}"
        res = requests.get(url).json()
        return res[0]['symbol'] if res else name
    except:
        return name

def show_logo_and_meta(ticker):
    cols = st.columns([1, 3])
    with cols[0]:
        try:
            logo_url = f"https://cloud.iexapis.com/stable/stock/{ticker}/logo?token={IEX_KEY}"
            logo = requests.get(logo_url).json().get('url')
            if logo:
                st.image(logo, width=100)
        except:
            st.write("No logo found.")
    with cols[1]:
        stock = yf.Ticker(ticker)
        info = stock.info
        st.markdown(f"### {info.get('longName', ticker)}")
        st.markdown(f"**Sector**: {info.get('sector', 'N/A')}  
**Industry**: {info.get('industry', 'N/A')}")
        st.markdown(f"**Current Price**: ${info.get('currentPrice', 'N/A')}")
        st.markdown(f"**52-Week High**: ${info.get('fiftyTwoWeekHigh', 'N/A')}  
**52-Week Low**: ${info.get('fiftyTwoWeekLow', 'N/A')}")

# CHART VISUALIZATION
def show_moving_averages(ticker):
    st.markdown("### 📉 Price Chart with Moving Averages")
    stock = yf.Ticker(ticker)
    hist = stock.history(period="5y")
    for ma in [7, 28, 50, 100, 200]:
        hist[f"MA_{ma}"] = hist["Close"].rolling(ma).mean()
    for ma in [7, 50, 100, 200]:
        st.markdown(f"**{ma}-Day MA Chart**")
        y_data = hist[["Close", f"MA_{ma}"]].dropna()
        if not y_data.empty:
            st.line_chart(y_data)

# INCOME STATEMENT
def show_income_statement(ticker):
    st.markdown("### 💵 5-Year Income Statement (via FMP)")
    url = f"https://financialmodelingprep.com/api/v3/income-statement/{ticker}?limit=5&apikey={FMP_KEY}"
    data = requests.get(url).json()
    if isinstance(data, list):
        df = pd.DataFrame(data).set_index("date")[["revenue", "ebitda", "netIncome"]]
        st.dataframe(df)

# NEWS AND SENTIMENT
def show_news_and_sentiment(ticker):
    st.markdown("### 📰 Latest News (via Finnhub)")
    today = date.today()
    last_year = today - timedelta(days=365)
    news_url = f"https://finnhub.io/api/v1/company-news?symbol={ticker}&from={last_year}&to={today}&token={FINNHUB_KEY}"
    news = requests.get(news_url).json()
    if news:
        for article in news[:5]:
            st.markdown(f"- [{article['headline']}]({article['url']})")
    else:
        st.info("No news available.")

    st.markdown("### 📈 Market Sentiment")
    sent_url = f"https://finnhub.io/api/v1/news-sentiment?symbol={ticker}&token={FINNHUB_KEY}"
    sentiment = requests.get(sent_url).json()
    if 'sentiment' in sentiment:
        st.json(sentiment['sentiment'])

# GPT BULL/BEAR INSIGHT
def show_gpt_insight(ticker):
    st.markdown("### 🧠 Bull & Bear Drivers (GPT Analysis)")
    prompt = f"What are the main bull and bear case drivers for {ticker} stock over the next 12 months?"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        content = response['choices'][0]['message']['content']
        st.markdown(content)
    except Exception as e:
        st.error(f"GPT Error: {e}")

# MAIN
company_input = st.text_input("🔎 Search by company name or ticker:")
if company_input:
    ticker = get_ticker_from_name(company_input)
    show_logo_and_meta(ticker)

    with st.container():
        col1, col2 = st.columns([2, 1])
        with col1:
            show_moving_averages(ticker)
        with col2:
            show_news_and_sentiment(ticker)

    st.divider()
    show_income_statement(ticker)
    st.divider()
    show_gpt_insight(ticker)
