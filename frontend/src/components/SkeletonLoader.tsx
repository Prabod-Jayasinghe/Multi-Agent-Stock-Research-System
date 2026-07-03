import React, { useEffect, useState } from 'react';

export const SkeletonLoader: React.FC = () => {
  const [progressText, setProgressText] = useState('Initializing research agents...');
  const [step, setStep] = useState(1);

  useEffect(() => {
    const textTimer1 = setTimeout(() => {
      setProgressText('News Agent: Fetching stock news from GNews API...');
      setStep(2);
    }, 4000);

    const textTimer2 = setTimeout(() => {
      setProgressText('Financials Agent: Retrieving fundamental metrics via yfinance...');
      setStep(3);
    }, 10000);

    const textTimer3 = setTimeout(() => {
      setProgressText('Financials Agent: Generating stock valuation commentary...');
      setStep(4);
    }, 18000);

    const textTimer4 = setTimeout(() => {
      setProgressText('Synthesis Agent: Aggregating inputs and generating BUY/HOLD/SELL verdict...');
      setStep(5);
    }, 25000);

    return () => {
      clearTimeout(textTimer1);
      clearTimeout(textTimer2);
      clearTimeout(textTimer3);
      clearTimeout(textTimer4);
    };
  }, []);

  return (
    <div className="w-full max-w-4xl mx-auto space-y-8 animate-fade-in p-6">
      {/* Status Card */}
      <div className="bg-[rgba(26,26,46,0.6)] border border-[rgba(255,255,255,0.06)] rounded-2xl p-6 text-center space-y-4">
        <div className="relative w-16 h-16 mx-auto">
          <div className="absolute inset-0 rounded-full border-4 border-indigo-500/20 border-t-indigo-500 animate-spin"></div>
          <div className="absolute inset-2 rounded-full border-4 border-purple-500/10 border-b-purple-500 animate-spin animate-reverse-spin"></div>
        </div>
        <div className="space-y-1">
          <h3 className="text-lg font-semibold text-slate-100">Running Multi-Agent Synthesis</h3>
          <p className="text-sm text-indigo-400 font-medium animate-pulse">{progressText}</p>
        </div>

        {/* Progress Bar steps */}
        <div className="max-w-md mx-auto grid grid-cols-5 gap-2 pt-2">
          {[1, 2, 3, 4, 5].map((s) => (
            <div
              key={s}
              className={`h-1.5 rounded-full transition-all duration-500 ${
                s <= step
                  ? 'bg-gradient-to-r from-indigo-500 to-purple-500 shadow-md shadow-indigo-500/20'
                  : 'bg-slate-800'
              }`}
            ></div>
          ))}
        </div>
        <p className="text-[11px] text-slate-500">
          This process normally takes between 15 to 30 seconds as agents perform real-time sentiment analysis and valuation modeling.
        </p>
      </div>

      {/* Main Grid Skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Recommendation card placeholder */}
        <div className="md:col-span-3 bg-[rgba(26,26,46,0.4)] border border-[rgba(255,255,255,0.04)] rounded-2xl p-6 space-y-4">
          <div className="h-4 bg-slate-800 rounded w-1/4 animate-pulse"></div>
          <div className="h-16 bg-slate-800/60 rounded-xl w-full animate-pulse"></div>
          <div className="space-y-2">
            <div className="h-3 bg-slate-800/40 rounded w-5/6 animate-pulse"></div>
            <div className="h-3 bg-slate-800/40 rounded w-4/6 animate-pulse"></div>
          </div>
        </div>

        {/* Financial metrics skeleton */}
        <div className="md:col-span-2 bg-[rgba(26,26,46,0.4)] border border-[rgba(255,255,255,0.04)] rounded-2xl p-6 space-y-4">
          <div className="h-4 bg-slate-800 rounded w-1/3 animate-pulse"></div>
          <div className="grid grid-cols-2 gap-4">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="flex justify-between items-center py-2 border-b border-white/5">
                <div className="h-3 bg-slate-800/50 rounded w-1/2 animate-pulse"></div>
                <div className="h-3 bg-slate-800 rounded w-1/4 animate-pulse"></div>
              </div>
            ))}
          </div>
        </div>

        {/* News skeleton */}
        <div className="bg-[rgba(26,26,46,0.4)] border border-[rgba(255,255,255,0.04)] rounded-2xl p-6 space-y-4">
          <div className="h-4 bg-slate-800 rounded w-1/2 animate-pulse"></div>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="space-y-2">
                <div className="flex justify-between">
                  <div className="h-2.5 bg-slate-800/60 rounded w-1/4 animate-pulse"></div>
                  <div className="h-2 bg-slate-800/40 rounded w-1/6 animate-pulse"></div>
                </div>
                <div className="h-3 bg-slate-800 rounded w-full animate-pulse"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
export default SkeletonLoader;
