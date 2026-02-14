from typing import Any, Dict, List, TypedDict


class CopilotState(TypedDict, total=False):
    task: str
    plan: Dict[str, Any]
    queries: List[str]
    notes: List[str]                
    evidence: List[str]
    sources_used: List[str]
    draft: str
    final: str
    verification_report: Dict[str, Any]
    trace: List[Dict[str, Any]]
    allowed_citations: List[str]
    raw_hits: int
