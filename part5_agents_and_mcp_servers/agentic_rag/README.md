# Agentic RAG Example with LangGraph

This folder contains a simplified example demonstrating how to build an agentic
Retrieval Augmented Generation (RAG) workflow using **LangGraph**. The example is
inspired by the [LangGraph agentic RAG tutorial](https://langchain-ai.github.io/langgraph/tutorials/rag/langgraph_agentic_rag/)
but the data and scenario focus on cybersecurity.

The script `agentic_rag_example.py` creates a small vector store from a text file
containing information about Server-Side Request Forgery (SSRF) vulnerabilities
and prevention techniques. An agent built with LangGraph decides whether it
needs to search the vector store or if it already has enough information to
answer the user's question.

## Project Structure
```
part5_agents_and_mcp_servers/
└── agentic_rag/
    ├── agentic_rag_example.py
    └── db/
        └── chroma_db/    # Vector store created on first run
```

## Prerequisites
- Python 3.x
- Required packages:
  ```bash
  pip install langchain langgraph langchain-openai chromadb python-dotenv
  ```
- An OpenAI API key set in your environment variables or in a `.env` file

## Usage
1. Ensure the dependencies are installed and the `OPENAI_API_KEY` environment
   variable is set.
2. Run the example:
   ```bash
   python agentic_rag_example.py
   ```
3. The agent will load the SSRF dataset, create (or load) the vector store, and
   answer a sample question: `How can I prevent SSRF attacks?`

Feel free to modify the question or dataset to experiment with other
cybersecurity topics.
