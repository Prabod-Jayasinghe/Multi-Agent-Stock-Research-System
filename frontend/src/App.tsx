import React, { useState } from 'react';
import Navbar from './components/Navbar';
import Research from './pages/Research';
import History from './pages/History';
import CseExplorer from './pages/CseExplorer';
import Watchlist from './pages/Watchlist';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'research' | 'history' | 'cse' | 'watchlist'>('research');

  const renderActivePage = () => {
    switch (activeTab) {
      case 'research':
        return <Research />;
      case 'history':
        return <History />;
      case 'cse':
        return <CseExplorer />;
      case 'watchlist':
        return <Watchlist />;
      default:
        return <Research />;
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#0f0f17] text-[#e2e8f0]">
      {/* Dynamic Header Navbar */}
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Core Page Content canvas */}
      <main className="flex-grow container mx-auto px-4 md:px-8 py-8">
        {renderActivePage()}
      </main>

      {/* Modern Professional Footer */}
      <footer className="py-6 border-t border-[rgba(255,255,255,0.05)] text-center bg-[rgba(26,26,46,0.3)]">
        <p className="text-xs text-slate-500 font-medium">
          © {new Date().getFullYear()} Antigravity Stock Research System • Built with multi-agent coordination engines.
        </p>
      </footer>
    </div>
  );
};

export default App;
