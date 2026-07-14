# 🔍 Multi-Agent Stock Research System

An AI-powered financial intelligence platform that coordinates three specialized AI agents (News, Financials, and Synthesis) to perform real-time equity research and deliver comprehensive reports with a clear **BUY / HOLD / SELL** recommendation.

![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![License](https://img.shields.io/badge/License-MIT-blue)
![Python](https://img.shields.io/badge/Python-3.11-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688)
![React](https://img.shields.io/badge/React-18-61DAFB)
![Tests](https://img.shields.io/badge/Tests-127_Passed-brightgreen)
![TypeScript](https://img.shields.io/badge/TypeScript-5-blue)
![Vite](https://img.shields.io/badge/Vite-5-646CFF)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-4-38B2AC)
![LLM-Power](https://img.shields.io/badge/LLM-Groq--Llama--3.1-orange)
![Database](https://img.shields.io/badge/Database-Supabase--PostgreSQL-3ECF8E)

---

## 🌐 Live Application & Demo

* **Live Deployment Link**: [Visit Live Application](https://multi-agent-stock-research-system.vercel.app/)

### 🎥 Working Demo Video
<video src="./docs/demo_video.mp4" width="100%" controls></video>

### 📸 System Screenshots
| | |
|---|---|
| **Research Dashboard** <br> ![Screenshot 1](./docs/Screenshot%201.png) | **Real-Time Agent Pipelines** <br> ![Screenshot 2](./docs/Screenshot%202.png) |
| **Comprehensive Analysis Report** <br> ![Screenshot 3](./docs/Screenshot%203.png) | **Interactive Watchlist Manager** <br> ![Screenshot 4](./docs/Screenshot%204.png) |

---

## 🏗️ Architecture

The orchestrator utilizes asynchronous concurrency with `asyncio.gather` to scrape financials and aggregate news in parallel, isolating individual agent failures and handing over unified datasets to the final LLM consensus synthesis engine.

```
                       [ User Input (Ticker) ]
                                  │
                                  ▼
                      ┌───────────────────────┐
                      │  FastAPI Orchestrator │
                      └───────────┬───────────┘
                                  │
                  ┌───────────────┴───────────────┐
                  ▼ (asyncio.gather Parallel)     ▼ (asyncio.gather Parallel)
       ┌─────────────────────┐         ┌─────────────────────┐
       │     News Agent      │         │   Financials Agent  │
       │  (GNews API + Groq) │         │ (yfinance/CSV + Groq)│
       └──────────┬──────────┘         └──────────┬──────────┘
                  │                               │
                  └───────────────┬───────────────┘
                                  ▼ (Sequential)
                      ┌───────────────────────┐
                      │    Synthesis Agent    │
                      │  (BUY/HOLD/SELL JSON) │
                      └───────────┬───────────┘
                                  ▼
                     ┌─────────────────────────┐
                     │ Supabase DB Persistence │
                     └─────────────────────────┘
```

---

## 🤖 AI Specialist Agents

| Agent | Core Responsibility | Logic & Flow Details | Data Source |
|-------|---------------------|----------------------|-------------|
| **News Agent** | Analyzes recent media sentiment | Fetches top 5 headlines, runs parallel sentiment classification per article via Groq, aggregates key catalyst events, and provides a majority-vote fallback if JSON parses fail. Implements an in-memory 1-hour `TTLCache` to protect GNews quotas. | GNews API + Groq LLM |
| **Financials Agent** | Analyzes fundamental valuation metrics | Scrapes valuation and balance sheet metrics. Runs yfinance in a background thread pool to prevent blocking the async loop. For Sri Lankan equities, automatically routes queries to a static local CSV fallback registry. Generates a concise valuation commentary paragraph. | yfinance API / Curated CSV + Groq LLM |
| **Synthesis Agent** | Resolves consensus recommendation | Synthesizes joint News & Financial outputs, runs a 3-tier self-correction retry loop to enforce valid JSON structures, appends risk caution metrics, and issues the final BUY/HOLD/SELL verdict. | Groq LLM |

---

## 🌍 Supported Exchanges

| Exchange | Suffix | Example Ticker | Description | Currency |
|----------|--------|----------------|-------------|----------|
| **USA** | *None* | `AAPL` / `TSLA` | NYSE & NASDAQ listings | USD ($) |
| **Japan** | `.T` | `7203.T` | Tokyo Stock Exchange | JPY (¥) |
| **United Kingdom** | `.L` | `VOD.L` | London Stock Exchange | GBP (£) |
| **Germany** | `.DE` | `SAP.DE` | XETRA / Frankfurt Exchange | EUR (€) |
| **India** | `.NS` | `RELIANCE.NS` | National Stock Exchange | INR (Rs.) |
| **India** | `.BO` | `TATASTEEL.BO` | Bombay Stock Exchange | INR (Rs.) |
| **Sri Lanka** | `.N` | `JKH.N` | Colombo Stock Exchange (Static fallbacks) | LKR (Rs.) |

---

## ✨ Features & Functionality

* **⭐ Localized Watchlist**: Save and monitor custom stock tickets across browser reloads using a persistent `localStorage` bookmark board. Triggers fresh multi-agent scans directly from the watchlist cards.
* **🖨️ Clean PDF Exporting**: Layout includes optimized print CSS that hides header/navbars and overrides colors to produce readable, high-contrast, paper-optimized reports via browser printing.
* **⚡ 1-Hour News Cache**: Limits API rate-limiting issues on the GNews free tier by checking an in-memory TTL caching layer.
* **🛡️ Chaos Isolation**: The orchestrator protects against agent crashes—if the News API rate limits or yfinance timeouts occur, the synthesis engine safely evaluates the report using partial metrics.

---

## 🛠️ Tech Stack

### Backend
* **FastAPI** — High-performance ASGI REST framework.
* **Groq SDK** — Powered by `llama-3.1-8b-instant` for sub-second, highly structured JSON-mode output generation.
* **yfinance** — Extends scraping rules for real-time tickers.
* **GNews API** — Targeted search and query parsing.
* **Supabase / SQL Alchemy** — PostgreSQL persistence with asyncpg drivers and automatic connection pools.

### Frontend
* **React 18 & TypeScript** — Type-safe, modular visual layouts.
* **Vite** — Optimized production bundler and dev server.
* **TailwindCSS v4** — High-performance grid styling and dark-mode gradients.
* **Axios** — Client requests with local dev proxy setups.

---

## 🚀 Quick Start (Local)

### Prerequisites
* Python 3.11+
* Node.js 18+
* Docker & Docker Compose (optional)

### 1. Clone and Configure
```bash
git clone https://github.com/j-coder-shan/Multi-Agent-Stock-Research-System.git
cd Multi-Agent-Stock-Research-System
cp .env.example .env
# Open .env and insert your GROQ_API_KEY and GNEWS_API_KEY
```

### 2. Run with Docker
```bash
docker compose up --build
```

### 3. Or Run Manually
#### Start the Backend API
```bash
cd backend
pip install -r requirements.txt
python main.py
```
*Backend documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs).*

#### Start the Frontend UI (separate terminal)
```bash
cd frontend
npm install
npm run dev
```
*Vite web server is available at [http://localhost:5173/](http://localhost:5173/).*

---

## 🚀 Production Deployment

For complete details on deploying the application to production using **Render** (backend), **Vercel** (frontend), and **Supabase** (database), refer to the [Production Deployment Guide](file:///c:/Users/PRABO/OneDrive/Documents/GitHub/Multi-Agent-Stock-Research-System/DEPLOYMENT.md).

---

## 📋 Project Milestones & Roadmap

| Milestone | Scope | Status |
|-------|--------|--------|
| **1 — Project Setup** | Scaffold backend & frontend layouts. | ✅ Complete |
| **2 — Stock Data Pipeline** | yfinance & local CSE dataset bindings. | ✅ Complete |
| **3 — News Agent** | GNews, sentiment scoring, TTLCache. | ✅ Complete |
| **4 — Synthesis Agent** | Consensus valuation rules, 3-tier correction loops. | ✅ Complete |
| **5 — Orchestration Layer** | Parallel execution models via asyncio. | ✅ Complete |
| **6 — Database Integration** | PostgreSQL schemas & async migrations. | ✅ Complete |
| **7 — User Interface** | Search boards, dials, news feeds, and skeleton loaders. | ✅ Complete |
| **8 — Curated Directory** | Colombo Stock Exchange explorer catalogs. | ✅ Complete |
| **9 — Automated Tests** | Pytest & Vitest configuration suite (127/127 tests). | ✅ Complete |
| **10 — Local Development** | Multi-container Docker configs & health validations. | ✅ Complete |
| **11 — India Market Suffixes** | Indian National & Bombay Stock Exchange support. | ✅ Complete |
| **12 — Features Integration** | Local Storage Watchlist and PDF print layouts. | ✅ Complete |
| **13 — Production Deployment** | Render backend + Vercel static frontends. | ✅ Complete |

---

## ⚠️ Disclaimer

Reports generated by this system are for **informational purposes only** and do not constitute financial advice. Always consult a qualified financial advisor before making investment decisions.

---

## 📄 License

MIT © 2026

