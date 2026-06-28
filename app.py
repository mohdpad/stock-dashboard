import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import requests
from datetime import datetime, timedelta
from streamlit_searchbox import st_searchbox

# ============================================================
# CACHED DATA FUNCTIONS
# ============================================================

@st.cache_data(ttl=60)
def get_live_price(ticker):
    return yf.Ticker(ticker).history(period="2d")

@st.cache_data(ttl=300)
def get_stock_history(ticker, period, interval):
    return yf.Ticker(ticker).history(period=period, interval=interval)

@st.cache_data(ttl=3600)
def get_stock_info(ticker):
    return yf.Ticker(ticker).info

@st.cache_data(ttl=1800)
def get_finnhub_news(ticker, start, end, token):
    url = f"https://finnhub.io/api/v1/company-news?symbol={ticker}&from={start}&to={end}&token={token}"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200 and isinstance(r.json(), list):
            return r.json()[:5]
    except Exception as e:
        st.warning(f"News fetch error: {e}")
    return []

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(page_title="Pro Stock Dashboard", layout="wide")

# ── THEME STATE — must be initialized before anything else ───
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

if "selected_stocks" not in st.session_state:
    st.session_state.selected_stocks = []

# ── THEME CSS ────────────────────────────────────────────────
if st.session_state.dark_mode:
    st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .stMainBlockContainer { background-color: #0e1117; color: #ffffff; }
    section[data-testid="stSidebar"] { background-color: #1e2530; }
    .stMetric { background-color: #1e2530 !important; border-radius: 8px; padding: 12px; }
    [data-testid="stMetricValue"] { color: #ffffff !important; }
    [data-testid="stMetricLabel"] { color: #ffffff !important; }
    [data-baseweb="checkbox"] div[role="switch"][aria-checked="true"] {
        background-color: #1E88E5 !important;
        border-color: #1E88E5 !important;
    }
    [data-baseweb="checkbox"] div[role="switch"][aria-checked="false"] {
        background-color: #888888 !important;
        border-color: #888888 !important;
    }
    /* Theme toggle button */
    button[data-testid="baseButton-secondary"] {
        background-color: #1E88E5 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 20px !important;
        font-size: 13px !important;
    }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    .stMainBlockContainer { background-color: #ffffff; color: #000000; }
    section[data-testid="stSidebar"] { background-color: #f0f2f6; }
    section[data-testid="stSidebar"] * { color: #000000 !important; }
    section[data-testid="stSidebar"] .stButton button {
        background-color: #e0e0e0 !important;
        color: #000000 !important;
    }
    .stMetric { background-color: #f0f2f6 !important; border-radius: 8px; padding: 12px; }
    [data-testid="stMetricValue"] { color: #000000 !important; }
    [data-testid="stMetricLabel"] { color: #000000 !important; }
    .stRadio label, .stRadio span, .stRadio p, .stRadio div { color: #000000 !important; }
    [role="radiogroup"] label, [role="radiogroup"] span { color: #000000 !important; }
    [data-testid="stWidgetLabel"] p { color: #000000 !important; }
    [data-baseweb="radio"] label, [data-baseweb="radio"] span { color: #000000 !important; }
    .stToggle label, .stToggle p, .stToggle span { color: #000000 !important; }
    [data-testid="stToggle"] > label { color: #000000 !important; }
    [data-baseweb="checkbox"] div[role="switch"][aria-checked="true"] {
        background-color: #1E88E5 !important;
        border-color: #1E88E5 !important;
    }
    /* Theme toggle button */
    button[data-testid="baseButton-secondary"] {
        background-color: #1E88E5 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 20px !important;
        font-size: 13px !important;
    }
    [data-baseweb="checkbox"] div[role="switch"][aria-checked="false"] {
        background-color: #888888 !important;
        border-color: #888888 !important;
    }
    p, h1, h2, h3, h4, label { color: #000000 !important; }
    [data-testid="stExpander"] { background-color: #f0f2f6 !important; }
    [data-testid="stExpander"] summary { background-color: #e0e4ea !important; color: #000000 !important; }
    [data-testid="stExpander"] summary span { color: #000000 !important; }
    [data-testid="stExpander"] div { background-color: #f0f2f6 !important; color: #000000 !important; }
    details { background-color: #f0f2f6 !important; }
    details summary { color: #000000 !important; }
    </style>
    """, unsafe_allow_html=True)

# ── FOOTER CSS ───────────────────────────────────────────────
footer_bg = "#0e1117" if st.session_state.dark_mode else "#f0f2f6"
footer_border = "#2e3a4a" if st.session_state.dark_mode else "#d0d4da"
st.markdown(f"""
<style>
.custom-footer {{
    position: fixed;
    bottom: 0; left: 0;
    width: 100%;
    text-align: center;
    padding: 6px 0px;
    color: #888888;
    font-size: 14px;
    font-family: 'Source Sans Pro', sans-serif;
    background-color: {footer_bg};
    border-top: 1px solid {footer_border};
    z-index: 999;
}}
</style>
""", unsafe_allow_html=True)

# ── PLOTLY THEME ─────────────────────────────────────────────
plotly_template = "plotly_dark" if st.session_state.dark_mode else "plotly_white"
plotly_paper_bg = "#1e2530" if st.session_state.dark_mode else "#f0f2f6"
plotly_font_color = "#ffffff" if st.session_state.dark_mode else "#000000"
plotly_grid_color = "#2e3a4a" if st.session_state.dark_mode else "#d0d4da"

# ── TITLE + TOGGLE ROW ───────────────────────────────────────
col_title, col_toggle = st.columns([9, 1])
with col_title:
    st.title("📈 Real-Time & Historical Stock Dashboard")
with col_toggle:
    st.write("")
    label = "☀️ Light Mode" if st.session_state.dark_mode else "🌙 Dark Mode"
    btn_color = "#1E88E5"
    st.markdown(f"""
        <style>
        div[data-testid="stBaseButton-secondary"] button,
        div[data-testid="stBaseButton-secondary"] button:hover,
        .stButton button, .stButton button:hover {{
            background-color: {btn_color} !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 20px !important;
            font-size: 13px !important;
            width: 100% !important;
        }}
        </style>
    """, unsafe_allow_html=True)
    if st.button(label, key="theme_toggle", use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.subheader("🔍 Search & Compare Companies")

def search_yahoo_finance(search_query: str):
    if not search_query or len(search_query) < 2:
        return []
    search_url = f"https://query2.finance.yahoo.com/v1/finance/search?q={search_query}&quotesCount=6&newsCount=0"
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(search_url, headers=headers, timeout=3)
        if response.status_code == 200:
            valid_matches = [
                item for item in response.json().get("quotes", [])
                if item.get("quoteType") in ["EQUITY", "INDEX"]
            ]
            return [
                (f"🏢 {item.get('shortname', 'Unknown')} ({item.get('symbol')})", item.get("symbol"))
                for item in valid_matches
            ]
    except Exception:
        return []
    return []

with st.sidebar:
    selected_ticker = st_searchbox(
        search_function=search_yahoo_finance,
        placeholder="Type Company Name or Ticker...",
        key="ticker_searchbox"
    )

if selected_ticker and selected_ticker not in st.session_state.selected_stocks:
    st.session_state.selected_stocks.append(selected_ticker)

if st.session_state.selected_stocks:
    st.sidebar.markdown("**Comparing Companies:**")
    for idx, ticker in enumerate(st.session_state.selected_stocks):
        if st.sidebar.button(f"❌ {ticker}", key=f"del_{ticker}_{idx}"):
            st.session_state.selected_stocks.remove(ticker)
            st.rerun()

selected_stocks = st.session_state.selected_stocks

# ============================================================
# MAIN DASHBOARD
# ============================================================

if not selected_stocks:
    st.info("💡 Please select or type a company name in the sidebar to display dashboard metrics.")
else:

    # ── FEATURE 1: LIVE PRICE METRICS ───────────────────────
    st.subheader("Current Market Price")
    cols = st.columns(len(selected_stocks))

    for i, ticker in enumerate(selected_stocks):
        with cols[i]:
            todays_data = get_live_price(ticker)
            if not todays_data.empty:
                current_price = todays_data['Close'].iloc[-1]
                previous_close = todays_data['Close'].iloc[0] if len(todays_data) > 1 else current_price
                price_change = current_price - previous_close
                pct_change = (price_change / previous_close) * 100
                st.metric(
                    label=ticker,
                    value=f"${current_price:,.2f} USD",
                    delta=f"{price_change:+.2f} ({pct_change:+.2f}%)"
                )

    # ── FEATURE 2: PRICE HISTORY CHART ──────────────────────
    st.markdown("---")
    st.subheader("Price History")

    time_tabs = st.radio(
        "Select a Time Range:",
        options=["1 Day", "1 Week", "1 Month", "1 Year"],
        index=2,
        horizontal=True
    )

    if time_tabs == "1 Day":
        chart_period, chart_interval = "1d", "1m"
    elif time_tabs == "1 Week":
        chart_period, chart_interval = "5d", "15m"
    elif time_tabs == "1 Month":
        chart_period, chart_interval = "1mo", "1d"
    else:
        chart_period, chart_interval = "1y", "1wk"

    fig = go.Figure()

    for ticker in selected_stocks:
        data = get_stock_history(ticker, chart_period, chart_interval)
        if not data.empty:
            if len(selected_stocks) == 1:
                fig.add_trace(go.Candlestick(
                    x=data.index,
                    open=data['Open'],
                    high=data['High'],
                    low=data['Low'],
                    close=data['Close'],
                    name=ticker
                ))
            else:
                normalized = (data['Close'] / data['Close'].iloc[0] - 1) * 100
                fig.add_trace(go.Scatter(
                    x=data.index,
                    y=normalized,
                    name=ticker,
                    mode='lines'
                ))

    fig.update_layout(
        template=plotly_template,
        paper_bgcolor=plotly_paper_bg,
        plot_bgcolor=plotly_paper_bg,
        font_color=plotly_font_color,
        xaxis=dict(gridcolor=plotly_grid_color),
        yaxis=dict(gridcolor=plotly_grid_color),
        xaxis_title="Time / Date",
        yaxis_title="Price (USD)" if len(selected_stocks) == 1 else "% Change from Start",
        xaxis_rangeslider_visible=False,
        hovermode="x unified",
        margin=dict(l=20, r=20, t=20, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    st.plotly_chart(fig, use_container_width=True)

    # ── FEATURE 3: COMPANY STATISTICS ───────────────────────
    st.markdown("---")
    st.subheader("📊 Company Statistics")

    for ticker in selected_stocks:
        info = get_stock_info(ticker)
        with st.expander(f"View Valuation & Data Metrics for {ticker}", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("52-Week High", f"${info.get('fiftyTwoWeekHigh', 0):,.2f}")
                st.metric("Forward P/E Ratio", f"{info.get('forwardPE', 'N/A')}")
            with col2:
                st.metric("52-Week Low", f"${info.get('fiftyTwoWeekLow', 0):,.2f}")
                cap = info.get('marketCap', 0)
                cap_str = f"${cap / 1e9:.2f}B" if cap >= 1e9 else f"${cap / 1e6:.2f}M"
                st.metric("Market Cap", cap_str)
            with col3:
                st.metric("Analyst Target Mean", f"${info.get('targetMeanPrice', 0):,.2f}")
                st.metric("Dividend Yield", f"{info.get('dividendYield', 0) * 100:.2f}%" if info.get('dividendYield') else "0.00%")

    # ── FEATURE 4: FINNHUB NEWS ──────────────────────────────
    st.markdown("---")
    st.subheader("📰 Latest Market News")

    end_date_str = datetime.today().strftime('%Y-%m-%d')
    start_date_str = (datetime.today() - timedelta(days=14)).strftime('%Y-%m-%d')

    FINNHUB_TOKEN = st.secrets["FINNHUB_TOKEN"]

    news_tabs = st.tabs(selected_stocks)

    for tab, ticker in zip(news_tabs, selected_stocks):
        with tab:
            finnhub_articles = get_finnhub_news(
                ticker,
                start_date_str,
                end_date_str,
                FINNHUB_TOKEN
            )

            if not finnhub_articles:
                st.info(f"No recent news found for {ticker}.")
            else:
                for item in finnhub_articles:
                    f_title = item.get("headline", "Market Headline Unavailable")
                    f_link = item.get("url", "#")
                    f_source = item.get("source", "Financial Wire")
                    f_summary = item.get("summary", "")
                    f_image = item.get("image", "")

                    col_img, col_txt = st.columns([1, 4])
                    with col_img:
                        if f_image and str(f_image).strip().startswith("http"):
                            st.image(f_image, use_container_width=True)
                        else:
                            st.image("https://placehold.co/300x200/1f2633/ffffff?text=NEWS", use_container_width=True)
                    with col_txt:
                        st.markdown(f"### [{f_title}]({f_link})")
                        st.caption(f"Source: **{str(f_source).upper()}**")
                        if f_summary:
                            st.write(f_summary)
                        else:
                            st.write("Click the link above to read the full article.")
                    st.markdown("")

# ============================================================
# FOOTER
# ============================================================

st.markdown("""
<div class="custom-footer">
    <p>Created with ❤️ by <b>Mohammed Padghawala</b> | © 2026 All Rights Reserved</p>
</div>
""", unsafe_allow_html=True)