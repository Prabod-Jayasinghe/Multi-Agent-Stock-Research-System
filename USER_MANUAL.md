# 📖 Antigravity Multi-Agent Stock Research System — User Manual

Welcome to **Antigravity**, an autonomous financial intelligence platform. By coordinating three specialized AI agents (News, Financials, and Synthesis), the system performs real-time market research and delivers structured equity analysis reports with a clear **BUY / HOLD / SELL** verdict.

This manual explains how to set up, operate, and troubleshoot the platform.

---

## 🛠️ Step 1: Getting Free API Keys

The system is designed to run entirely on free-tier APIs. Before starting, obtain the following credentials:

### 1. Groq LLM Key (Free)
- **What it does**: Powers the reasoning engine of all three agents.
- **Where to get it**: Visit [console.groq.com](https://console.groq.com/), sign up, and create an API key.
- **Limits**: The free plan provides up to 14,400 requests/day, which is more than enough for individual use.

### 2. GNews API Key (Free)
- **What it does**: Allows the News Agent to fetch the top 5 recent news headlines for a stock ticker.
- **Where to get it**: Sign up at [gnews.io](https://gnews.io/) to receive a free API key.
- **Limits**: The free plan allows **100 requests per day**.
  > [!TIP]
  > The platform implements an **in-memory 1-hour cache** per ticker. Repeatedly searching the same stock within an hour will not consume your GNews API quota.

### 3. Supabase Database URL (Optional - Free Tier)
- **What it does**: Stores generated research reports so you can browse them later on the "Report History" page.
- **Where to get it**: Sign up at [supabase.com](https://supabase.com/), create a new PostgreSQL project, and copy your connection string from the database settings.
  > [!NOTE]
  > If you do not configure a database, the system automatically falls back to an **in-memory store**. The application will function normally, but reports will be cleared when the backend server restarts.

---

## ⚙️ Step 2: Environment Configuration

1. In the root of the project, make a copy of `.env.example` and name it `.env`:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and fill in your API credentials:
   ```env
   GROQ_API_KEY=gsk_your_real_key_here
   GNEWS_API_KEY=your_gnews_key_here
   
   # Optional: Database settings (leave blank for in-memory mode)
   DATABASE_URL=postgresql://postgres:password@db.xxxx.supabase.co:5432/postgres
   ```

---

## 🚀 Step 3: Launching the Application

### Option A: Running with Docker (Recommended)
If you have Docker installed, you can start the entire system with a single command:
```bash
docker compose up --build
```
This launches the backend on port `8000` and the frontend on port `3000`.

### Option B: Running Manually

#### 1. Start the Backend API:
```bash
cd backend
pip install -r requirements.txt
python main.py
```
*The backend API will run at [http://localhost:8000](http://localhost:8000).*

#### 2. Start the Frontend UI:
Open a separate terminal window:
```bash
cd frontend
npm install
npm run dev
```
*The Vite development server will open the UI at [http://localhost:5173](http://localhost:5173).*

---

## 🌍 Step 4: Global Exchange Suffix Guide

The Financials Agent parses ticker suffixes to identify the correct stock exchange. Standardise your inputs using the following rules:

| Exchange | Suffix | Example Ticker | Description |
|----------|--------|----------------|-------------|
| **USA** | *None* | `AAPL` / `TSLA` | NYSE & NASDAQ listings (real-time via `yfinance`) |
| **Japan** | `.T` | `7203.T` | Tokyo Stock Exchange (real-time via `yfinance`) |
| **United Kingdom** | `.L` | `VOD.L` | London Stock Exchange (real-time via `yfinance`) |
| **Germany** | `.DE` | `SAP.DE` | XETRA / Frankfurt Exchange (real-time via `yfinance`) |
| **India (NSE)** | `.NS` | `RELIANCE.NS` | National Stock Exchange of India (real-time via `yfinance`) |
| **India (BSE)** | `.BO` | `TATASTEEL.BO` | Bombay Stock Exchange (real-time via `yfinance`) |
| **Sri Lanka** | `.N` | `JKH.N` | Colombo Stock Exchange (curated 50-stock static CSV) |

---

## 🧭 Step 5: Application Walkthrough

### 🔬 1. Running Stock Research
- Go to the **Research** tab.
- Enter a stock symbol (e.g. `AAPL` or `7203.T`).
- Set the exchange drop-down to **AUTO Detect** or explicitly select an exchange.
- Click **Run Analysis**.
- The screen will transition to the loading page. You will see real-time updates as different agents execute (fetching news, scraping ratios, modeling recommendations).
- Once synthesis finishes, a beautifully formatted visual report containing the final verdict, financial progress meters, news sentiment gauges, and risk cards will load.

### 📜 2. Viewing Past Reports
- Click the **Report History** tab to view all previously generated reports.
- Use the search bar to filter history by ticker.
- Click on any row to open the full detailed report.

### 🇱🇰 3. Colombo Stock Exchange Curated Directory
- Click the **CSE Explorer** tab.
- Browse the 50 top listed equities on the Colombo Stock Exchange (loaded from static registers).
- Use the dropdown to filter by sector (e.g. `Banking & Finance`, `Telecommunications`, `Diversified`).
- Click **⚡ Analyze** next to any stock to trigger the multi-agent synthesis model immediately.

---

## ❓ Troubleshooting

### 1. "Network Error" appears on click
- **Cause**: The backend server is either stopped or CORS is blocking the request.
- **Solution**: 
  1. Verify the backend is running by visiting [http://localhost:8000/health](http://localhost:8000/health).
  2. Ensure your terminal running Vite is serving on `localhost:5173` or `localhost:3000`, as allowed in `backend/core/config.py`.

### 2. "Valuation commentary unavailable: Groq API key not configured"
- **Cause**: The `GROQ_API_KEY` is missing from the `.env` file.
- **Solution**: Ensure your `.env` contains a valid Groq key, and restart the backend terminal.

### 3. Sri Lankan stocks show no live price
- **Cause**: CSE data is served from a static CSV fallback (`cse_stocks.csv`) compiled in 2025.
- **Solution**: This is expected behavior as CSE lacks a public real-time API. Financial commentary and analysis are performed using the static curated values.
