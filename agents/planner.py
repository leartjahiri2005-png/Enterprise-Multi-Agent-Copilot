from langchain_openai import ChatOpenAI
import json

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def planner_agent(state):
    task = state.get("task", "")

    prompt = f"""
You are a planning agent.
Given the user task, output a small plan and 6 focused retrieval queries that are likely to be answered by supply chain PDFs.
Return valid JSON only with keys:
- plan: short bullet list (3-6 bullets)
- retrieval_queries: list of 6 queries

User task:
{task}
""".strip()

    try:
        out = llm.invoke(prompt).content.strip()
        out = out.replace("```json", "").replace("```", "").strip()
        data = json.loads(out)
        plan = data.get("plan", [])
        queries = data.get("retrieval_queries", [])
        if not queries:
            raise ValueError
    except Exception:
        plan = [
            "Use safety stock as a buffer against demand/lead-time variability",
            "Define reorder point (ROP) to trigger replenishment at the right time",
            "Align parameters to reduce stockout risk while controlling inventory cost"
        ]
        queries = [
            "safety stock buffer demand variability stockouts",
            "reorder point (ROP) definition triggers replenishment",
            "reorder point relates to safety stock lead time demand",
            "too little safety stock shortages too much increases costs",
            "lead time variability customer demand safety stock stockouts",
            "when to reorder inventory reorder point critical stock"
        ]

    state["plan"] = {"bullets": plan}
    state["queries"] = queries[:6]
    return state
