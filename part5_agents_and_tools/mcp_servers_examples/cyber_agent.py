# LangGraph Example: MCP Client for Cybersecurity Tools
#
# This script implements a small FastAPI application that exposes a ``/scan``
# endpoint. Given an IP address, it performs a real (but limited) port scan using
# the :mod:`python-nmap` module. The goal is to illustrate how an MCP-style server
# could be structured for cybersecurity purposes.
#
# Instructor: Omar Santos @santosomar

import os
import asyncio
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

# Get the directory of the current script
script_dir = os.path.dirname(__file__)

# Construct the path to the .env file and load it
# Make sure to create a .env file in this directory
# and add your OPENAI_API_KEY to it.
dotenv_path = os.path.join(script_dir, '.env')
load_dotenv(dotenv_path=dotenv_path)

async def main():
    """Main function to run the cyber agent."""
    # The script_dir is already defined globally, so we can use it to build the server path
    server_path = os.path.join(script_dir, "cyber_mcp_server.py")

    # Initialize the MultiServerMCPClient to connect to the cyber server
    client = MultiServerMCPClient(
        {
            "cyber_tools": {
                "command": "python",
                "args": [server_path],
                "transport": "stdio",
            }
        }
    )

    print("Fetching tools from MCP server...")
    # Getting the tools from the MCP server
    tools = await client.get_tools()
    print(f"Available tools: {[tool.name for tool in tools]}")

    # Checking for API key and initializing the AI model.
    # FYI: A security best practice is to not hardcode the API key in the code or use environment variables.
    # In this case, we are using a .env file to store the API key as a quick example.
    # In a production environment, you should use a secure method to store and retrieve the API key.
    # For example, you can use a secrets manager or a secure vault.
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found. Please check your .env file.")
        return

    print("OpenAI API key found. Initializing AI model...")
    try:
        llm = ChatOpenAI(model="gpt-5-mini")
        
        # Create a ReAct agent with the fetched tools
        agent = create_react_agent(llm, tools)
        print("AI model and agent initialized successfully.")
    except Exception as e:
        print(f"Error initializing AI model or agent: {e}")
        return

    print("\n--- Running Agent with Nmap Scan ---")
    try:
        # Example 1: Using the nmap tool
        nmap_response = await agent.ainvoke(
            {"messages": [{"role": "user", "content": "run an nmap scan on 127.0.0.1 with arguments -sV"}]}
        )
        print(nmap_response['messages'][-1].content)
    except Exception as e:
        print(f"An error occurred during the Nmap scan task: {e}")

    print("\n--- Running Agent with CISA KEV Catalog ---")
    try:
        # Example 2: Using the CISA KEV catalog tool
        cisa_response = await agent.ainvoke(
            {"messages": [{"role": "user", "content": "get the latest CISA KEV catalog. Explain the latest 5 vulnerabilities in the catalog."}]}
        )
        print(cisa_response['messages'][-1].content)
    except Exception as e:
        print(f"An error occurred during the CISA KEV catalog task: {e}")

if __name__ == "__main__":
    asyncio.run(main())
