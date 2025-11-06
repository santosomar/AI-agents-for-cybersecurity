# Introduction to Building AI Agents with [LangGraph](https://docs.langchain.com/oss/python/langgraph/overview)

Why [LangGraph](https://docs.langchain.com/oss/python/langgraph/overview) for Agents?

- ✅ **State Management**: Track conversation history, context, and intermediate results
- ✅ **Cycles/Loops**: Agents can iterate and refine their approach
- ✅ **Tool Integration**: Seamlessly call external tools and APIs
- ✅ **Human-in-the-Loop**: Pause for human approval or input
- ✅ **Persistence**: Save and resume agent state
- ✅ **Streaming**: Real-time updates on agent progress

## Core Concepts

### 1. State
The data structure that flows through your agent:

```python
from typing_extensions import TypedDict

class AgentState(TypedDict):
    messages: list[dict]  # Conversation history
    next_action: str      # What to do next
    final_answer: str     # The result
```

### 2. Nodes
Functions that process state:

```python
async def my_node(state: AgentState, config):
    # Do some processing
    return {"next_action": "continue"}
```

### 3. Edges
Connections between nodes (can be conditional):

```python
graph.add_edge("node_a", "node_b")  # Always go from A to B
graph.add_conditional_edges("node_a", router_function)  # Dynamic routing
```

## Example 1: Simple ReAct Agent

A basic agent that reasons and acts in a loop:

```python
from typing import Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END, START
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# Define agent state
class AgentState(TypedDict):
    messages: list
    iteration: int

# Agent node: Think and decide
async def agent_node(state: AgentState, config):
    messages = state["messages"]
    iteration = state.get("iteration", 0)
    
    # Agent reasons about what to do
    response = await llm.ainvoke(messages, config)
    
    return {
        "messages": messages + [response],
        "iteration": iteration + 1
    }

# Decision node: Should we continue or finish?
def should_continue(state: AgentState) -> Literal["continue", "end"]:
    last_message = state["messages"][-1]
    
    # Stop if we have a final answer or hit max iterations
    if "FINAL ANSWER:" in last_message.content or state["iteration"] >= 5:
        return "end"
    return "continue"

# Build the graph
graph = StateGraph(AgentState)
graph.add_node("agent", agent_node)

graph.add_edge(START, "agent")
graph.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "agent",  # Loop back to agent
        "end": END
    }
)

app = graph.compile()

# Run the agent
result = await app.ainvoke({
    "messages": [
        SystemMessage(content="You are a helpful assistant. Think step by step."),
        HumanMessage(content="What is 15 * 23?")
    ],
    "iteration": 0
})

print(result["messages"][-1].content)
```

## Example 2: Tool-Calling Agent

An agent that can use external tools:

```python
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage
from langchain_core.tools import tool

# Define tools
@tool
def search_web(query: str) -> str:
    """Search the web for information."""
    # Simulate a web search
    return f"Search results for '{query}': [Mock results about {query}]"

@tool
def calculator(expression: str) -> str:
    """Calculate a mathematical expression."""
    try:
        result = eval(expression)
        return f"The result is {result}"
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def get_weather(location: str) -> str:
    """Get weather information for a location."""
    return f"Weather in {location}: Sunny, 72°F"

tools = [search_web, calculator, get_weather]

# Bind tools to LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0)
llm_with_tools = llm.bind_tools(tools)

# Define state
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], "The messages in the conversation"]

# Agent node
async def call_model(state: AgentState, config):
    messages = state["messages"]
    response = await llm_with_tools.ainvoke(messages, config)
    return {"messages": [response]}

# Routing function
def should_continue(state: AgentState) -> str:
    last_message = state["messages"][-1]
    
    # If there are tool calls, continue to tools
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    # Otherwise, end
    return "end"

# Build the graph
graph = StateGraph(AgentState)

# Add nodes
graph.add_node("agent", call_model)
graph.add_node("tools", ToolNode(tools))

# Add edges
graph.add_edge(START, "agent")
graph.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        "end": END
    }
)
graph.add_edge("tools", "agent")  # After tools, go back to agent

app = graph.compile()

# Run the agent
from langchain_core.messages import HumanMessage

result = await app.ainvoke({
    "messages": [
        HumanMessage(content="What's the weather in Paris and what is 25 * 4?")
    ]
})

# Print conversation
for msg in result["messages"]:
    if hasattr(msg, "content"):
        print(f"{msg.__class__.__name__}: {msg.content}")
```

## Example 3: Agent with Memory

An agent that maintains conversation history:

```python
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

# Define state with message accumulation
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], "Conversation history"]

# Simple conversational agent
async def chat_node(state: AgentState, config):
    llm = ChatOpenAI(model="gpt-4o-mini")
    response = await llm.ainvoke(state["messages"], config)
    return {"messages": [response]}

# Build graph with memory
graph = StateGraph(AgentState)
graph.add_node("chat", chat_node)
graph.add_edge(START, "chat")
graph.add_edge("chat", END)

# Add checkpointer for memory
memory = MemorySaver()
app = graph.compile(checkpointer=memory)

# Multi-turn conversation with same thread
config = {"configurable": {"thread_id": "conversation-1"}}

# First message
result1 = await app.ainvoke({
    "messages": [HumanMessage(content="My name is Alice")]
}, config)
print(result1["messages"][-1].content)

# Second message - agent remembers previous context
result2 = await app.ainvoke({
    "messages": [HumanMessage(content="What's my name?")]
}, config)
print(result2["messages"][-1].content)  # Should mention Alice
```

## Example 4: Agent with Human-in-the-Loop

Pause agent execution for human approval:

```python
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

class AgentState(TypedDict):
    messages: list
    approved: bool

async def generate_draft(state: AgentState, config):
    llm = ChatOpenAI(model="gpt-4o-mini")
    response = await llm.ainvoke(state["messages"], config)
    return {"messages": [response]}

def check_approval(state: AgentState) -> str:
    if state.get("approved", False):
        return "send"
    return "wait_approval"

# Build graph
graph = StateGraph(AgentState)
graph.add_node("generate_draft", generate_draft)
graph.add_node("send", lambda state, config: {"messages": [HumanMessage(content="Sent!")]})

graph.add_edge(START, "generate_draft")
graph.add_conditional_edges(
    "generate_draft",
    check_approval,
    {
        "send": "send",
        "wait_approval": END  # Pause here
    }
)
graph.add_edge("send", END)

# Use interrupt_before for human approval
app = graph.compile(
    checkpointer=MemorySaver(),
    interrupt_before=["send"]  # Pause before sending
)

# Run agent
config = {"configurable": {"thread_id": "email-draft-1"}}
result = await app.ainvoke({
    "messages": [HumanMessage(content="Write an email to John about the meeting")]
}, config)

# Human reviews and approves
# Continue execution after approval
result = await app.ainvoke({"approved": True}, config)
```

## Key Agent Patterns

### 1. **ReAct (Reason + Act)**
Agent reasons about what to do, acts, observes results, repeats.

### 2. **Plan-and-Execute**
Agent creates a plan, executes steps, adjusts plan based on results.

### 3. **Reflection**
Agent generates output, critiques it, improves it iteratively.

### 4. **Multi-Agent**
Multiple specialized agents collaborate on a task.

## Visualizing Your Agent

```python
from IPython.display import Image

# Visualize the graph structure
Image(app.get_graph().draw_mermaid_png())
```

## Best Practices

1. **Start Simple**: Begin with a basic loop, add complexity gradually
2. **Define Clear State**: Make your state structure explicit with TypedDict
3. **Use Checkpointers**: Add persistence for production agents
4. **Add Logging**: Track what your agent is doing at each step
5. **Set Limits**: Prevent infinite loops with iteration counts
6. **Handle Errors**: Add error handling nodes
7. **Test Thoroughly**: Test edge cases and failure modes

## Installation

```bash
pip install -qU langgraph
pip install -qU langchain-openai
pip install -qU langchain-core
```

## Next Steps

- **Add more tools**: Integrate APIs, databases, file systems
- **Implement streaming**: Show real-time agent progress
- **Build multi-agent systems**: Coordinate multiple specialized agents
- **Add persistence**: Use SQLite or Postgres checkpointers
- **Deploy to production**: Use LangGraph Cloud for deployment

LangGraph makes it easy to build agents that are reliable, debuggable, and production-ready! 🚀
