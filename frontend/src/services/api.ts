import axios from 'axios';

// In development, Vite proxies /api/* to the backend (see vite.config.ts)
// In production, set VITE_API_URL to the deployed backend URL (e.g. https://your-app.onrender.com)
const API_BASE_URL = import.meta.env.VITE_API_URL || '';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface NewsItem {
  title: string;
  url: string;
  published_at: string;
  sentiment: 'Positive' | 'Neutral' | 'Negative';
  source: string;
}

export interface NewsAgentOutput {
  ticker: string;
  headlines: NewsItem[];
  overall_sentiment: 'Positive' | 'Neutral' | 'Negative';
  key_events: string[];
}

export interface FinancialsAgentOutput {
  ticker: string;
  company_name: string;
  exchange: string;
  pe_ratio: number | null;
  eps: number | null;
  revenue: number | null;
  market_cap: number | null;
  debt_to_equity: number | null;
  dividend_yield: number | null;
  fifty_two_week_high: number | null;
  fifty_two_week_low: number | null;
  current_price: number | null;
  valuation_commentary: string;
  data_source: 'yfinance' | 'cse_csv';
}

export interface SynthesisAgentOutput {
  verdict: 'BUY' | 'HOLD' | 'SELL';
  confidence: 'Low' | 'Medium' | 'Medium-High' | 'High';
  reasoning: string;
  risks: string[];
  disclaimer: string;
}

export interface ResearchReport {
  id: string;
  ticker: string;
  exchange: string;
  generated_at: string;
  news: NewsAgentOutput | null;
  financials: FinancialsAgentOutput | null;
  synthesis: SynthesisAgentOutput | null;
  processing_time_seconds: number | null;
  error: string | null;
}

export interface HistoryResponse {
  reports: ResearchReport[];
  total: number;
  page: number;
  page_size: number;
}

export interface CseStock {
  ticker: string;
  company: string;
  sector: string;
  pe_ratio: number | null;
  market_cap_lkr_mn: number | null;
  revenue_lkr_mn: number | null;
  eps: number | null;
  dividend_yield: number | null;
  debt_to_equity: number | null;
  last_updated: string;
}

export interface CseResponse {
  stocks: CseStock[];
  total: number;
  sectors: string[];
  note: string;
}

export const apiService = {
  /**
   * Triggers research pipeline for a stock
   */
  async runResearch(ticker: string, exchange: string = 'AUTO'): Promise<ResearchReport> {
    const response = await client.post<ResearchReport>('/api/research', {
      ticker,
      exchange,
    });
    return response.data;
  },

  /**
   * Retrieves paginated research history
   */
  async getHistory(ticker?: string, page: number = 1, pageSize: number = 10): Promise<HistoryResponse> {
    const params: Record<string, any> = { page, page_size: pageSize };
    if (ticker) {
      params.ticker = ticker;
    }
    const response = await client.get<HistoryResponse>('/api/history', { params });
    return response.data;
  },

  /**
   * Retrieves single report by ID
   */
  async getReport(reportId: string): Promise<ResearchReport> {
    const response = await client.get<ResearchReport>(`/api/report/${reportId}`);
    return response.data;
  },

  /**
   * Retrieves Colombo Stock Exchange (CSE) curated stocks
   */
  async getCseStocks(sector?: string): Promise<CseResponse> {
    const params: Record<string, any> = {};
    if (sector) {
      params.sector = sector;
    }
    const response = await client.get<CseResponse>('/api/cse', { params });
    return response.data;
  },

  /**
   * Gets detail of single CSE stock
   */
  async getCseStockDetail(ticker: string): Promise<CseStock> {
    const response = await client.get<CseStock>(`/api/cse/${ticker}`);
    return response.data;
  },
};
