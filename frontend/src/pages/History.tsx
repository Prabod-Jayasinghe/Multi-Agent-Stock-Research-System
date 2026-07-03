import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import type { ResearchReport } from '../services/api';
import { ReportView } from '../components/ReportView';

export const History: React.FC = () => {
  const [reports, setReports] = useState<ResearchReport[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [tickerQuery, setTickerQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedReport, setSelectedReport] = useState<ResearchReport | null>(null);
  const [error, setError] = useState<string | null>(null);

  const PAGE_SIZE = 10;

  const fetchHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiService.getHistory(tickerQuery.trim(), page, PAGE_SIZE);
      setReports(data.reports);
      setTotal(data.total);
    } catch (err: any) {
      console.error(err);
      setError('Failed to retrieve report history.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [page]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchHistory();
  };

  const loadReportDetail = async (reportId: string) => {
    setLoading(true);
    setError(null);
    try {
      const rep = await apiService.getReport(reportId);
      setSelectedReport(rep);
    } catch (err) {
      console.error(err);
      setError('Could not retrieve detailed report details.');
    } finally {
      setLoading(false);
    }
  };

  const getVerdictBadge = (verdict?: 'BUY' | 'HOLD' | 'SELL') => {
    if (!verdict) return 'bg-slate-500/10 text-slate-400 border border-slate-500/20';
    const badges = {
      BUY: 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/20',
      HOLD: 'bg-amber-500/15 text-amber-400 border border-amber-500/20',
      SELL: 'bg-rose-500/15 text-rose-400 border border-rose-500/20',
    };
    return badges[verdict];
  };

  if (selectedReport) {
    return <ReportView report={selectedReport} onBack={() => setSelectedReport(null)} />;
  }

  return (
    <div className="max-w-5xl mx-auto py-12 px-6 space-y-8">
      {/* Title */}
      <div className="space-y-2">
        <h2 className="text-3xl font-extrabold tracking-tight text-white">
          📜 Report History Catalog
        </h2>
        <p className="text-slate-400 text-sm">
          Browse previously generated equity research reports. Click on any row to open the full detailed report.
        </p>
      </div>

      {/* Filter controls */}
      <div className="bg-[rgba(26,26,46,0.4)] border border-[rgba(255,255,255,0.06)] rounded-2xl p-5 shadow-lg">
        <form onSubmit={handleSearchSubmit} className="flex flex-col sm:flex-row gap-3">
          <input
            type="text"
            placeholder="Search by Ticker symbol (e.g. AAPL)..."
            value={tickerQuery}
            onChange={(e) => setTickerQuery(e.target.value)}
            className="flex-grow px-4 py-2.5 rounded-xl bg-slate-900/60 border border-[rgba(255,255,255,0.1)] text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-all font-semibold uppercase text-sm"
          />
          <button
            type="submit"
            className="px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold transition-all text-sm cursor-pointer"
          >
            Filter Results
          </button>
        </form>
      </div>

      {/* Reports Table container */}
      <div className="bg-[rgba(26,26,46,0.4)] border border-[rgba(255,255,255,0.06)] rounded-3xl overflow-hidden shadow-2xl">
        {loading && reports.length === 0 ? (
          <div className="p-12 text-center text-slate-400 animate-pulse font-medium">
            Loading report database...
          </div>
        ) : error ? (
          <div className="p-8 text-center text-rose-400 text-sm font-semibold">
            {error}
          </div>
        ) : reports.length === 0 ? (
          <div className="p-12 text-center text-slate-500 italic">
            No research reports found in history. Try running a new analysis.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/5 bg-slate-900/40 text-slate-400 text-xs font-bold uppercase tracking-wider">
                  <th className="px-6 py-4">Ticker</th>
                  <th className="px-6 py-4">Company Name</th>
                  <th className="px-6 py-4">Exchange</th>
                  <th className="px-6 py-4">Verdict</th>
                  <th className="px-6 py-4">Confidence</th>
                  <th className="px-6 py-4 text-right">Analyzed Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {reports.map((report) => (
                  <tr
                    key={report.id}
                    onClick={() => loadReportDetail(report.id)}
                    className="hover:bg-white/5 transition-all cursor-pointer text-slate-200 text-sm"
                  >
                    <td className="px-6 py-4 font-bold text-white tracking-wide">
                      {report.ticker}
                    </td>
                    <td className="px-6 py-4 font-medium text-slate-300">
                      {report.financials?.company_name || report.ticker}
                    </td>
                    <td className="px-6 py-4 text-slate-400">
                      {report.exchange}
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2.5 py-1 rounded-full text-xs font-black ${getVerdictBadge(report.synthesis?.verdict)}`}>
                        {report.synthesis?.verdict || 'HOLD'}
                      </span>
                    </td>
                    <td className="px-6 py-4 font-medium text-slate-400">
                      {report.synthesis?.confidence || 'Medium'}
                    </td>
                    <td className="px-6 py-4 text-right text-xs text-slate-500">
                      {new Date(report.generated_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Pagination component */}
      {total > PAGE_SIZE && (
        <div className="flex justify-between items-center px-4">
          <p className="text-xs text-slate-500 font-medium">
            Showing Page <span className="text-slate-300">{page}</span> of{' '}
            <span className="text-slate-300">{Math.ceil(total / PAGE_SIZE)}</span> (
            <span className="text-indigo-400">{total}</span> total reports)
          </p>
          <div className="flex gap-2">
            <button
              onClick={() => setPage((p) => Math.max(p - 1, 1))}
              disabled={page === 1}
              className="px-4 py-2 text-xs font-semibold rounded-lg bg-white/5 border border-white/5 text-slate-400 disabled:opacity-40 hover:bg-white/10 hover:text-white transition-all cursor-pointer"
            >
              Previous
            </button>
            <button
              onClick={() => setPage((p) => p + 1)}
              disabled={page * PAGE_SIZE >= total}
              className="px-4 py-2 text-xs font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white disabled:opacity-40 disabled:hover:bg-indigo-600 transition-all cursor-pointer"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
export default History;
