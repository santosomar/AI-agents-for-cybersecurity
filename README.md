# AI Agents for Cybersecurity

Hands-on code, labs, and reference material by [Omar Santos](https://www.linkedin.com/in/santosomar/) for building, securing, and operating AI agents in cybersecurity.

## Where this repository is used

This is the companion repository for several of Omar's training programs and publications:

- **Pearson live trainings**: instructor-led sessions on AI agents, agentic AI security, RAG, and MCP
- **Video courses**: on-demand courses from Pearson and on the [O'Reilly learning platform](https://www.oreilly.com/search/?q=omar%20santos&rows=100)
- **O'Reilly live events**: live courses and workshops on the O'Reilly platform
- **Books**: code examples and labs referenced in several of Omar's books on AI and cybersecurity

If you came here from a training or a book, each part below lines up with a module or chapter. The scripts stand alone, so you can jump straight to the part you need.

## Quick start

```bash
# Python 3.13+ and uv are required
uv sync --python python3.13

# Smoke-test the environment (runs offline)
uv run python part1_foundational_topics/huggingface_example.py

# Most other scripts need an OpenAI API key in your environment or a local .env file
export OPENAI_API_KEY="your-key-here"
```

Never commit API keys. `.env` is already in `.gitignore`.

# Repository Structure
The repository is structured with seven comprehensive parts covering the spectrum from basic AI concepts to advanced agentic implementations:

- **`part1_foundational_topics/`**: Foundational examples covering chat models, embeddings (with TensorFlow Projector visualization), interactive chatbots, and integration with various model providers (OpenAI, Hugging Face, Ollama)
- **`part2_prompt_templates/`**: Advanced prompt engineering techniques, template systems, and structured prompting strategies for cybersecurity applications
- **`part3_prompt_chaining/`**: Sophisticated prompt chaining workflows using LangChain Expression Language (LCEL), including branching chains, parallel processing, and conditional logic for security incident analysis and threat hunting
- **`part4_rag_examples/`**: Comprehensive Retrieval Augmented Generation implementations with vector databases (Chroma), text splitting strategies, embedding comparisons, metadata handling, and web scraping
- **`part5_agents_and_mcp_servers/`**: Advanced AI agents, tools integration, LangGraph workflows, agentic RAG, and Model Context Protocol (MCP) implementations for cybersecurity automation
- **`part6_agentic_frameworks/`**: Security-team guides to six ready-made agentic frameworks (OpenClaw, Hermes, Agent Zero, OpenHands, Paperclip, Buzz): what each is, where it helps, and where it should stay out
- **`part7_tokenomics/`**: What agents cost to run and how to measure it: context compounding, prompt caching, model routing, compaction, tool-schema overhead, batch processing, per-task budgets, and cost per accepted outcome

## Comprehensive Learning Path
This repository provides a structured learning journey covering cutting-edge AI agent technologies and their applications in cybersecurity operations.

### Part 1: Foundational Topics - Basic AI Interactions
- **Chat Models**: Basic chat interactions with OpenAI and LangChain (`chat_model_basic.py`)
- **Interactive Chatbots**: Complete Streamlit-based chatbot with conversation history (`chatbot_example.py`)
- **Embeddings**: Text embedding generation and visualization with TensorFlow Projector using CVE data (`embeddings/`)
  - 1000 CVE embeddings and metadata for hands-on visualization
  - Step-by-step guide for using TensorFlow's Embedding Projector
- **Hugging Face Integration**: Sentiment analysis with DistilBERT (`huggingface_example.py`)
- **Ollama Integration**: Local model deployment with streaming and multimodal capabilities (`ollama/`)
- **Document Processing**: Multimodal document analysis and chunking strategies (`chunking_and_images.md`)

### Part 2: Prompt Engineering and Context Engineering Mastery
- Advanced prompt template design and optimization
- System message crafting for cybersecurity contexts
- Multi-variable prompt construction and placeholders
- Message history management and conversation flow
- Chain-of-Thought, Tree-of-Thought, and ReAct techniques
- Meta prompting and iterative refinement strategies

### Part 3: Intelligent Prompt Chaining
- LangChain Expression Language (LCEL) fundamentals
- Sequential and parallel chain orchestration
- Conditional branching for dynamic decision-making
- Security incident analysis workflows
- Threat hunting automation with adaptive chains
- Multi-step reasoning for complex cybersecurity tasks

### Part 4: Advanced RAG Implementations
- **Vector Database Management**: Multi-document Chroma vector store creation, persistence, and source metadata (`basic_rag_part1.py`, `basic_rag_part2.py`)
- **End-to-End RAG Chain**: Retriever, prompt, and LLM combined with LCEL (`basic_rag_part3.py`)
- **Text Splitting Strategies**: Character, sentence, token, and recursive splitting techniques (`text_splitting_deep_dive.py`)
- **Embedding Comparisons**: OpenAI vs. Hugging Face embedding models (`embedding_deep_dive.py`)
- **Web Scraping**: Dynamic content ingestion and processing (`web_scrape_basic.py`)
- **Cost Optimization**: Embedding cost calculation utilities (`utils/embedding_cost_calculator.py`)
- **Cybersecurity Data**: SSRF vulnerability analysis and Tesla security data examples
- **RAG Failure Modes Reference**: [WFGY 16 Problem Map](https://github.com/onestardao/WFGY/blob/main/ProblemMap/README.md) — compact checklist of common RAG and long-context failure modes with minimal repros and concrete mitigation patterns that can help harden security-focused RAG pipelines and agents.

### Part 5: Next-Generation AI Agents & Tools
- **Basic Agent Frameworks**: ReAct agents with tool integration (`basic_agent_and_tools.py`)
- **Security-Focused Agents**: Network scanning and security tool integration (`basic_agent_and_tools_scanner.py`)
- **Advanced Agent Architectures**: 
  - Chat agents with Wikipedia integration (`agent_deep_dive/agent_chat.py`)
  - Document-aware agents with storage capabilities (`agent_deep_dive/agent_docstore.py`)
- **LangGraph Workflows**: Complex decision workflows with state management (`langgraph/`)
  - Conditional branching logic and multi-step processes
  - CISA KEV agent and ethical hacking automation
- **Agentic RAG**: Reasoning-based real-time data retrieval with SSRF analysis (`agentic_rag/`)
- **Attack Surface Management**: LangGraph recon → scan → analysis → report workflow (`asm_example/`)
- **Multi-Agent Crews**: CrewAI vulnerability management crew with nmap and CVE tools (`crewai_example/`)
- **Deep Agents**: Autonomous SOC agent with planning and subagents built on DeepAgents (`deepagents_example/`)
- **Model Context Protocol (MCP)**: FastMCP security servers (nmap scanning, CISA KEV, Shodan) and MCP client agents (`mcp_servers_examples/`)

### Part 6: Agentic Frameworks for Security Teams
What each framework is, where it helps a security team, where it should stay out, and how to harden it. The overview also includes a side-by-side comparison, a "which one for which job" guide, a map of the 2026 CVEs and supply-chain incidents, and lab exercises:
- **OpenClaw**: Personal assistant you message in your chat apps (`openclaw/`)
- **Hermes**: Self-improving agent from Nous Research that saves workflows as skills (`hermes/`)
- **Agent Zero**: General-purpose agent with its own Kali Linux container (`agent_zero/`)
- **OpenHands**: Autonomous software engineer, issue in and pull request out (`openhands/`)
- **Paperclip**: Control plane for a "company" of agents (`paperclip/`)
- **Buzz**: Block's shared workspace for people and agents on a self-hosted relay (`buzz/`)

### Part 7: Tokenomics for Security Agents
Where the money goes in an agent, and the metric that matters (cost per accepted outcome, not cost per token):
- **Context Compounding**: Why agent cost grows with the square of task length, and how compaction bends the curve (`01_context_growth.py`)
- **Prompt Caching**: Provider mechanics, TTL selection, break-even math, prompt layout, and a live cache-hit check (`02_prompt_caching.py`, `03_live_cache_check.py`)
- **Cost per Outcome**: Model + runtime + human review, divided by acceptance rate (`04_cost_per_outcome.py`)
- **Model Routing**: Intent routers, cascades, and the escalation trap (`05_model_routing.py`)
- **Fewer Tools**: Tool-schema token overhead, pruning by intent, and capping tool output (`06_tool_schema_overhead.py`)
- **Budgets**: Per-task token, cost, and loop ceilings as a denial-of-wallet defense (`07_token_budget_guard.py`)
- **Batch**: Offline triage at half price with the Batch API (`08_batch_triage.py`)
- **Cyber Index**: Using a cost-aware defensive security benchmark to choose models (`docs/07_cyber_index.md`)


**Note**: This is a **living set of resources**. Content is updated regularly as the tools, models, and threats change, so the code may be newer than the version shown in a recorded video or a printed book. If something in a book or recording no longer matches, the version in this repository is the current one.

## Responsible use

Several examples (nmap scanning, Agent Zero on Kali Linux, attack surface management, ethical hacking agents) can act against real systems. Run them only against systems you own or are explicitly authorized to test, ideally in an isolated lab.

## Contact Information

For any queries or further information, please contact:

**Omar Santos**
- X: [@santosomar](https://x.com/santosomar)
- LinkedIn: [/santosomar](https://www.linkedin.com/in/santosomar/)
