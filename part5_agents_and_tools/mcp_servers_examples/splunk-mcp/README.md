# Integrating Splunk MCP Server with LangChain and LangGraph

Here's a comprehensive example showing how to use the Splunk MCP server to build a SOC analyst agent that can query Splunk data using natural language.

## Example 1: Basic Splunk MCP Connection with LangChain

```python
from langchain_openai import ChatOpenAI

# Initialize the LLM with Splunk MCP server
llm = ChatOpenAI(model="gpt-4o", output_version="responses/v1")

# Bind the Splunk MCP server as a tool
llm_with_splunk = llm.bind_tools([
    {
        "type": "mcp",
        "server_label": "splunk",
        "server_url": "https://your-splunk-instance.splunkcloud.com/mcp",
        "require_approval": {
            "always": {
                # Require approval for queries that might be expensive
                "tool_names": ["run_splunk_query"]
            }
        }
    }
])

# Simple query example
response = llm_with_splunk.invoke(
    "What indexes do I have access to in Splunk?"
)
print(response.content)
```

---

## Example 2: Full LangGraph SOC Agent with Splunk MCP

This example creates an autonomous SOC analyst that uses Splunk as its primary data source:

```python
from typing import TypedDict, Annotated, List, Optional
from datetime import datetime
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import operator
import json

# ============================================================================
# State Definition
# ============================================================================

class SplunkSOCState(TypedDict):
    """State for the Splunk-powered SOC agent."""
    # Investigation context
    query: str                                    # Natural language query from analyst
    investigation_id: str
    
    # Splunk interaction tracking
    spl_queries: Annotated[List[str], operator.add]    # SPL queries generated/executed
    query_results: Annotated[List[dict], operator.add]  # Results from Splunk
    
    # Analysis
    findings: Annotated[List[str], operator.add]
    threat_indicators: List[str]
    
    # Workflow control
    messages: Annotated[List, operator.add]
    phase: str  # understand, query, analyze, report
    iteration: int
    max_iterations: int
    
    # Output
    report: Optional[str]
    requires_approval: bool
    pending_approval_id: Optional[str]

# ============================================================================
# LLM with Splunk MCP
# ============================================================================

def create_splunk_llm(splunk_mcp_url: str, require_query_approval: bool = True):
    """
    Create an LLM instance connected to Splunk MCP server.
    
    Args:
        splunk_mcp_url: URL of your Splunk MCP server
        require_query_approval: Whether to require human approval for queries
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0, output_version="responses/v1")
    
    approval_config = "never"
    if require_query_approval:
        approval_config = {
            "always": {
                "tool_names": ["run_splunk_query"]  # Approval for data-retrieving queries
            }
        }
    
    return llm.bind_tools([
        {
            "type": "mcp",
            "server_label": "splunk",
            "server_url": splunk_mcp_url,
            "require_approval": approval_config
        }
    ])

# Initialize the LLM
SPLUNK_MCP_URL = "https://your-instance.splunkcloud.com/mcp"
splunk_llm = create_splunk_llm(SPLUNK_MCP_URL, require_query_approval=False)

# ============================================================================
# Workflow Nodes
# ============================================================================

def understand_query_node(state: SplunkSOCState) -> SplunkSOCState:
    """
    Understand the analyst's query and plan the investigation.
    Uses Splunk MCP to understand available data sources.
    """
    system_prompt = """You are an expert SOC analyst working with Splunk.
    
    The analyst has asked: {query}
    
    Your task:
    1. Use get_indexes to understand what data is available
    2. Use get_metadata to identify relevant sources and sourcetypes
    3. Plan which Splunk queries will help answer the question
    
    Think step by step about what data you need.
    """
    
    messages = [
        SystemMessage(content=system_prompt.format(query=state['query'])),
        HumanMessage(content="First, explore the available data sources to plan the investigation.")
    ]
    
    response = splunk_llm.invoke(messages)
    
    return {
        **state,
        'phase': 'generate_spl',
        'messages': [response],
        'iteration': state['iteration'] + 1
    }

def generate_spl_node(state: SplunkSOCState) -> SplunkSOCState:
    """
    Generate optimized SPL queries using Splunk's AI-powered tools.
    """
    system_prompt = """You are an expert SOC analyst generating Splunk queries.
    
    Original question: {query}
    
    Previous context:
    {context}
    
    Your task:
    1. Use generate_spl to create SPL from the natural language question
    2. Use optimize_spl to improve query performance
    3. Use explain_spl to verify the query does what we need
    
    Generate efficient, security-focused queries.
    """
    
    context = "\n".join([str(m) for m in state['messages'][-3:]])
    
    messages = [
        SystemMessage(content=system_prompt.format(
            query=state['query'],
            context=context
        )),
        HumanMessage(content="Generate and optimize the SPL query for this investigation.")
    ]
    
    response = splunk_llm.invoke(messages)
    
    # Extract any SPL from the response
    new_spl = []
    if hasattr(response, 'tool_calls') and response.tool_calls:
        for tool_call in response.tool_calls:
            if tool_call.get('name') in ['generate_spl', 'optimize_spl']:
                # Track the SPL being generated
                new_spl.append(json.dumps(tool_call.get('args', {})))
    
    return {
        **state,
        'phase': 'execute_query',
        'spl_queries': new_spl,
        'messages': state['messages'] + [response],
        'iteration': state['iteration'] + 1
    }

def execute_query_node(state: SplunkSOCState) -> SplunkSOCState:
    """
    Execute the SPL queries against Splunk.
    """
    system_prompt = """You are executing Splunk queries for a security investigation.
    
    Original question: {query}
    
    Generated SPL queries:
    {spl_queries}
    
    Now use run_splunk_query to execute these queries and retrieve the results.
    Analyze the results for security-relevant findings.
    """
    
    messages = [
        SystemMessage(content=system_prompt.format(
            query=state['query'],
            spl_queries="\n".join(state['spl_queries'])
        )),
        HumanMessage(content="Execute the queries and analyze the results.")
    ]
    
    response = splunk_llm.invoke(messages)
    
    # Check for approval requests
    requires_approval = False
    pending_id = None
    
    if hasattr(response, 'content') and isinstance(response.content, list):
        for block in response.content:
            if isinstance(block, dict) and block.get('type') == 'mcp_approval_request':
                requires_approval = True
                pending_id = block.get('id')
                break
    
    return {
        **state,
        'phase': 'analyze' if not requires_approval else 'awaiting_approval',
        'messages': state['messages'] + [response],
        'requires_approval': requires_approval,
        'pending_approval_id': pending_id,
        'iteration': state['iteration'] + 1
    }

def analyze_results_node(state: SplunkSOCState) -> SplunkSOCState:
    """
    Analyze query results and identify threats.
    """
    system_prompt = """You are an expert SOC analyst analyzing Splunk query results.
    
    Investigation question: {query}
    
    Query results and context:
    {context}
    
    Your task:
    1. Identify any security threats or anomalies
    2. Correlate events to build a timeline
    3. Determine if this is a true positive or false positive
    4. Use ask_splunk_question for any additional context needed
    
    Provide clear, actionable findings.
    """
    
    context = "\n".join([str(m.content)[:500] for m in state['messages'][-5:]])
    
    messages = [
        SystemMessage(content=system_prompt.format(
            query=state['query'],
            context=context
        )),
        HumanMessage(content="Analyze the results and provide your security assessment.")
    ]
    
    response = splunk_llm.invoke(messages)
    
    # Extract findings
    findings = [f"Analysis at {datetime.utcnow().isoformat()}: {response.content[:500]}"]
    
    return {
        **state,
        'phase': 'report',
        'findings': findings,
        'messages': state['messages'] + [response],
        'iteration': state['iteration'] + 1
    }

def generate_report_node(state: SplunkSOCState) -> SplunkSOCState:
    """
    Generate the final investigation report.
    """
    report = f"""
================================================================================
                    SPLUNK SECURITY INVESTIGATION REPORT
================================================================================
Generated: {datetime.utcnow().isoformat()}Z
Investigation ID: {state['investigation_id']}

ORIGINAL QUERY:
{state['query']}

SPL QUERIES EXECUTED:
{chr(10).join(['  - ' + q for q in state['spl_queries']])}

FINDINGS:
{chr(10).join(['  • ' + f for f in state['findings']])}

THREAT INDICATORS:
{chr(10).join(['  ⚠ ' + t for t in state.get('threat_indicators', ['None identified'])])}
================================================================================
"""
    
    return {
        **state,
        'phase': 'complete',
        'report': report,
        'iteration': state['iteration'] + 1
    }

# ============================================================================
# Build the Graph
# ============================================================================

def route_after_execute(state: SplunkSOCState) -> str:
    """Route based on whether approval is needed."""
    if state.get('requires_approval'):
        return 'await_approval'
    return 'analyze'

def build_splunk_soc_graph():
    """Build the complete Splunk SOC analyst graph."""
    workflow = StateGraph(SplunkSOCState)
    
    # Add nodes
    workflow.add_node("understand", understand_query_node)
    workflow.add_node("generate_spl", generate_spl_node)
    workflow.add_node("execute", execute_query_node)
    workflow.add_node("analyze", analyze_results_node)
    workflow.add_node("report", generate_report_node)
    
    # Set entry point
    workflow.set_entry_point("understand")
    
    # Add edges
    workflow.add_edge("understand", "generate_spl")
    workflow.add_edge("generate_spl", "execute")
    
    # Conditional routing after execute
    workflow.add_conditional_edges(
        "execute",
        route_after_execute,
        {
            "analyze": "analyze",
            "await_approval": END  # Pause for human approval
        }
    )
    
    workflow.add_edge("analyze", "report")
    workflow.add_edge("report", END)
    
    # Compile with checkpointing for approval workflow
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)

# ============================================================================
# Usage Examples
# ============================================================================

def investigate_with_splunk(query: str, thread_id: str = "investigation-1"):
    """
    Run a security investigation using natural language.
    
    Args:
        query: Natural language question about security data
        thread_id: Unique ID for this investigation thread
    
    Returns:
        Investigation report and findings
    """
    agent = build_splunk_soc_graph()
    config = {"configurable": {"thread_id": thread_id}}
    
    initial_state: SplunkSOCState = {
        'query': query,
        'investigation_id': f"INV-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
        'spl_queries': [],
        'query_results': [],
        'findings': [],
        'threat_indicators': [],
        'messages': [],
        'phase': 'understand',
        'iteration': 0,
        'max_iterations': 10,
        'report': None,
        'requires_approval': False,
        'pending_approval_id': None
    }
    
    # Run the investigation
    final_state = agent.invoke(initial_state, config)
    
    return final_state

# Example usage
if __name__ == "__main__":
    # Example 1: Investigate failed logins
    result = investigate_with_splunk(
        "Show me all failed login attempts in the last 24 hours, "
        "grouped by source IP and user, highlighting any accounts "
        "with more than 10 failures"
    )
    print(result['report'])
    
    # Example 2: Investigate potential data exfiltration
    result = investigate_with_splunk(
        "Find any unusually large outbound data transfers from "
        "internal hosts to external IPs in the last 7 days"
    )
    print(result['report'])
    
    # Example 3: Investigate specific threat
    result = investigate_with_splunk(
        "Search for any PowerShell executions with encoded commands "
        "that also made network connections to non-corporate IPs"
    )
    print(result['report'])
```

