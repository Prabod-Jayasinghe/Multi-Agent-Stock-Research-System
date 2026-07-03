"""
orchestrator.py
Stub — will be fully implemented in Phase 5.
Runs News Agent and Financials Agent in parallel, then feeds results to Synthesis Agent.
"""
from core.models import ResearchRequest, ResearchReport


async def run_research_pipeline(request: ResearchRequest) -> ResearchReport:
    """
    Orchestrates the full multi-agent research pipeline.
    Phase 5 will implement:
      - asyncio.gather() for parallel News + Financials agents
      - Sequential Synthesis agent call
      - Error isolation per agent
    """
    raise NotImplementedError("Orchestrator will be implemented in Phase 5")
