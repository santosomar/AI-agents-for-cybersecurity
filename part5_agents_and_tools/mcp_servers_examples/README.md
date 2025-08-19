# Multi-Tool Agent using LangGraph and MCP Servers

This directory contains a practical example of a Model Context Protocol (MCP) agent and server designed for cybersecurity operations. The example demonstrates how to create a server that exposes cybersecurity tools and an agent that can intelligently use these tools to perform tasks.

## Table of Contents

- [What is MCP?](#what-is-mcp)
- [Overview](#overview)
- [Components](#components)
  - [`cyber_mcp_server.py`](#cyber_mcp_serverpy)
  - [`cyber_agent.py`](#cyber_agentpy)
- [Prerequisites](#prerequisites)
- [How to Run](#how-to-run)

## What is MCP?

The [Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction) is an open, standardized framework designed to simplify and unify how AI applications—particularly large language models (LLMs) and autonomous agents—connect to external data sources, tools, and systems. Often described as the "USB-C of AI apps," MCP acts as a universal connector, allowing AI models to securely access, retrieve, and interact with a wide variety of business data, APIs, and software environments without the need for custom integrations for each new system. 

MCP operates using a client-server architecture: AI-powered applications (clients) connect to MCP servers, which expose specific capabilities such as tools (functions the agent can call), resources (structured data sources), and prompts (predefined templates). This structure enables agents to perform multi-step, context-sensitive tasks—like pulling customer records, executing workflows, or reasoning over organizational data—by leveraging a consistent protocol for accessing and updating context. 

For AI agents, MCP unlocks several key capabilities:
- **Context Sharing and Synchronization:** Agents can maintain and exchange up-to-date context—such as goals, recent actions, and environmental state—enabling more coordinated and intelligent behavior in multi-agent or collaborative scenarios.
- **Tool and Data Access:** Agents can dynamically discover and use tools or data sources exposed by MCP servers, making it easy to extend their abilities as new integrations become available.
- **Security and Governance:** MCP includes features for explicit user consent, granular permissions, and secure data access, making it suitable for enterprise environments.
- **Modularity and Scalability:** By decoupling context and integration logic from agent behavior, MCP allows new agents or data sources to be added with minimal reconfiguration, supporting rapid scaling and ecosystem growth.


## Overview

The project consists of two main components:

1.  **MCP Server (`cyber_mcp_server.py`)**: A server that exposes cybersecurity-related tools, such as an Nmap scanner and a CISA Known Exploited Vulnerabilities (KEV) catalog fetcher.
2.  **MCP Agent (`cyber_agent.py`)**: A client application that connects to the MCP server, discovers the available tools, and uses a LangGraph ReAct agent powered by an LLM to interact with these tools based on natural language commands.

This example showcases how to build a system where an AI agent can leverage external tools to perform complex cybersecurity tasks.

## Components

### `cyber_mcp_server.py`

This script implements an MCP server using `FastMCP`. It defines and exposes two tools for the agent to use.

#### Tools Exposed:

-   **`run_nmap_scan(hosts: str, arguments: str = '-sV') -> dict`**: 
    -   Runs a port scan on the specified host(s) using the `python-nmap` library.
    -   **Parameters**:
        -   `hosts`: The target IP address or domain to scan.
        -   `arguments`: Nmap command-line arguments (defaults to `-sV` for service version detection).

-   **`get_cisa_kev_catalog() -> dict`**:
    -   Fetches the latest Known Exploited Vulnerabilities (KEV) catalog from the CISA website.
    -   Returns the catalog as a JSON object.

### `cyber_agent.py`

This script sets up and runs a cybersecurity agent. It performs the following steps:

1.  **Initializes an `MultiServerMCPClient`**: Connects to the `cyber_mcp_server.py` to access its tools.
2.  **Fetches Tools**: Dynamically retrieves the list of available tools from the server.
3.  **Creates a ReAct Agent**: Uses `langgraph.prebuilt.create_react_agent` to create an agent that can reason and decide which tool to use.
4.  **Initializes an LLM**: Uses `ChatOpenAI` with the `gpt-5-mini` model as the brain of the agent.
5.  **Invokes the Agent**: Runs the agent with specific tasks, such as performing an Nmap scan and fetching the CISA KEV catalog.

## Prerequisites

Before running the agent, ensure you have the following:

1.  **Python Environment**: A working Python 3 environment.
2.  **Required Packages**: Install the necessary packages from `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```
    Key packages for this example include:
    - `langgraph`
    - `langchain-mcp-adapters`
    - `mcp`
    - `python-nmap`
    - `langchain_openai`
    - `requests`
    - `python-dotenv`


## How to Run

To run the cybersecurity agent, execute the `cyber_agent.py` script from your terminal:

```bash
python cyber_agent.py
```

The script will automatically start the `cyber_mcp_server.py` in the background, connect to it, and then run two example tasks:

1.  An Nmap scan on `127.0.0.1`.
2.  A request to fetch the CISA KEV catalog.

The agent's final responses for each task will be printed to the console.
