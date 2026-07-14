/**
 * hooks/useWatchlist.ts
 * Custom React hook for managing a persistent watchlist of stock tickers.
 * Data is stored in localStorage under the key "antigravity_watchlist".
 */

import { useState, useCallback } from 'react';

const STORAGE_KEY = 'antigravity_watchlist';

export interface WatchlistItem {
  ticker: string;
  addedAt: string;
  lastVerdict?: 'BUY' | 'HOLD' | 'SELL';
  companyName?: string;
}

function loadFromStorage(): WatchlistItem[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as WatchlistItem[]) : [];
  } catch {
    return [];
  }
}

function saveToStorage(items: WatchlistItem[]): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
  } catch {
    // Storage quota exceeded — fail silently
  }
}

export function useWatchlist() {
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>(loadFromStorage);

  const addTicker = useCallback(
    (ticker: string, opts?: { lastVerdict?: 'BUY' | 'HOLD' | 'SELL'; companyName?: string }) => {
      const upper = ticker.trim().toUpperCase();
      setWatchlist((prev) => {
        if (prev.some((item) => item.ticker === upper)) return prev;
        const next: WatchlistItem[] = [
          { ticker: upper, addedAt: new Date().toISOString(), ...opts },
          ...prev,
        ];
        saveToStorage(next);
        return next;
      });
    },
    []
  );

  const removeTicker = useCallback((ticker: string) => {
    const upper = ticker.trim().toUpperCase();
    setWatchlist((prev) => {
      const next = prev.filter((item) => item.ticker !== upper);
      saveToStorage(next);
      return next;
    });
  }, []);

  const updateVerdict = useCallback(
    (ticker: string, verdict: 'BUY' | 'HOLD' | 'SELL', companyName?: string) => {
      const upper = ticker.trim().toUpperCase();
      setWatchlist((prev) => {
        const next = prev.map((item) =>
          item.ticker === upper ? { ...item, lastVerdict: verdict, companyName } : item
        );
        saveToStorage(next);
        return next;
      });
    },
    []
  );

  const isWatched = useCallback(
    (ticker: string) => {
      const upper = ticker.trim().toUpperCase();
      return watchlist.some((item) => item.ticker === upper);
    },
    [watchlist]
  );

  return { watchlist, addTicker, removeTicker, updateVerdict, isWatched };
}
