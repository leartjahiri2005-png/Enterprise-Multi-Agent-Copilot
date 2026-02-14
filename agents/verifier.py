from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def verifier_agent(state):
    draft = state.get("draft", "")
    notes = state.get("notes", []) or []
    allowed = state.get("allowed_citations", []) or []

    notes_block = "\n\n".join(notes[:60]).strip()
    allowed_block = "\n".join(allowed[:200]).strip()

    prompt = f"""
You are a strict verifier.

Rules:
1) Keep headings/sections the same.
2) Only allow claims supported by Evidence Notes.
3) Allowed citations must be EXACTLY from the whitelist.
4) Owner/Due/Confidence are planning metadata (do NOT require evidence).
5) If a bullet/email line/action is unsupported OR has missing/invalid citation:
   REPLACE THE ENTIRE LINE with exactly:
Not found in sources.
(Do not keep any original words, numbering, punctuation, or citations.)

Allowed Citations Whitelist:
{allowed_block}

Draft:
{draft}

Evidence Notes:
{notes_block}

Return:
A) VERIFICATION_REPORT (short bullets)
B) VERIFIED_DRAFT (final corrected output)
""".strip()

    result = llm.invoke(prompt).content
    state["verification"] = result

    verified = result
    if "VERIFIED_DRAFT" in result:
        verified = result.split("VERIFIED_DRAFT", 1)[1].lstrip(":").strip()

    state["final"] = verified
    state["needs_revision"] = False
    return state
