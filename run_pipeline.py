from dotenv import load_dotenv
load_dotenv()

from agents.graph import build_graph

def main():
    app = build_graph()

    question = input("Question: ").strip()
    goal = input("Goal: ").strip()

    state = {"task": {"question": question, "goal": goal}, "trace": []}
    out = app.invoke(state)

    print("\n================ FINAL OUTPUT ================\n")
    print(out.get("final", out.get("draft", "")))

    print("\n================ TRACE LOG ================\n")
    for step in out.get("trace", []):
        print(step)

if __name__ == "__main__":
    main()
