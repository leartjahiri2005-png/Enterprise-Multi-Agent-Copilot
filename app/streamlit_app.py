# app/streamlit_app.py
import os
import sys
import subprocess
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
RUN_SCRIPT = ROOT / "run_pipeline.py"

FINAL_MARKER = "================ FINAL OUTPUT ================"
TRACE_MARKER = "================ TRACE LOG ================"


def run_pipeline_cli(question: str, goal: str) -> dict:
    """Run run_pipeline.py (stdin: Question + Goal) and parse Final Output + Trace Log."""
    if not RUN_SCRIPT.exists():
        raise FileNotFoundError(f"Cannot find: {RUN_SCRIPT}")

    user_input = f"{question.strip()}\n{goal.strip()}\n"

    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"

    proc = subprocess.run(
        [sys.executable, str(RUN_SCRIPT)],
        input=user_input,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        cwd=str(ROOT),
        env=env,
        timeout=300,  # prevent hanging forever
    )

    stdout = proc.stdout or ""
    stderr = proc.stderr or ""

    final_output = ""
    trace_log = ""

    if FINAL_MARKER in stdout:
        after_final = stdout.split(FINAL_MARKER, 1)[1].strip()
        if TRACE_MARKER in after_final:
            final_output = after_final.split(TRACE_MARKER, 1)[0].strip()
            trace_log = after_final.split(TRACE_MARKER, 1)[1].strip()
        else:
            final_output = after_final.strip()

    return {
        "returncode": proc.returncode,
        "final_output": final_output,
        "trace_log": trace_log,
        "raw_stdout": stdout,
        "raw_stderr": stderr,
    }


st.set_page_config(page_title="Enterprise Multi-Agent Copilot", layout="wide")

st.title("Enterprise Multi-Agent Copilot UI")
st.caption("Planner → Researcher → Writer → Verifier • Final Output + Trace Log + Raw Logs")

with st.sidebar:
    st.subheader("Run settings")
    st.write("Make sure your `.env` has `OPENAI_API_KEY` and your `.venv` is active.")
    st.code("streamlit run app/streamlit_app.py")

    st.subheader("Presets")
    preset = st.selectbox(
        "Pick a sample task",
        [
            "Cycle counting (inventory discrepancies)",
            "Safety stock + ROP (reduce stockouts)",
            "Supplier reliability (lead-time variability)",
            "Lean warehouse (reduce lead times)",
        ],
    )

    if preset == "Cycle counting (inventory discrepancies)":
        default_q = "How can cycle counting reduce inventory discrepancies in a warehouse?"
        default_g = "Generate an executive summary (<=150 words), a 6-line client email (each line ends with one citation), and 6 actions (Owner, Due, Confidence + one citation each)."
    elif preset == "Safety stock + ROP (reduce stockouts)":
        default_q = "How can we set safety stock and reorder points (ROP) to reduce stockouts without increasing excess inventory?"
        default_g = "Generate an executive summary (<=150 words), a 6-line client email (each line ends with one citation), and 6 actions (Owner, Due, Confidence + one citation each)."
    elif preset == "Supplier reliability (lead-time variability)":
        default_q = "How can we improve supplier reliability and reduce lead-time variability to prevent stockouts in the supply chain?"
        default_g = "Generate an executive summary (<=150 words), a 6-line client email (each line ends with one citation), and 6 actions (Owner, Due, Confidence + one citation each)."
    else:
        default_q = "How can lean warehouse practices reduce picking/receiving lead times and improve inventory accuracy?"
        default_g = "Generate an executive summary (<=150 words), a 6-line client email (each line ends with one citation), and 6 actions (Owner, Due, Confidence + one citation each)."

# store in session only once (so typing won’t reset on rerun)
if "question" not in st.session_state:
    st.session_state.question = default_q
if "goal" not in st.session_state:
    st.session_state.goal = default_g

col1, col2 = st.columns(2)

with col1:
    st.session_state.question = st.text_area("Question", st.session_state.question, height=140)

with col2:
    st.session_state.goal = st.text_area("Goal", st.session_state.goal, height=140)

c1, c2, c3 = st.columns([1, 1, 2])
with c1:
    run_btn = st.button("Run Pipeline", type="primary")
with c2:
    clear_btn = st.button("Clear Output")

if clear_btn:
    st.session_state.pop("last_result", None)

if run_btn:
    q = (st.session_state.question or "").strip()
    g = (st.session_state.goal or "").strip()

    if not q or not g:
        st.error("Please provide both Question and Goal.")
    else:
        with st.spinner("Running pipeline..."):
            try:
                result = run_pipeline_cli(q, g)
                st.session_state.last_result = result
            except subprocess.TimeoutExpired:
                st.error("Pipeline timed out (300s).")
            except Exception as e:
                st.error(f"Failed to run pipeline: {e}")

result = st.session_state.get("last_result")

if result:
    if result["returncode"] != 0:
        st.error("Pipeline returned a non-zero exit code.")
        if result["raw_stderr"]:
            st.code(result["raw_stderr"])
    else:
        st.success("Done ✅")

    tabs = st.tabs(["Final Output", "Trace Log", "Raw Console Output"])

    with tabs[0]:
        if result["final_output"].strip():
            st.markdown(result["final_output"])
        else:
            st.warning("Could not parse Final Output section. See Raw Console Output.")
            st.code(result["raw_stdout"])

    with tabs[1]:
        if result["trace_log"].strip():
            st.code(result["trace_log"])
        else:
            st.warning("Could not parse Trace Log section. See Raw Console Output.")
            st.code(result["raw_stdout"])

    with tabs[2]:
        st.subheader("STDOUT")
        st.code(result["raw_stdout"] or "(empty)")
        st.subheader("STDERR")
        st.code(result["raw_stderr"] or "(empty)")
