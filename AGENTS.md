# AGENTS.md

## Project overview

Educational Python codebase for [O'Reilly courses](https://www.oreilly.com/search/?q=omar%20santos&rows=100) by Omar Santos. Standalone scripts (no interconnected services) demonstrating AI agents for cybersecurity across five progressive parts. See `README.md` for the full learning path.

## Directory structure

```
part1_foundational_topics/   Chat models, embeddings, Streamlit chatbot, Hugging Face, Ollama
part2_prompt_templates/      Prompt engineering: templates, placeholders, chat history
part3_prompt_chaining/       LCEL chains: sequential, parallel, branching, threat hunting
part4_rag_examples/          RAG with Chroma, text splitting, embedding comparison, web scraping
part5_agents_and_tools/      Agents, LangGraph, agentic RAG, CrewAI, MCP servers
```

### Part 5 sub-directories

| Directory | Contents |
|-----------|----------|
| `agent_deep_dive/` | Chat agent with Wikipedia, docstore agent with Chroma retriever |
| `agent_deep_dive/langgraph/` | LangGraph agents: URL analysis, CISA KEV, ethical hacking, branching |
| `agentic_rag/` | LangGraph agentic RAG over SSRF data with Chroma |
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
- **uv** is the package manager (`uv.lock` + `pyproject.toml`). A legacy `requirements.txt` exists at root but `pyproject.toml` is authoritative.
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
| `part5_agents_and_tools/basic_agent_and_tools_scanner.py` | ReAct agent with nmap tool | `OPENAI_API_KEY`, `nmap` binary |
| `part5_agents_and_tools/mcp_servers_examples/cyber_mcp_server.py` | FastMCP server (nmap scan + CISA KEV) | `nmap` binary |
| `part5_agents_and_tools/mcp_servers_examples/cyber_agent.py` | MCP client agent using cyber server | `OPENAI_API_KEY`, `nmap` binary |

## Running scripts

```bash
# Install dependencies
uv sync --python python3.13

# Run any standalone script
uv run python part1_foundational_topics/huggingface_example.py

# Streamlit chatbot
uv run streamlit run part1_foundational_topics/chatbot_example.py --server.port 8501 --server.headless true

# CrewAI vulnerability management
cd part5_agents_and_tools/crewai_example/vulnerability_management
uv run run        # or: uv run train / uv run test

# Shodan MCP (from its own project dir)
cd part5_agents_and_tools/mcp_servers_examples/shodan_mcp
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

- `part5_agents_and_tools/mcp_servers_examples/shodan_mcp/test_shodan_openapi.py` — Shodan OpenAPI/mock tests
- `part5_agents_and_tools/mcp_servers_examples/shodan_mcp/test_agent_setup.py` — Environment and dependency validation

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
- `.github/instructions/` — Markdown mirrors of CodeGuard security rules

## Cursor rules

22 CodeGuard `.mdc` rules in `.cursor/rules/` covering: crypto algorithms, digital certificates, hardcoded credentials, safe C functions, API security, auth/MFA, authorization, input validation, cloud/K8s, data storage, DevOps CI/CD, file uploads, frameworks, IaC, logging, mobile, privacy, session management, supply chain, XML/serialization, and more.

Identical rules also exist in `.windsurf/rules/` (Windsurf IDE copy).

## Gotchas

- PyTorch pulls CUDA/NVIDIA packages (~3 GB) even on CPU-only machines. This is expected from the lockfile.
- The `.venv/` directory is created at the workspace root by `uv sync`.
- ChromaDB stores are pre-committed under `part4_rag_examples/db/` — no separate database setup needed.
- Some READMEs reference `rag_basics_metadata_part1.py` and `chroma_db_with_metadata/` which are not present in the current tree (may be planned or generated locally).
- No Jupyter notebooks exist in this repo — all examples are standalone `.py` scripts.
