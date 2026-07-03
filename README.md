# 🔍 Multi-Agent Stock Research System

An AI-powered financial research platform that uses **three specialized AI agents** working in coordination to deliver comprehensive stock analysis reports with a **BUY / HOLD / SELL** recommendation.

![Status](https://img.shields.io/badge/Status-In%20Development-yellow)
![License](https://img.shields.io/badge/License-MIT-blue)
![Python](https://img.shields.io/badge/Python-3.11-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688)
![React](https://img.shields.io/badge/React-18-61DAFB)

---

## 🏗️ Architecture

```
User Input (ticker)
       │
       ▼
┌─────────────────────────────────────────┐
│              Orchestrator               │
│   (asyncio.gather — runs in parallel)   │
└────────────┬───────────────┬────────────┘
             │               │
     ┌───────▼──────┐ ┌──────▼────────┐
     │  News Agent  │ │Financials Agent│
     │  (GNews API) │ │  (yfinance)   │
     │  Groq LLM   │ │  Groq LLM     │
     └───────┬──────┘ └──────┬────────┘
             │               │
             └───────┬───────┘
                     ▼
            ┌────────────────┐
            │Synthesis Agent │
            │   Groq LLM    │
            │ BUY/HOLD/SELL  │
            └────────┬───────┘
                     │
                     ▼
              Research Report
              (saved to DB)
```

## 🤖 Agents

| Agent | Responsibility | Data Source |
|-------|---------------|-------------|
| **News Agent** | Fetches top 5 headlines, sentiment analysis | GNews API + Groq |
| **Financials Agent** | PE, EPS, Revenue, Market Cap, etc. | yfinance + Groq |
| **Synthesis Agent** | BUY/HOLD/SELL verdict, confidence, risks | Groq (aggregator) |

## 🌍 Supported Exchanges

| Exchange | Suffix | Example |
|----------|--------|---------|
| USA (NYSE/NASDAQ) | *(none)* | `AAPL`, `TSLA` |
| Japan (TSE) | `.T` | `7203.T` |
| UK (LSE) | `.L` | `VOD.L` |
| Germany (XETRA) | `.DE` | `SAP.DE` |
| Colombo (CSE) | `.N` | `JKH.N` (static CSV) |

## 🛠️ Tech Stack

**Backend**
- [FastAPI](https://fastapi.tiangolo.com/) — REST API
- [Groq](https://console.groq.com/) — Free LLM (llama3-8b-8192)
- [yfinance](https://github.com/ranaroussi/yfinance) — Stock data (free)
- [GNews](https://gnews.io/) — News headlines (free, 100 req/day)
- [Supabase](https://supabase.com/) — PostgreSQL database (free tier)

**Frontend**
- [React 18](https://react.dev/) + [Vite](https://vitejs.dev/) + TypeScript
- [TailwindCSS](https://tailwindcss.com/) — Styling

**Infrastructure**
- [Render.com](https://render.com/) — Backend hosting (free tier)
- [Vercel](https://vercel.com/) — Frontend hosting (free tier)
- [Docker Compose](https://docs.docker.com/compose/) — Local dev environment

---

## 🚀 Quick Start (Local)

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optional)

### 1. Clone and configure
```bash
git clone https://github.com/j-coder-shan/Multi-Agent-Stock-Research-System.git
cd Multi-Agent-Stock-Research-System
cp .env.example .env
# Edit .env with your API keys
```

### 2. Get free API keys
| Service | URL | Free Tier |
|---------|-----|-----------|
| Groq | https://console.groq.com/ | 14,400 req/day |
| GNews | https://gnews.io/ | 100 req/day |
| Supabase | https://supabase.com/ | 500MB DB |

### 3. Run with Docker
```bash
docker compose up --build
```

### 4. Or run manually
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

### 5. Open the app
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 📋 Development Phases

| Phase | Branch | Status |
|-------|--------|--------|
| 1 — Project Setup | `phase/1-project-setup` | ✅ Complete |
| 2 — Stock Data Pipeline | `phase/2-stock-data-pipeline` | 🔄 Next |
| 3 — News Agent | `phase/3-news-agent` | ⏳ Pending |
| 4 — Synthesis Agent | `phase/4-synthesis-agent` | ⏳ Pending |
| 5 — Orchestrator + FastAPI | `phase/5-orchestrator-fastapi` | ⏳ Pending |
| 6 — Database Integration | `phase/6-database-integration` | ⏳ Pending |
| 7 — React Frontend | `phase/7-react-frontend` | ⏳ Pending |
| 8 — CSE Dataset | `phase/8-cse-dataset` | ⏳ Pending |
| 9 — Testing | `phase/9-testing` | ⏳ Pending |
| 10 — Docker & Local Dev | `phase/10-docker-local-dev` | ⏳ Pending |
| 11 — Deployment | `phase/11-deployment` | ⏳ Pending |

---

## ⚠️ Disclaimer

Reports generated by this system are for **informational purposes only** and do not constitute financial advice. Always consult a qualified financial advisor before making investment decisions.

---

## 📄 License

MIT © 2026
