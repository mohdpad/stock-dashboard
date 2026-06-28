# 📈 Real-Time & Historical Multi-Stock Analytics Dashboard

A premium, production-ready financial analytics dashboard built with **Streamlit**, **YFinance**, and **Plotly**. This application enables institutional-grade, multi-stock comparative analysis by delivering real-time pricing metrics, responsive historical market visualization, expanded corporate fundamental data, and a live financial news pipeline.

## 🚀 Key Architectural Features

*   **Asynchronous API Search Auto-Complete:** Utilizes an asynchronous background processing pipeline via `streamlit-searchbox` to query Yahoo Finance endpoints dynamically on every keystroke, bypassing traditional `Enter`-to-submit lag.
*   **Multi-Ticker Comparative Engine:** Supports concurrent evaluation of multiple equity/index assets with dynamic layout adjustments for modern side-by-side metric tracking.
*   **Dynamic Time-Horizon Charting:** Features responsive interval/period mapping via interactive Plotly Candlestick overlays across tailored windows (`1D @ 1m`, `1W @ 15m`, `1M @ 1d`, `1Y @ 1wk`).
*   **Live Institutional News Stream:** Integrates an isolated premium market news pipeline powered by the Finnhub API for real-time editorial sentiment tracking.

---

## 🛠️ Tech Stack & Infrastructure

*   **UI Framework:** Streamlit (Wide-layout responsive configuration)
*   **Data Aggregation:** `yfinance` (Market data structures), `requests` (REST API polling)
*   **Visualization Engine:** Plotly Graph Objects (`plotly.graph_objects`)
*   **Data Manipulation:** Pandas (`pandas`)

---

## 📦 Local Installation & Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   cd YOUR_REPO_NAME
   ```

2. **Set Up a Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application:**
   ```bash
   streamlit run app.py
   ```

## 🔑 Environment Configuration & Secrets Management
To securely manage third-party infrastructure without hardcoding corporate credentials, this project utilizes Streamlit Secrets management (.streamlit/secrets.toml locally or via the Streamlit Cloud management interface):

```toml
FINNHUB_TOKEN = "your_premium_finnhub_api_token_here"
```

## 🤝 Author

Developed by **Mohammed Padghawala**.

***
