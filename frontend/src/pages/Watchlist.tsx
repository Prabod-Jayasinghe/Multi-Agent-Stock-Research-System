import React, { useState } from 'react';
import { useWatchlist } from '../hooks/useWatchlist';
import { apiService } from '../services/api';
import type { ResearchReport } from '../services/api';
import { SkeletonLoader } from '../components/SkeletonLoader';
import { ReportView } from '../components/ReportView';

const verdictColors: Record<string, string> = {
  BUY:  'bg-emerald-500/15 text-emerald-400 border border-emerald-500/25',
  HOLD: 'bg-amber-500/15  text-amber-400  border border-amber-500/25',
  SELL: 'bg-rose-500/15   text-rose-400   border border-rose-500/25',
};

export const Watchlist: React.FC = () => {
  const { watchlist, removeTicker, updateVerdict } = useWatchlist();
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState<ResearchReport | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [analyzingTicker, setAnalyzingTicker] = useState<string | null>(null);

  const handleAnalyze = async (ticker: string) => {
    setAnalyzingTicker(ticker);
    setLoading(true);
    setError(null);
    try {
      const data = await apiService.runResearch(ticker, 'AUTO');
      if (data.error) {
        setError(data.error);
      } else {
        if (data.synthesis?.verdict) {
          updateVerdict(ticker, data.synthesis.verdict, data.financials?.company_name);
        }
        setReport(data);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Research pipeline failed.');
    } finally {
      setLoading(false);
      setAnalyzingTicker(null);
    }
  };

  if (loading) return <SkeletonLoader />;
  if (report) return <ReportView report={report} onBack={() => setReport(null)} />;

  return (
    <div className="max-w-5xl mx-auto py-12 px-6 space-y-8">
      {/* Title */}
      <div className="space-y-2">
        <h2 className="text-3xl font-extrabold tracking-tight text-white">
          ⭐ Watchlist
        </h2>
        <p className="text-slate-400 text-sm">
          Your saved tickers. Click <span className="text-indigo-400 font-semibold">⚡ Analyze</span> to run a fresh multi-agent report, or{' '}
          <span className="text-rose-400 font-semibold">🗑️ Remove</span> to delete from the list.
          Your watchlist is saved locally in your browser.
        </p>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/25 text-rose-400 text-sm font-medium">
          ❌ {error}
        </div>
      )}

      {watchlist.length === 0 ? (
        /* Empty State */
        <div className="flex flex-col items-center justify-center py-24 space-y-6">
          <div className="w-20 h-20 rounded-2xl bg-[rgba(99,102,241,0.08)] border border-indigo-500/15 flex items-center justify-center text-4xl">
            ⭐
          </div>
          <div className="text-center space-y-2">
            <p className="text-lg font-semibold text-slate-300">Your watchlist is empty</p>
            <p className="text-sm text-slate-500 max-w-sm">
              Run a stock analysis, then click the{' '}
              <span className="text-amber-400 font-semibold">⭐ Watch</span> button on any report to save it here.
            </p>
          </div>
        </div>
      ) : (
        /* Watchlist Cards */
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {watchlist.map((item) => (
            <div
              key={item.ticker}
              className="bg-[rgba(26,26,46,0.5)] border border-[rgba(255,255,255,0.07)] rounded-2xl p-5 space-y-4 shadow-lg hover:border-indigo-500/25 transition-all group relative overflow-hidden"
            >
              {/* Glow accent */}
              <div className="absolute -top-8 -right-8 w-24 h-24 bg-indigo-500/5 rounded-full blur-2xl group-hover:bg-indigo-500/10 transition-all" />

              {/* Header */}
              <div className="flex justify-between items-start">
                <div className="space-y-0.5">
                  <p className="text-xl font-black text-white tracking-tight">{item.ticker}</p>
                  {item.companyName && (
                    <p className="text-xs text-slate-500 font-medium truncate max-w-[160px]">
                      {item.companyName}
                    </p>
                  )}
                </div>
                {item.lastVerdict && (
                  <span className={`px-2.5 py-1 rounded-full text-[10px] font-black ${verdictColors[item.lastVerdict]}`}>
                    {item.lastVerdict}
                  </span>
                )}
              </div>

              {/* Added date */}
              <p className="text-[11px] text-slate-600">
                Added {new Date(item.addedAt).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}
              </p>

              {/* Actions */}
              <div className="flex gap-2 pt-1">
                <button
                  onClick={() => handleAnalyze(item.ticker)}
                  disabled={analyzingTicker !== null}
                  className="flex-1 py-2 rounded-lg bg-indigo-600/20 hover:bg-indigo-600 text-indigo-400 hover:text-white border border-indigo-500/20 text-xs font-bold transition-all active:scale-95 cursor-pointer disabled:opacity-50 disabled:cursor-wait"
                >
                  {analyzingTicker === item.ticker ? '⏳ Analyzing…' : '⚡ Analyze'}
                </button>
                <button
                  onClick={() => removeTicker(item.ticker)}
                  className="px-3 py-2 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/15 text-xs font-bold transition-all active:scale-95 cursor-pointer"
                  title="Remove from watchlist"
                >
                  🗑️
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {watchlist.length > 0 && (
        <p className="text-center text-xs text-slate-600">
          {watchlist.length} ticker{watchlist.length !== 1 ? 's' : ''} in watchlist — stored locally in your browser
        </p>
      )}
    </div>
  );
};

export default Watchlist;