---

## Example 3: Handling MCP Approval Requests

When queries require approval, here's how to handle it:

```python
async def investigate_with_approval(query: str, thread_id: str):
    """
    Run investigation with human-in-the-loop for query approval.
    """
    agent = build_splunk_soc_graph()
    config = {"configurable": {"thread_id": thread_id}}
    
    initial_state = {
        'query': query,
        'investigation_id': f"INV-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
        # ... other state fields
    }
    
    # Stream until we hit an approval request or completion
    for event in agent.stream(initial_state, config):
        node_name = list(event.keys())[0]
        node_state = event[node_name]
        
        print(f"Completed: {node_name}")
        
        # Check if we're awaiting approval
        if node_state.get('requires_approval'):
            print("\n" + "="*50)
            print("⚠️  QUERY APPROVAL REQUIRED")
            print("="*50)
            
            # Show the pending query
            print(f"\nSPL Query to execute:")
            for q in node_state.get('spl_queries', []):
                print(f"  {q}")
            
            # Get human decision
            approval = input("\nApprove this query? (yes/no): ")
            
            if approval.lower() == 'yes':
                # Submit approval and continue
                approval_message = {
                    "role": "user",
                    "content": [{
                        "type": "mcp_approval_response",
                        "approve": True,
                        "approval_request_id": node_state['pending_approval_id']
                    }]
                }
                
                # Update state and continue
                # ... continue execution with approval
                
            else:
                print("Query rejected. Investigation halted.")
                return None
    
    # Get final state
    final_state = agent.get_state(config)
    return final_state.values
```

---

## Key Splunk MCP Tools Available

| Tool | Purpose | Use Case |
|------|---------|----------|
| `generate_spl` | Convert natural language → SPL | "Show failed logins" → `index=auth action=failure` |
| `optimize_spl` | Improve query performance | Add time bounds, field extractions |
| `explain_spl` | SPL → natural language | Validate query does what you expect |
| `run_splunk_query` | Execute SPL and get results | Retrieve actual security data |
| `get_indexes` | List available indexes | Discover data sources |
| `get_metadata` | Get hosts, sources, sourcetypes | Build targeted queries |
| `ask_splunk_question` | General Splunk Q&A | "What's the syntax for stats?" |

This integration allows your SOC agent to leverage Splunk's full power through natural language, making security investigations accessible even to analysts who aren't SPL experts.
