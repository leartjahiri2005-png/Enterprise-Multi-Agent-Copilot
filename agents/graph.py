import time
from typing import Dict, Any
from langgraph.graph import StateGraph, END

from .state import CopilotState
from .planner import planner_agent
from .researcher import researcher_agent
from .writer import writer_agent
from .verifier import verifier_agent


def _trace(state: CopilotState, agent: str, info: Dict[str, Any]) -> None:
    t = state.get("trace", [])
    t.append({"agent": agent, **info})
    state["trace"] = t


def planner_node(state: CopilotState) -> CopilotState:
    t0 = time.time()

    # planner_agent pret dict (state) dhe kthen state të përditësuar
    state = planner_agent(state)

    _trace(
        state,
        "planner",
        {
            "ms": int((time.time() - t0) * 1000),
            "queries": state.get("queries", []),
        },
    )
    return state


def researcher_node(state: CopilotState) -> CopilotState:
    t0 = time.time()

    # i kalojmë gjithë state-in te researcher_agent
    state = researcher_agent(state)
    notes = state.get("notes", [])
    print("notes_len:", len(notes))
    if notes:
        print("note0_type:", type(notes[0]))
        print("note0_preview:", str(notes[0])[:200])


    _trace(state, "researcher", {
        "ms": int((time.time()-t0)*1000),
        "hits": state.get("raw_hits", 0),
        "sources": state.get("sources_used", [])
    })
    return state



def writer_node(state: CopilotState) -> CopilotState:
    t0 = time.time()

    state = writer_agent(state)  # ✅ vetëm 1 argument (state)
    print("allowed_citations:", len(state.get("allowed_citations", [])))



    draft = state.get("draft", "")
    _trace(
        state,
        "writer",
        {"ms": int((time.time() - t0) * 1000), "draft_chars": len(draft)},
    )
    return state

def verifier_node(state: CopilotState) -> CopilotState:
    t0 = time.time()

    state = verifier_agent(state)  # ✅ vetëm 1 argument

    report = state.get("verification_report", {})
    trace_info = {"ms": int((time.time() - t0) * 1000)}
    if isinstance(report, dict):
        trace_info.update(report)

    _trace(state, "verifier", trace_info)
    return state


def build_graph():
    g = StateGraph(CopilotState)

    g.add_node("planner", planner_node)
    g.add_node("researcher", researcher_node)
    g.add_node("writer", writer_node)
    g.add_node("verifier", verifier_node)

    g.set_entry_point("planner")
    g.add_edge("planner", "researcher")
    g.add_edge("researcher", "writer")
    g.add_edge("writer", "verifier")
    g.add_edge("verifier", END)

    return g.compile()


