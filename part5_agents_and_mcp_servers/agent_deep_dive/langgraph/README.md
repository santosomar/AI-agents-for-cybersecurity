# LangGraph: Branching and Conditional Logic Example

This directory contains examples demonstrating the use of LangGraph, a library for building stateful, multi-actor applications with LLMs.

## `branching_conditional_logic.py`

This script showcases how to implement conditional logic (branching) within a LangGraph workflow. It simulates a basic cybersecurity incident response scenario where the analysis path changes based on the initial findings.

### Workflow Overview:

1.  **State Definition**: An `IncidentState` class is defined to hold the state of the workflow, including `messages` and `indicators_of_compromise`.
2.  **Nodes**:
    *   `initial_analysis`: Performs an initial assessment of an alert.
    *   `phishing_analysis`: Performs a detailed analysis if the incident is suspected to be a phishing attempt. It extracts a (dummy) malicious URL.
    *   `malware_analysis`: Performs a detailed analysis if the incident is suspected to involve malware. It identifies a (dummy) C2 server.
3.  **Conditional Edges**:
    *   The `decide_next_step` function determines the next node to execute based on keywords in the last message from the `initial_analysis` node.
    *   If "phishing" is detected, the graph transitions to `phishing_analysis`.
    *   If "malware" is detected, the graph transitions to `malware_analysis`.
    *   Otherwise, the workflow ends.
4.  **Graph Construction**:
    *   A `StateGraph` is initialized with `IncidentState`.
    *   Nodes are added to the graph.
    *   `initial_analysis` is set as the entry point.
    *   Conditional edges are defined using `add_conditional_edges` to route the workflow based on the output of `decide_next_step`.
    *   Regular edges connect `phishing_analysis` and `malware_analysis` to the `END` node.
5.  **Execution**: The compiled graph (`app`) is invoked with an initial empty state, and the final state (result) is printed.

### Key LangGraph Concepts Demonstrated:

*   **StateGraph**: Building a graph where nodes modify a shared state.
*   **Nodes**: Functions that represent steps in the workflow.
*   **Conditional Edges**: Defining branches in the workflow based on the current state.
*   **Entry Point**: Specifying the starting node of the graph.
*   **Compilation**: Compiling the graph definition into a runnable application.

This example provides a clear illustration of how to direct the flow of a LangGraph application based on dynamic conditions, a crucial feature for creating sophisticated and adaptive LLM-powered agents.
