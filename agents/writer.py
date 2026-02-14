from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def writer_agent(state):
    task = state.get("task", "")
    plan = state.get("plan", {})
    notes_list = state.get("notes", []) or []
    allowed_list = state.get("allowed_citations", []) or []

    evidence_block = "\n\n".join(notes_list[:60]).strip()
    allowed_block = "\n".join(allowed_list[:200]).strip()

    prompt = f"""
You are a writing agent. Use ONLY the Evidence Notes.

User task:
{task}

Plan:
{plan}

Evidence Notes (each ends with a citation; copy citations EXACTLY):
{evidence_block}

Allowed Citations (use ONLY these; copy EXACTLY):
{allowed_block}

OUTPUT (exact structure):

### 1) Executive Summary
- Exactly 3 bullets
- Total <= 150 words
- Each bullet MUST end with exactly ONE allowed citation
- If you cannot support a bullet, output exactly: Not found in sources.

### 2) Client-ready Email
Subject: <short subject>
- Then EXACTLY 6 lines (do NOT count Subject as a line)
- Each line MUST end with exactly ONE allowed citation
- If you cannot support a line, output exactly: Not found in sources.

### 3) Action List
- Exactly 6 actions
- Format each action EXACTLY like:
  1) <action>. Owner: <role>. Due: <30 days/60 days/90 days/Quarterly/Ongoing>. Confidence: <High/Medium/Low>. [citation]
- Each action MUST end with exactly ONE allowed citation
- If you cannot support an action, output exactly: Not found in sources.

STRICT:
- Do NOT add facts not in Evidence Notes.
- Do NOT invent/modify citations.
""".strip()

    state["draft"] = llm.invoke(prompt).content.strip()
    return state
