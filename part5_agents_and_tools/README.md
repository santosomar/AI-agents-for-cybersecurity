# Agents and Tools Examples

This directory contains advanced examples demonstrating the implementation and use of AI agents and tools in cybersecurity applications. The examples showcase various agent architectures, from basic tool usage to complex agentic workflows using LangGraph.

## Directory Structure

### Basic Examples
- `basic_agent_and_tools.py`: A foundational example showing:
  - Basic agent setup with ReAct framework
  - Tool creation and integration
  - ChatOpenAI model interaction
  - Simple task execution patterns

- `basic_agent_and_tools_scanner.py`: Security-focused implementation featuring:
  - Network scanning capabilities
  - Security tool integration
  - Safe execution patterns

### Agent Deep Dive (`agent_deep_dive/`)

#### Core Agent Examples
- `agent_chat.py`: Advanced chat agent featuring:
  - Conversation memory management
  - Wikipedia search integration
  - Structured chat prompts
  - Error handling and logging

- `agent_docstore.py`: Document-aware agent with:
  - Document storage integration
  - Content retrieval capabilities
  - Context-aware responses

#### LangGraph Integration (`langgraph/`)
- `branching_conditional_logic.py`: Demonstrates:
  - Complex decision workflows
  - State management in multi-step processes
  - Conditional branching logic
  - Integration with LangGraph framework

### Agentic RAG Implementation (`agentic_rag/`)
- Main implementation in `agentic_rag_example.py`:
  - Vector store integration
  - SSRF vulnerability analysis
  - Dynamic information retrieval
  - Intelligent query processing
- Includes detailed README with implementation specifics

### MCP Servers (`mcp_servers_examples/`)
- `mcp_server.py`: FastAPI-based security server:
  - Port scanning functionality
  - API endpoint management
  - Security assessment tools
- Comprehensive README with setup and usage instructions

## Key Features

- **Agent Architectures**: Multiple agent implementations from basic to complex
- **Tool Integration**: Examples of integrating security tools and APIs
- **Memory Management**: Conversation and context retention techniques
- **Workflow Management**: LangGraph-based complex decision flows
- **Security Focus**: Cybersecurity-specific implementations and use cases

## Prerequisites

- Python 3.x
- LangChain and LangGraph
- OpenAI API access
- Additional security tools as required by specific examples

## Getting Started

1. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set up environment variables in `.env`:
   - OpenAI API key
   - Other required API credentials
3. Review individual README files in subdirectories
4. Start with basic examples before moving to complex implementations

## Usage Examples

Each subdirectory contains specific usage examples and documentation. Start with:
1. Basic agent examples to understand core concepts
2. Move to agent deep dive for advanced features
3. Explore agentic RAG for information retrieval
4. Study MCP servers for API integration

## Contributing

Contributions are welcome! Please feel free to submit pull requests with:
- New agent examples
- Additional security tools
- Improved documentation
- Bug fixes and optimizations

## Usage

Run the script using Python:
```bash
python basic_agent_and_tools.py
```

The script will:
1. Load the necessary environment variables
2. Create a custom time tool
3. Initialize the LangChain agent with the ReAct framework
4. Execute a test query asking for the current time
5. Display the response


## Features

- Custom tool implementation
- Integration with OpenAI's GPT-4 model
- ReAct framework implementation
- Verbose output for debugging and understanding agent behavior

## Note

The example uses `gpt-5-mini` as the model. Make sure to update the model name in the code if you want to use a different OpenAI model.


---

## Basic Agent with Network Scanning Tools

The script `basic_agent_and_tools_scanner.py` demonstrates the implementation of a LangChain agent equipped with basic network scanning capabilities using nmap. The agent combines OpenAI's language models with custom tools to perform network scanning operations and time-related queries.

## Features

- Custom agent using LangChain's ReAct (Reason and Action) framework
- Integration with OpenAI's GPT models
- Network scanning capabilities using nmap
- Current time retrieval functionality

## Prerequisites

- Python 3.x
- OpenAI API key (set in `.env` file)
- Required Python packages:
  ```bash
  pip install python-nmap langchain langchain-openai python-dotenv pydantic
  ```
- Nmap installed on your system

## Environment Setup

1. Create a `.env` file in the project root
2. Add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Available Tools

1. **Time Tool**
   - Returns the current time in H:MM AM/PM format
   - Usage: Ask the agent about the current time

2. **Scanner Tool**
   - Performs network scanning using nmap
   - Input: IP address or range
   - Returns: List of discovered hosts

## Usage Example

```python
# Initialize and run the agent
response = agent_executor.invoke({"input": "Scan the IP address 8.8.8.8"})
```

## Security Considerations

- This script performs network scanning operations which should only be used on networks you have permission to scan
- Always follow responsible security testing practices and applicable laws and regulations
- Be cautious when scanning IP addresses, as unauthorized scanning may be illegal in some jurisdictions

