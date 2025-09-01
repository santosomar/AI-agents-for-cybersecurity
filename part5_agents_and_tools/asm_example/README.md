## LangGraph Pentesting Workflow Example (ASM)

This example demonstrates a simple Attack Surface Management (ASM) workflow built with LangGraph. It shows how to model a pentesting pipeline as a stateful graph with nodes for reconnaissance, vulnerability scanning, analysis with an LLM, and report generation.

### Files

- `main.py`: Builds the `StateGraph` using `AttackSurfaceState`, wires nodes and edges, compiles the app, runs it with an initial state, and prints the final report and workflow log.
- `pentest_graph_state.py`: Defines the shared state schema as a `TypedDict` (`AttackSurfaceState`) that flows through the graph: `target_domain`, `subdomains`, `open_ports`, `vulnerabilities`, `analysis_result`, `is_exploitable`, `report`, and `workflow_log`.
- `pentest_graph_nodes.py`: Implements the graph nodes and placeholder tools:
  - Placeholder tools: `run_subfinder`, `run_nmap`, `run_nuclei` (simple, safe simulators of common security tools).
  - Nodes:
    - `reconnaissance_step`: Discovers subdomains and open ports.
    - `vulnerability_scan_step`: Scans discovered assets for vulnerabilities.
    - `analysis_step`: Uses an LLM to analyze scan results and decide if they look exploitable.
    - `report_step`: Compiles a human-readable report using the state.
- `pentest_graph_router.py`: Routing logic after analysis via `should_proceed_to_report`. In this example it always proceeds to `generate_report`, but this is where branching could happen (e.g., to an exploitation branch) based on state.

### How the Graph Flows

Entry → `reconnaissance` → `vulnerability_scan` → `analysis` → conditional route → `generate_report` → END

- The `AttackSurfaceState` is passed between nodes and incrementally enriched.
- The conditional route checks the analysis and (optionally) vulnerability presence to decide next steps.

### Prerequisites

- Python 3.10+ recommended
- Install dependencies from the repository root:

```bash
pip install -r requirements.txt
```

- OpenAI API key is required for the `analysis_step` (uses `ChatOpenAI` with `gpt-5`). Set it in your environment before running:

```bash
export OPENAI_API_KEY="YOUR_KEY_HERE"
```

Notes:
- The placeholder tools do not perform any real scanning; they are safe to run. Only the LLM call requires internet access and valid credentials.
- If you do not have an API key, you can modify `analysis_step` to short-circuit (e.g., return a fixed result) for offline demos.

### Running the Example

From the repository root or this directory:

```bash
python part5_agents_and_tools/asm_example/main.py
# or if you are already in the directory
python main.py
```

What you will see:
- A final “Penetration Test Report” summarizing subdomains, open ports, vulnerabilities, and analysis.
- A workflow log indicating which steps ran.

### Customization Tips

- Change the target domain: edit `initial_state` in `main.py` (key `target_domain`).
- Branching logic: update `should_proceed_to_report` in `pentest_graph_router.py` to add more routes (e.g., to an exploitation node) based on `is_exploitable` or other state.
- Replace placeholders with real tools: swap out `run_subfinder`, `run_nmap`, `run_nuclei` in `pentest_graph_nodes.py` with actual tool wrappers. Ensure you have proper authorization and follow legal/ethical guidelines before running any real scans against external systems.
- LLM configuration: in `analysis_step` you can change the model name, temperature, or provider configuration if needed.

### Safety and Ethics

This project is for educational purposes. The included scanning functions are placeholders that do not perform real network or web activity. If you integrate real tools, only test against systems you own or have explicit permission to assess, and follow applicable laws and responsible disclosure practices.


