from retrieval.search import search_docs

FALLBACK_QUERIES = ["reorder point", "safety stock", "reorder point safety stock"]

def researcher_agent(state, k=8):
    queries = state.get("queries", []) or []
    all_hits = []

    for q in queries:
        all_hits.extend(search_docs(q, k=k))

    if not all_hits:
        for q in FALLBACK_QUERIES:
            all_hits.extend(search_docs(q, k=k))

    notes = []
    sources_used = set()
    allowed = set()
    seen_citations = set()

    for h in all_hits:
        src = h.get("source", "unknown")
        page = h.get("page", "?")
        chunk = h.get("chunk_id", "?")
        txt = (h.get("text", "") or "").replace("\n", " ").strip()
        citation = f"[{src} | page {page} | chunk {chunk}]"

        if citation in seen_citations:
            continue
        seen_citations.add(citation)

        sources_used.add(src)
        allowed.add(citation)
        notes.append(f"{txt} {citation}")

    state["notes"] = notes
    state["sources_used"] = sorted(sources_used)
    state["raw_hits"] = len(all_hits)
    state["allowed_citations"] = sorted(allowed)
    return state
