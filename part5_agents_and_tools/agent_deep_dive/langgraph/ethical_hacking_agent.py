# LangGraph Example: An Ethical Hacking Assistant Agent
#
# This script builds a more elaborate, stateful agent that can use tools
# to perform ethical hacking tasks and maintain conversation history.
#
# Instructor: Omar Santos @santosomar

import operator
import uuid
from typing import TypedDict, Annotated

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain.tools import Tool
from langgraph.prebuilt import ToolNode
import nmap

# Load environment variables
load_dotenv()

# 1. Define the Tools for our agent
# We'll create mock tools for demonstration purposes.

def nmap_scan(target: str) -> str:
    """Runs a real Nmap scan on a target IP or domain using python-nmap."""
    print(f"---TOOL: Running Nmap scan on {target}---")
    try:
        nm = nmap.PortScanner()
    except nmap.PortScannerError:
        return "Nmap not found. Please ensure the nmap command-line tool is installed and in your PATH."

    try:
        # -F for a fast scan of the most common 100 ports
        nm.scan(target, arguments='-F')
        summary = []
        for host in nm.all_hosts():
            host_summary = [f"Nmap scan report for {host} ({nm[host].hostname()})"]
            host_summary.append(f"State: {nm[host].state()}")
            for proto in nm[host].all_protocols():
                host_summary.append(f"Protocol: {proto}")
                ports = nm[host][proto].keys()
                for port in sorted(ports):
                    state = nm[host][proto][port]['state']
                    name = nm[host][proto][port]['name']
                    host_summary.append(f"  Port: {port}\tState: {state}\tService: {name}")
            summary.append("\n".join(host_summary))
        
        if not summary:
            return f"Nmap scan on {target} completed, but no hosts were found up or no ports were open."
            
        return "\n---\n".join(summary)
    except Exception as e:
        return f"An error occurred during the Nmap scan: {e}"

def search_exploitdb(query: str) -> str:
    """Simulates searching Exploit-DB for a given query (e.g., a software name)."""
    print(f"---TOOL: Searching Exploit-DB for '{query}'---")
    if "apache" in query.lower():
        return "Found exploit: Apache 2.4.49 - Path Traversal (Exploit-DB ID 50383)"
    return "No exploits found for the given query."

# Wrap the functions in the LangChain Tool class
nmap_tool = Tool(
    name="nmap_scan",
    func=nmap_scan,
    description="Runs an Nmap scan on a target IP or domain to find open ports."
)

exploitdb_tool = Tool(
    name="search_exploitdb",
    func=search_exploitdb,
    description="Searches Exploit-DB for exploits related to a software or technology."
)

tools = [nmap_tool, exploitdb_tool]

# The ToolNode is a pre-built node that executes tools.
tool_node = ToolNode(tools)

# 2. Define the Agent's State
# The state now tracks the conversation messages.
class AgentState(TypedDict):
    messages: Annotated[list, operator.add]

# 3. Define the Agent's Logic (the nodes)

# Initialize the AI model and bind the tools to it
# This allows the model to decide when to call a tool.
model = ChatOpenAI(temperature=0.2, model="gpt-5-mini").bind_tools(tools)

def should_continue(state: AgentState) -> str:
    """Conditional logic to decide whether to continue or end the workflow."""
    print("---AGENT: Checking for tool calls---")
    if isinstance(state['messages'][-1], AIMessage) and state['messages'][-1].tool_calls:
        return "tools"
    return "end"

def call_model(state: AgentState) -> dict:
    """The primary agent node. It calls the AI model to decide the next action."""
    print("---AGENT: Calling model---")
    response = model.invoke(state['messages'])
    # The response from the model is added to the list of messages
    return {"messages": [response]}

# 4. Build the Graph
workflow = StateGraph(AgentState)

# Add the nodes
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

# Set the entry point
workflow.set_entry_point("agent")

# Add the conditional edge
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        "end": END
    }
)

# Add the edge from the tool node back to the agent
# This allows the agent to process the tool's output.
workflow.add_edge("tools", "agent")

# 5. Add the Checkpointer and Compile the Graph
memory_saver = MemorySaver()
app = workflow.compile(checkpointer=memory_saver)

# 6. Run the Agent
config = {"configurable": {"thread_id": str(uuid.uuid4())}}

# First interaction
print("---RUN 1: User asks to scan a target---")
user_input = "Can you run a scan on localhost?"
result = app.invoke({"messages": [HumanMessage(content=user_input)]}, config=config)
print(f"Agent Response: {result['messages'][-1].content}")

# Second interaction
print("\n---RUN 2: User asks to search for exploits---")
user_input = "Great. Now, can you check for any Apache exploits?"
result = app.invoke({"messages": [HumanMessage(content=user_input)]}, config=config)
print(f"Agent Response: {result['messages'][-1].content}")

# Third interaction (no tool use)
print("\n---RUN 3: User asks to use an exploit---")
user_input = "How can I use that exploit?"
result = app.invoke({"messages": [HumanMessage(content=user_input)]}, config=config)
print(f"Agent Response: {result['messages'][-1].content}")

# Fourth interaction (no tool use)
print("\n---RUN 4: User asks to provide mitigations---")
user_input = "Can you provide recommendations on how to mitigate this?"
result = app.invoke({"messages": [HumanMessage(content=user_input)]}, config=config)
print(f"Agent Response: {result['messages'][-1].content}")

# Verify the final state
print("\n---Final Conversation History---")
final_state = app.get_state(config)
for message in final_state.values['messages']:
    if isinstance(message, HumanMessage):
        print(f"Human: {message.content}")
    else:
        print(f"AI: {message.content}")
