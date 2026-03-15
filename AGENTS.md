# AGENTS.md

## Cursor Cloud specific instructions

### Project overview
Educational Python codebase (O'Reilly course) with standalone scripts demonstrating AI agents for cybersecurity. Not a monorepo; no interconnected services. See `README.md` for the full learning path.

### Runtime
- **Python >= 3.13** is required (`pyproject.toml`). The system default may be 3.12; the update script installs 3.13 from the deadsnakes PPA.
- **uv** is the package manager (`uv.lock` + `pyproject.toml`). Run `uv sync --python python3.13` to install deps into `.venv/`.
- Run scripts with `uv run python <script.py>` to use the project venv automatically.

### Linting
No linting is configured at the root level. Use `uvx ruff check .` for basic linting. The shodan_mcp subproject has ruff/black/mypy in its own `pyproject.toml`.

### Testing
No formal test suite at the root. Two test scripts exist under `part5_agents_and_tools/mcp_servers_examples/shodan_mcp/` (`test_shodan_openapi.py`, `test_agent_setup.py`). Run with `uv run python <test_file>`.

### Running scripts
- Most scripts require `OPENAI_API_KEY` env var. Without it, ~90% of scripts will fail at startup.
- `part1_foundational_topics/huggingface_example.py` runs fully offline (DistilBERT sentiment analysis) — good for smoke-testing the environment.
- Streamlit chatbot: `uv run streamlit run part1_foundational_topics/chatbot_example.py --server.port 8501 --server.headless true`
- Optional: `SHODAN_API_KEY` for shodan MCP examples, `nmap` system binary for scanner scripts, Ollama server for local LLM examples.

### Gotchas
- PyTorch pulls CUDA/NVIDIA packages (~3GB) even on CPU-only VMs. This is normal and expected from the lockfile.
- The `.venv/` directory is created at the workspace root by `uv sync`.
- ChromaDB data is pre-committed under `part4_rag_examples/db/`; no separate database server needed.
