"""
agents/synthesis_agent.py
Stub — will be fully implemented in Phase 4.
Combines news + financials data and generates a BUY/HOLD/SELL verdict via Groq LLM.
"""
from core.models import NewsAgentOutput, FinancialsAgentOutput, SynthesisAgentOutput


async def run_synthesis_agent(
    news: NewsAgentOutput,
    financials: FinancialsAgentOutput
) -> SynthesisAgentOutput:
    """Entry point called by the orchestrator."""
    raise NotImplementedError("Synthesis Agent will be implemented in Phase 4")
