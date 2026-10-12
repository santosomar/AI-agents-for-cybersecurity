# AGENTS.md

## Project overview

Educational Python codebase for [O'Reilly courses](https://www.oreilly.com/search/?q=omar%20santos&rows=100) by Omar Santos. Standalone scripts (no interconnected services) demonstrating AI agents for cybersecurity across seven progressive parts. See `README.md` for the full learning path.

## Directory structure

```
part1_foundational_topics/   Chat models, embeddings, Streamlit chatbot, Hugging Face, Ollama
part2_prompt_templates/      Prompt engineering: templates, placeholders, chat history
part3_prompt_chaining/       LCEL chains: sequential, parallel, branching, threat hunting
part4_rag_examples/          RAG with Chroma, text splitting, embedding comparison, web scraping
part5_agents_and_mcp_servers/ Agents, LangGraph, agentic RAG, CrewAI, MCP servers
part6_agentic_frameworks/    Docs only: OpenClaw, Hermes, Agent Zero, OpenHands, Paperclip, Buzz (one folder each)
part7_tokenomics/            Agent cost: caching, routing, compaction, tool overhead, batch, budgets, cost per outcome
```

### Part 7 notes

- All scripts share `part7_tokenomics/pricing.yaml` (Oct 2026 price snapshot) via `token_math.py`. Update prices in the YAML, not in scripts.
- Scripts 01, 02, 04, 05, 06, 08 run offline. `03_live_cache_check.py`, `07_token_budget_guard.py --live`, and `08_batch_triage.py --submit` need `OPENAI_API_KEY`.
- Generated charts and batch JSONL go to `part7_tokenomics/output/` (gitignored). Write-ups live in `part7_tokenomics/docs/`.

### Part 5 sub-directories

| Directory | Contents |
|-----------|----------|
| `agent_deep_dive/` | Chat agent with Wikipedia, docstore agent with Chroma retriever |
| `agent_deep_dive/langgraph/` | LangGraph agents: URL analysis, CISA KEV, ethical hacking, branching |
| `agentic_rag/` | LangGraph agentic RAG over SSRF data with Chroma |
| `deepagents_example/` | DeepAgents SOC supervisor with planning, virtual filesystem, and subagents |
| `asm_example/` | Attack surface management graph (recon → scan → analysis → exploit/report) |
| `crewai_example/vulnerability_management/` | CrewAI crew with nmap/CVE tools (`pyproject.toml` with `crewai` scripts) |
| `mcp_servers_examples/` | FastMCP cyber server, Shodan MCP, Splunk MCP (README only) |
| `mcp_servers_examples/shodan_mcp/` | Self-contained MCP project with its own `pyproject.toml` and tests |

### Data and persistence

- `part1_foundational_topics/embeddings/` — CVE embedding TSVs for clustering/TensorFlow Projector.
- `part4_rag_examples/data/` — `ssrf.txt`, `llm_cheatsheet.md`, `tesla.json`, `tesla_hostnames.txt`.
- `part4_rag_examples/db/` — Pre-committed Chroma SQLite stores (`chroma_db_security/`, `hacker_training/`). No separate database server needed.

## Runtime

- **Python >= 3.13** is required (`pyproject.toml`).
- **uv** is the package manager (`uv.lock` + `pyproject.toml`). A legacy `requirements.txt` exists at root (unpinned names mirrored from `pyproject.toml`) but `pyproject.toml` is authoritative.
- Install: `uv sync --python python3.13` (creates `.venv/` at workspace root).
- Run scripts: `uv run python <script.py>`.

## Environment variables

| Variable | Required by | Notes |
|----------|-------------|-------|
| `OPENAI_API_KEY` | ~90% of scripts | Without it most scripts fail at startup |
| `SHODAN_API_KEY` | Shodan MCP examples | See `shodan_mcp/env_template.txt` for template |

**System dependencies (optional):**
- `nmap` binary — needed by `basic_agent_and_tools_scanner.py`, `ethical_hacking_agent.py`, CrewAI vulnerability management
- Ollama server — needed by `part1_foundational_topics/ollama/` examples

No `.env` files are committed (`.env` is gitignored). Scripts use `python-dotenv` to load from `.env` if present.

## Key scripts quick reference

| Script | What it does | Special requirements |
|--------|-------------|---------------------|
| `part1_foundational_topics/huggingface_example.py` | DistilBERT sentiment analysis | Runs fully offline — best for smoke-testing the environment |
| `part1_foundational_topics/chatbot_example.py` | Streamlit cybersecurity tutor chatbot | `OPENAI_API_KEY` |
| `part1_foundational_topics/embeddings/clustering.py` | K-means + PCA/t-SNE on CVE embeddings | Offline (uses bundled TSVs) |
| `part4_rag_examples/basic_rag_part1.py` | Builds Chroma vector store from `data/` | `OPENAI_API_KEY` |
| `part5_agents_and_mcp_servers/basic_agent_and_tools_scanner.py` | ReAct agent with nmap tool | `OPENAI_API_KEY`, `nmap` binary |
| `part5_agents_and_mcp_servers/mcp_servers_examples/cyber_mcp_server.py` | FastMCP server (nmap scan + CISA KEV) | `nmap` binary |
| `part5_agents_and_mcp_servers/mcp_servers_examples/cyber_agent.py` | MCP client agent using cyber server | `OPENAI_API_KEY`, `nmap` binary |

## Running scripts

```bash
# Install dependencies
uv sync --python python3.13

# Run any standalone script
uv run python part1_foundational_topics/huggingface_example.py

# Streamlit chatbot
uv run streamlit run part1_foundational_topics/chatbot_example.py --server.port 8501 --server.headless true

# CrewAI vulnerability management
cd part5_agents_and_mcp_servers/crewai_example/vulnerability_management
uv run run        # or: uv run train / uv run test

# Shodan MCP (from its own project dir)
cd part5_agents_and_mcp_servers/mcp_servers_examples/shodan_mcp
uv sync --extra agent --extra dev
uv run python shodan_mcp.py
```

## Linting

No linting is configured at the root level. For ad-hoc checks:

```bash
uvx ruff check .
```

The `shodan_mcp` subproject has ruff/black/mypy in its own `pyproject.toml`.

## Testing

No formal test suite or pytest configuration at the root. Test files exist only in the Shodan MCP subproject:

- `part5_agents_and_mcp_servers/mcp_servers_examples/shodan_mcp/test_shodan_openapi.py` — Shodan OpenAPI/mock tests
- `part5_agents_and_mcp_servers/mcp_servers_examples/shodan_mcp/test_agent_setup.py` — Environment and dependency validation

Run with: `uv run python <test_file>`.

The CrewAI project also exposes a `test` CLI entrypoint (`uv run test`) but it is not a standard unit test.

## MCP servers

Two in-repo FastMCP servers (stdio transport):

1. **Cyber MCP** (`mcp_servers_examples/cyber_mcp_server.py`) — Tools: `run_nmap_scan`, `get_cisa_kev_catalog`
2. **Shodan MCP** (`mcp_servers_examples/shodan_mcp/shodan_mcp.py`) — Wraps Shodan REST API as MCP tools via OpenAPI spec; requires `SHODAN_API_KEY`

Client scripts (`cyber_agent.py`, `ethical_hacking_agent.py`) use `langchain-mcp-adapters` `MultiServerMCPClient` to connect over stdio.

The `splunk-mcp/` directory contains only a README with conceptual examples — no runnable server.

## CI / GitHub

- `.github/workflows/greetings.yml` — Greets new contributors
- `.github/workflows/assign_pr.yml` — Auto-assigns PRs
- `.github/dependabot.yml` — Dependency update automation
- `.github/instructions/` — GitHub Copilot copy of the CodeGuard security rules
- `.github/agents/codeguard-reviewer.agent.md` — Copilot CodeGuard reviewer agent (SARIF output)

## Cursor rules

[Project CodeGuard](https://github.com/cosai-oasis/project-codeguard) v1.5.0 — 23 `.mdc` rules in `.cursor/rules/`. `codeguard-1-*` rules are always applied (crypto algorithms, digital certificates, hardcoded credentials); `codeguard-0-*` rules apply by context: safe C functions, MCP security, API security, auth/MFA, authorization, input validation, cloud/K8s, data storage, DevOps CI/CD, file uploads, frameworks, IaC, logging, mobile, privacy, session management, supply chain, XML/serialization, and more.

`.cursor/agents/codeguard-reviewer.md` is a CodeGuard reviewer subagent that emits SARIF findings on explicit request.

Identical rules also exist in `.windsurf/rules/` (Windsurf) and `.github/instructions/` (Copilot). Claude Code and Codex get the same rules packaged as a `codeguard` skill: `.claude/skills/codeguard/` + `.claude/agents/codeguard-reviewer.md` (Claude Code) and `.agents/skills/codeguard/` + `.codex/agents/codeguard-reviewer.toml` (Codex). To update, replace them with the per-agent ZIPs from the [upstream releases](https://github.com/cosai-oasis/project-codeguard/releases).

## Gotchas

- PyTorch pulls CUDA/NVIDIA packages (~3 GB) even on CPU-only machines. This is expected from the lockfile.
- The `.venv/` directory is created at the workspace root by `uv sync`.
- ChromaDB stores are pre-committed under `part4_rag_examples/db/` — no separate database setup needed.
- LangChain 1.x removed the legacy `langchain.*` modules. Import runnables, prompts, parsers, and tools from `langchain_core`; text splitters from `langchain_text_splitters`; and `AgentExecutor`, `hub`, memory, and classic chains from `langchain_classic`. `from langchain.agents import create_agent` is the 1.x agent API.
- No Jupyter notebooks exist in this repo — all examples are standalone `.py` scripts.
