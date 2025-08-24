# AI Agents for Cybersecurity

This repository contains resources and materials for [several courses](https://www.oreilly.com/search/?q=omar%20santos&rows=100) by [Omar Santos](https://www.linkedin.com/in/santosomar/).

# Repository Structure
The repository is structured with five comprehensive parts covering the spectrum from basic AI concepts to advanced agentic implementations:

- **`part1_foundational_topics/`**: Foundational examples covering chat models, embeddings (with TensorFlow Projector visualization), interactive chatbots, and integration with various model providers (OpenAI, Hugging Face, Ollama)
- **`part2_prompt_templates/`**: Advanced prompt engineering techniques, template systems, and structured prompting strategies for cybersecurity applications
- **`part3_prompt_chaining/`**: Sophisticated prompt chaining workflows using LangChain Expression Language (LCEL), including branching chains, parallel processing, and conditional logic for security incident analysis and threat hunting
- **`part4_rag_examples/`**: Comprehensive Retrieval Augmented Generation implementations with vector databases (Chroma), text splitting strategies, embedding comparisons, metadata handling, and web scraping
- **`part5_agents_and_tools/`**: Advanced AI agents, tools integration, LangGraph workflows, agentic RAG, and Model Context Protocol (MCP) implementations for cybersecurity automation

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
- **Vector Database Management**: Chroma vector store creation and persistence (`basic_rag_part1.py`, `basic_rag_part2.py`)
- **Text Splitting Strategies**: Character, sentence, token, and recursive splitting techniques (`text_splitting_deep_dive.py`)
- **Embedding Comparisons**: OpenAI vs. Hugging Face embedding models (`embedding_deep_dive.py`)
- **Metadata Integration**: Source tracking and metadata-rich vector stores (`rag_basics_metadata_part1.py`)
- **Web Scraping**: Dynamic content ingestion and processing (`web_scrape_basic.py`)
- **Cost Optimization**: Embedding cost calculation utilities (`utils/embedding_cost_calculator.py`)
- **Cybersecurity Data**: SSRF vulnerability analysis and Tesla security data examples

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
- **Model Context Protocol (MCP)**: FastAPI-based security servers with port scanning (`mcp_servers_examples/`)


**Note**: This will continue to be a **living set of resources** with updates and new content added regularly. 

## Contact Information

For any queries or further information, please contact:

**Omar Santos**
- X: [@santosomar](https://x.com/santosomar)
- LinkedIn: [/santosomar](https://www.linkedin.com/in/santosomar/)
