"""
agents/financials_agent.py
Stub — will be fully implemented in Phase 2.
Fetches stock fundamentals via yfinance and generates valuation commentary via Groq LLM.
"""
from core.models import FinancialsAgentOutput


async def run_financials_agent(ticker: str, exchange: str) -> FinancialsAgentOutput:
    """Entry point called by the orchestrator."""
    raise NotImplementedError("Financials Agent will be implemented in Phase 2")
