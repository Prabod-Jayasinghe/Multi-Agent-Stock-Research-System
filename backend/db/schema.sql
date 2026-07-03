-- ─────────────────────────────────────────────────────────────────────────────
-- schema.sql
-- Supabase / PostgreSQL schema for Multi-Agent Stock Research System
--
-- Run this once in your Supabase SQL editor (or any PostgreSQL instance).
-- ─────────────────────────────────────────────────────────────────────────────

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ─── Reports table ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS reports (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker          VARCHAR(20) NOT NULL,
    exchange        VARCHAR(100),
    generated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- News Agent output (JSONB for flexibility)
    news            JSONB,

    -- Financials Agent output
    financials      JSONB,

    -- Synthesis Agent output
    synthesis       JSONB,

    -- Pipeline metadata
    processing_time_seconds FLOAT,
    error           TEXT        -- populated if pipeline partially failed

);

-- ─── Indexes ──────────────────────────────────────────────────────────────────
-- Fast lookup by ticker (most common query)
CREATE INDEX IF NOT EXISTS idx_reports_ticker
    ON reports (ticker);

-- Newest-first ordering
CREATE INDEX IF NOT EXISTS idx_reports_generated_at
    ON reports (generated_at DESC);

-- Composite: ticker + date (for filtered history queries)
CREATE INDEX IF NOT EXISTS idx_reports_ticker_date
    ON reports (ticker, generated_at DESC);

-- ─── Row-Level Security (RLS) ────────────────────────────────────────────────
-- Enable RLS on the table (Supabase best practice).
-- The backend uses the service role key which bypasses RLS.
-- Public (anon) access is intentionally read-only here.
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;

-- Allow anyone (anon) to SELECT reports (public read)
CREATE POLICY IF NOT EXISTS "Public read reports"
    ON reports FOR SELECT
    TO anon
    USING (true);

-- Only the service role can INSERT/UPDATE/DELETE
-- (No explicit policy needed — service role bypasses RLS by default)

-- ─── Sample data for verification ────────────────────────────────────────────
-- Uncomment to insert a test row after running the schema:
/*
INSERT INTO reports (ticker, exchange, news, financials, synthesis)
VALUES (
    'AAPL',
    'NYSE / NASDAQ',
    '{"overall_sentiment": "Positive", "headlines": [], "key_events": ["Test event"]}'::jsonb,
    '{"company_name": "Apple Inc.", "pe_ratio": 32.1, "data_source": "yfinance"}'::jsonb,
    '{"verdict": "BUY", "confidence": "High", "reasoning": "Test.", "risks": ["r1","r2","r3"]}'::jsonb
);
SELECT * FROM reports;
*/
