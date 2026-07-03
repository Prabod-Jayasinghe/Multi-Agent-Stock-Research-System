import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import type { CseStock, ResearchReport } from '../services/api';
import { SkeletonLoader } from '../components/SkeletonLoader';
import { ReportView } from '../components/ReportView';

export const CseExplorer: React.FC = () => {
  const [stocks, setStocks] = useState<CseStock[]>([]);
  const [sectors, setSectors] = useState<string[]>([]);
  const [selectedSector, setSelectedSector] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [researchLoading, setResearchLoading] = useState(false);
  const [report, setReport] = useState<ResearchReport | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchCseData = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiService.getCseStocks(selectedSector || undefined);
      setStocks(data.stocks);
      setSectors(data.sectors);
    } catch (err) {
      console.error(err);
      setError('Failed to fetch CSE curated stock dataset.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCseData();
  }, [selectedSector]);

  const handleResearch = async (ticker: string) => {
    setResearchLoading(true);
    setError(null);
    try {
      const data = await apiService.runResearch(ticker, 'CSE');
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
        'An error occurred executing research on this CSE stock.'
      );
    } finally {
      setResearchLoading(false);
    }
  };

  // Filter stocks client-side by search query
  const filteredStocks = stocks.filter((stock) => {
    const query = searchQuery.toLowerCase().trim();
    return (
      stock.ticker.toLowerCase().includes(query) ||
      stock.company.toLowerCase().includes(query) ||
      stock.sector.toLowerCase().includes(query)
    );
  });

  if (researchLoading) {
    return <SkeletonLoader />;
  }

  if (report) {
    return <ReportView report={report} onBack={() => setReport(null)} />;
  }

  return (
    <div className="max-w-5xl mx-auto py-12 px-6 space-y-8">
      {/* Title */}
      <div className="space-y-2">
        <h2 className="text-3xl font-extrabold tracking-tight text-white">
          🇱🇰 Colombo Stock Exchange Curated Directory
        </h2>
        <p className="text-slate-400 text-sm">
          Browse the top 50 CSE listed stocks curated from static financial registers. Click "Analyze" on any ticker to execute the multi-agent report pipeline.
        </p>
      </div>

      {/* Filters and Search Bar */}
      <div className="bg-[rgba(26,26,46,0.4)] border border-[rgba(255,255,255,0.06)] rounded-2xl p-5 shadow-lg grid grid-cols-1 sm:grid-cols-3 gap-4">
        
        {/* Search */}
        <div className="sm:col-span-2">
          <input
            type="text"
            placeholder="Filter stocks by ticker, company, or sector..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-4 py-2.5 rounded-xl bg-slate-900/60 border border-[rgba(255,255,255,0.1)] text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-all font-semibold uppercase text-sm"
          />
        </div>

        {/* Sector dropdown */}
        <div>
          <select
            value={selectedSector}
            onChange={(e) => setSelectedSector(e.target.value)}
            className="w-full px-4 py-2.5 rounded-xl bg-slate-900/60 border border-[rgba(255,255,255,0.1)] text-slate-300 focus:outline-none focus:border-indigo-500 transition-all font-semibold text-sm"
          >
            <option value="">All Sectors</option>
            {sectors.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Main Stock list */}
      <div className="bg-[rgba(26,26,46,0.4)] border border-[rgba(255,255,255,0.06)] rounded-3xl overflow-hidden shadow-2xl">
        {loading ? (
          <div className="p-12 text-center text-slate-400 animate-pulse font-medium">
            Retrieving CSE directories...
          </div>
        ) : error ? (
          <div className="p-8 text-center text-rose-400 text-sm font-semibold">
            {error}
          </div>
        ) : filteredStocks.length === 0 ? (
          <div className="p-12 text-center text-slate-500 italic">
            No stock listings matched search queries.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/5 bg-slate-900/40 text-slate-400 text-xs font-bold uppercase tracking-wider">
                  <th className="px-6 py-4">Ticker</th>
                  <th className="px-6 py-4">Company Name</th>
                  <th className="px-6 py-4">Sector</th>
                  <th className="px-6 py-4">Curated P/E</th>
                  <th className="px-6 py-4">Market Cap</th>
                  <th className="px-6 py-4 text-center">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {filteredStocks.map((stock) => (
                  <tr
                    key={stock.ticker}
                    className="hover:bg-white/5 transition-all text-slate-200 text-sm"
                  >
                    <td className="px-6 py-4 font-bold text-white tracking-wide">
                      {stock.ticker}
                    </td>
                    <td className="px-6 py-4 font-medium text-slate-300">
                      {stock.company}
                    </td>
                    <td className="px-6 py-4 text-slate-400">
                      {stock.sector}
                    </td>
                    <td className="px-6 py-4 font-mono font-medium text-slate-300">
                      {stock.pe_ratio !== null ? stock.pe_ratio.toFixed(1) : 'N/A'}
                    </td>
                    <td className="px-6 py-4 text-slate-400">
                      {stock.market_cap_lkr_mn !== null
                        ? `Rs. ${(stock.market_cap_lkr_mn).toLocaleString()} Mn`
                        : 'N/A'}
                    </td>
                    <td className="px-6 py-4 text-center">
                      <button
                        onClick={() => handleResearch(stock.ticker)}
                        className="px-4 py-1.5 rounded-lg bg-indigo-600/20 hover:bg-indigo-600 text-indigo-400 hover:text-white border border-indigo-500/20 text-xs font-bold transition-all transform active:scale-95 cursor-pointer"
                      >
                        ⚡ Analyze
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
export default CseExplorer;
