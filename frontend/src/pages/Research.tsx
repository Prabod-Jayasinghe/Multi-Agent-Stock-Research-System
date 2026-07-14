import React, { useState } from 'react';
import { apiService } from '../services/api';
import type { ResearchReport } from '../services/api';
import { SkeletonLoader } from '../components/SkeletonLoader';
import { ReportView } from '../components/ReportView';

export const Research: React.FC = () => {
  const [ticker, setTicker] = useState('');
  const [exchange, setExchange] = useState('AUTO');
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState<ResearchReport | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ticker.trim()) return;

    setLoading(true);
    setError(null);
    setReport(null);

    try {
      const data = await apiService.runResearch(ticker.trim(), exchange);
      if (data.error) {
        setError(data.error);
      } else {
        setReport(data);
      }
    } catch (err: any) {
      console.error(err);
      setError(
        err.response?.data?.detail || 
        err.message || 
        'An error occurred while executing the research agents.'
      );
    } finally {
      setLoading(false);
    }
  };

  const clearReport = () => {
    setReport(null);
    setError(null);
  };

  if (loading) {
    return <SkeletonLoader />;
  }

  if (report) {
    return <ReportView report={report} onBack={clearReport} />;
  }

  return (
    <div className="max-w-4xl mx-auto py-12 px-6 space-y-12">
      {/* Hero Header */}
      <div className="text-center space-y-4 max-w-2xl mx-auto">
        <h2 className="text-4xl md:text-5xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-200 to-slate-400">
          Autonomous Equity Research
        </h2>
        <p className="text-slate-400 text-sm md:text-base leading-relaxed">
          Input a stock ticker to coordinate a team of AI analysts. The system gathers recent news articles, extracts financial fundamentals, and synthesizes a Buy/Hold/Sell report.
        </p>
      </div>

      {/* Main Search Panel */}
      <div className="bg-[rgba(26,26,46,0.5)] border border-[rgba(255,255,255,0.08)] rounded-3xl p-6 md:p-10 shadow-2xl relative">
        <div className="absolute -top-12 -left-12 w-48 h-48 bg-indigo-500/10 rounded-full blur-3xl -z-10"></div>
        <div className="absolute -bottom-12 -right-12 w-48 h-48 bg-purple-500/10 rounded-full blur-3xl -z-10"></div>

        <form onSubmit={handleSearch} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            
            {/* Ticker Input */}
            <div className="md:col-span-2 space-y-2">
              <label htmlFor="ticker" className="text-xs font-bold uppercase tracking-wider text-indigo-400">
                Stock Ticker Symbol
              </label>
              <input
                id="ticker"
                type="text"
                value={ticker}
                onChange={(e) => setTicker(e.target.value)}
                placeholder="e.g. AAPL, 7203.T, JKH.N"
                className="w-full px-4 py-3 rounded-xl bg-slate-900/60 border border-[rgba(255,255,255,0.1)] text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-all font-semibold uppercase"
                required
              />
            </div>

            {/* Exchange Dropdown */}
            <div className="space-y-2">
              <label htmlFor="exchange" className="text-xs font-bold uppercase tracking-wider text-indigo-400">
                Exchange Hint
              </label>
              <select
                id="exchange"
                value={exchange}
                onChange={(e) => setExchange(e.target.value)}
                className="w-full px-4 py-3 rounded-xl bg-slate-900/60 border border-[rgba(255,255,255,0.1)] text-slate-300 focus:outline-none focus:border-indigo-500 transition-all font-semibold"
              >
                <option value="AUTO">AUTO Detect</option>
                <option value="USA">USA (NYSE/NASDAQ)</option>
                <option value="Japan">Japan (TSE)</option>
                <option value="UK">UK (LSE)</option>
                <option value="Germany">Germany (XETRA)</option>
                <option value="India">India — NSE (.NS)</option>
                <option value="India">India — BSE (.BO)</option>
                <option value="CSE">CSE (Colombo)</option>
              </select>
            </div>

            {/* Submit Button */}
            <div className="flex items-end">
              <button
                type="submit"
                className="w-full py-3 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white font-bold shadow-lg shadow-indigo-500/25 transition-all transform active:scale-[0.98] cursor-pointer"
              >
                Run Analysis
              </button>
            </div>
          </div>
        </form>

        {error && (
          <div className="mt-6 p-4 rounded-xl bg-rose-500/10 border border-rose-500/25 text-rose-400 text-sm font-medium">
            ❌ {error}
          </div>
        )}
      </div>

      {/* Suffix Helper Card */}
      <div className="bg-[rgba(255,255,255,0.01)] border border-[rgba(255,255,255,0.03)] rounded-2xl p-6">
        <h4 className="text-sm font-bold text-slate-300 mb-4">💡 Global Exchange Suffix Guide</h4>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 text-xs">
          <div className="space-y-1">
            <p className="text-slate-500 uppercase font-semibold">USA Exchange</p>
            <p className="text-white font-bold">No Suffix</p>
            <p className="text-slate-400">e.g. AAPL, TSLA</p>
          </div>
          <div className="space-y-1">
            <p className="text-slate-500 uppercase font-semibold">Tokyo Stock Exch</p>
            <p className="text-white font-bold">.T</p>
            <p className="text-slate-400">e.g. 7203.T (Toyota)</p>
          </div>
          <div className="space-y-1">
            <p className="text-slate-500 uppercase font-semibold">London Stock Exch</p>
            <p className="text-white font-bold">.L</p>
            <p className="text-slate-400">e.g. VOD.L (Vodafone)</p>
          </div>
          <div className="space-y-1">
            <p className="text-slate-500 uppercase font-semibold">Germany (XETRA)</p>
            <p className="text-white font-bold">.DE</p>
            <p className="text-slate-400">e.g. SAP.DE</p>
          </div>
          <div className="space-y-1">
            <p className="text-slate-500 uppercase font-semibold">India NSE</p>
            <p className="text-white font-bold">.NS</p>
            <p className="text-slate-400">e.g. RELIANCE.NS</p>
          </div>
          <div className="space-y-1">
            <p className="text-slate-500 uppercase font-semibold">Colombo Stock Exch</p>
            <p className="text-white font-bold">.N</p>
            <p className="text-slate-400">e.g. JKH.N (John Keells)</p>
          </div>
        </div>
      </div>
    </div>
  );
};
export default Research;
