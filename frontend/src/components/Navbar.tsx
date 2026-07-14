import React from 'react';

interface NavbarProps {
  activeTab: 'research' | 'history' | 'cse' | 'watchlist';
  setActiveTab: (tab: 'research' | 'history' | 'cse' | 'watchlist') => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab }) => {
  return (
    <header className="sticky top-0 z-50 backdrop-blur-md bg-[rgba(26,26,46,0.8)] border-b border-[rgba(255,255,255,0.08)] py-4 px-6 md:px-12 flex flex-col md:flex-row items-center justify-between gap-4">
      <div className="flex items-center gap-3 cursor-pointer" onClick={() => setActiveTab('research')}>
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-500 via-purple-500 to-pink-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
          <span className="text-xl font-bold text-white">🔍</span>
        </div>
        <div>
          <h1 className="text-xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-200 to-slate-400 uppercase">
            Multi-Agent Stock Analyst
          </h1>
        </div>
      </div>

      <nav className="flex items-center gap-1 bg-[rgba(15,15,23,0.6)] p-1.5 rounded-xl border border-[rgba(255,255,255,0.05)]">
        <button
          onClick={() => setActiveTab('research')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${
            activeTab === 'research'
              ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/10'
              : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
          }`}
        >
          🔬 Research
        </button>
        <button
          onClick={() => setActiveTab('history')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${
            activeTab === 'history'
              ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/10'
              : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
          }`}
        >
          📜 History
        </button>
        <button
          onClick={() => setActiveTab('cse')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${
            activeTab === 'cse'
              ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/10'
              : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
          }`}
        >
          🇱🇰 CSE
        </button>
        <button
          onClick={() => setActiveTab('watchlist')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${
            activeTab === 'watchlist'
              ? 'bg-amber-500 text-white shadow-md shadow-amber-500/10'
              : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
          }`}
        >
          ⭐ Watchlist
        </button>
      </nav>
    </header>
  );
};
export default Navbar;
