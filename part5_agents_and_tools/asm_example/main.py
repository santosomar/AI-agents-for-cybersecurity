# LangGraph Example: Pentesting Workflow — Main Entry Point
#
# Assembles the attack surface management graph, compiles it, and runs it
# against a target domain.  The graph demonstrates:
#   - Linear edges (recon → vuln scan → analysis)
#   - Conditional branching (analysis → exploitation OR report)
#   - Shared state with Annotated reducers
#
# Instructor: Omar Santos @santosomar

from dotenv import load_dotenv
from langgraph.graph import END, StateGraph

from pentest_graph_nodes import (
    analysis_step,
    exploitation_step,
    reconnaissance_step,
    report_step,
    vulnerability_scan_step,
)
from pentest_graph_router import route_after_analysis
from pentest_graph_state import AttackSurfaceState

load_dotenv()

# ------------------------------------------------------------------
# 1. Build the graph
# ------------------------------------------------------------------
workflow = StateGraph(AttackSurfaceState)

# 2. Register every node
workflow.add_node("reconnaissance", reconnaissance_step)
workflow.add_node("vulnerability_scan", vulnerability_scan_step)
workflow.add_node("analysis", analysis_step)
workflow.add_node("exploitation", exploitation_step)
workflow.add_node("generate_report", report_step)

# 3. Linear edges
workflow.set_entry_point("reconnaissance")
workflow.add_edge("reconnaissance", "vulnerability_scan")
workflow.add_edge("vulnerability_scan", "analysis")

# 4. Conditional edge — branch after analysis
workflow.add_conditional_edges(
    "analysis",
    route_after_analysis,
    {
        "exploitation": "exploitation",
        "generate_report": "generate_report",
    },
)

# exploitation always flows into the report
workflow.add_edge("exploitation", "generate_report")
workflow.add_edge("generate_report", END)

# 5. Compile
app = workflow.compile()

# ------------------------------------------------------------------
# 6. Run
# ------------------------------------------------------------------
if __name__ == "__main__":
    initial_state = {
        "target_domain": "example.com",
        "is_exploitable": False,
        "subdomains": [],
        "open_ports": {},
        "vulnerabilities": [],
        "workflow_log": [],
    }

    final_state = app.invoke(initial_state)

    print("\n" + "=" * 60)
    print("  PENETRATION TEST REPORT")
    print("=" * 60 + "\n")
    print(final_state.get("report", "No report generated."))

    print("\n" + "=" * 60)
    print("  WORKFLOW LOG")
    print("=" * 60 + "\n")
    for entry in final_state.get("workflow_log", []):
        print(f"  • {entry}")
    print()
