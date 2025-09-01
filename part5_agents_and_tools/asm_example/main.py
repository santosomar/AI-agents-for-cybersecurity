# LangGraph Example: Pentesting Workflow Main
#
# This script builds the main workflow for our pentesting application using LangGraph.
# It includes the necessary nodes and edges to discover subdomains, scan for open ports,
# scan for vulnerabilities, and generate a report.
#
# Instructor: Omar Santos @santosomar


from langgraph.graph import StateGraph, END
from pentest_graph_state import AttackSurfaceState
from pentest_graph_nodes import reconnaissance_step, vulnerability_scan_step, analysis_step, report_step
from pentest_graph_router import should_proceed_to_report

# 1. Initialize the StateGraph
workflow = StateGraph(AttackSurfaceState)

# 2. Add the nodes to the graph
workflow.add_node("reconnaissance", reconnaissance_step)
workflow.add_node("vulnerability_scan", vulnerability_scan_step)
workflow.add_node("analysis", analysis_step)
workflow.add_node("generate_report", report_step)

# 3. Define the edges
workflow.set_entry_point("reconnaissance")
workflow.add_edge("reconnaissance", "vulnerability_scan")
workflow.add_edge("vulnerability_scan", "analysis")

# 4. Add the conditional edge for routing after analysis
workflow.add_conditional_edges(
    "analysis",
    should_proceed_to_report,
    {
        "generate_report": "generate_report"
        # "attempt_exploitation": "exploitation_node" # Example of another branch
    }
)
workflow.add_edge("generate_report", END)

# 5. Compile the graph into a runnable application
app = workflow.compile()

# 6. Run the agent
initial_state = {"target_domain": "example.com", "is_exploitable": False}
final_state = app.invoke(initial_state)

# Print the final report
print("\n" + "="*50)
print("FINAL PENETRATION TEST REPORT")
print("="*50 + "\n")
print(final_state.get("report"))

# Print the workflow log
print("\n" + "="*50)
print("WORKFLOW LOG")
print("="*50 + "\n")
print(final_state.get("workflow_log"))
