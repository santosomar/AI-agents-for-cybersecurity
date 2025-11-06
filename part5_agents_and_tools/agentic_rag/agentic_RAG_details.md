# Agentic RAG

**Agentic RAG** is an advanced approach to Retrieval-Augmented Generation (RAG) where an AI agent dynamically decides when, what, and how to retrieve information, rather than simply retrieving documents for every query.

## RAG vs Agentic RAG

### Traditional RAG (Passive)
```
User Query → Retrieve Documents → Generate Answer
```
- **Always retrieves**, even when not needed
- **Single retrieval step** - no refinement
- **Fixed retrieval strategy** - same approach for all queries

### Agentic RAG (Active)
```
User Query → Agent Decides → [Retrieve? Which source? Refine? Use tools?] → Generate Answer
```
- **Selective retrieval** - only when necessary
- **Iterative refinement** - can retrieve multiple times
- **Multiple strategies** - different approaches for different queries
- **Tool use** - can combine retrieval with other actions

## Why Agentic RAG?

| Scenario | Traditional RAG | Agentic RAG |
|----------|----------------|-------------|
| "What is 2+2?" | Retrieves documents unnecessarily | Uses calculator directly |
| "What's the weather?" | Retrieves outdated docs | Calls weather API |
| Complex query | Single retrieval, might miss context | Iteratively refines search |
| Multi-source query | Limited to one knowledge base | Searches multiple sources |

## Basic RAG Implementation

First, let's see traditional RAG:

```python
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Setup
llm = ChatOpenAI(model="gpt-4o-mini")
embeddings = OpenAIEmbeddings()

# Create vector store
documents = [
    "LangChain is a framework for building LLM applications.",
    "LangGraph is used for building stateful agents.",
    "RAG stands for Retrieval-Augmented Generation.",
]

vectorstore = FAISS.from_texts(documents, embeddings)
retriever = vectorstore.as_retriever(k=2)

# Simple RAG chain
prompt = ChatPromptTemplate.from_template(
    """Answer based on the context:

Context: {context}

Question: {question}

Answer:"""
)

# Traditional RAG - ALWAYS retrieves
rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# This retrieves documents even for "What is 2+2?"
result = await rag_chain.ainvoke("What is LangChain?")
print(result)
```

## Agentic RAG Implementation

Now, let's build an intelligent agent that decides when to retrieve:

```python
from typing import Annotated, Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END, START, MessagesState
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
import operator

# Setup LLM and embeddings
llm = ChatOpenAI(model="gpt-4o", temperature=0)
embeddings = OpenAIEmbeddings()

# Create knowledge base
documents = [
    "LangChain is a framework for developing applications powered by LLMs.",
    "LangGraph is a library for building stateful, multi-actor applications.",
    "RAG (Retrieval-Augmented Generation) combines retrieval with generation.",
    "Vector databases store embeddings for semantic search.",
    "Agentic systems can make decisions about when and how to act.",
]

vectorstore = FAISS.from_texts(documents, embeddings)

# Define retrieval tool
@tool
def search_knowledge_base(query: str) -> str:
    """Search the knowledge base for information about LangChain, LangGraph, and RAG.
    
    Use this tool when you need information about:
    - LangChain framework
    - LangGraph library
    - RAG (Retrieval-Augmented Generation)
    - Vector databases
    - AI agents
    
    Args:
        query: The search query
    """
    docs = vectorstore.similarity_search(query, k=2)
    return "\n\n".join([doc.page_content for doc in docs])

@tool
def calculator(expression: str) -> str:
    """Calculate mathematical expressions.
    
    Args:
        expression: A mathematical expression to evaluate (e.g., "2+2", "10*5")
    """
    try:
        result = eval(expression)
        return f"The result is {result}"
    except Exception as e:
        return f"Error calculating: {str(e)}"

# Define tools list
tools = [search_knowledge_base, calculator]

# Bind tools to LLM
llm_with_tools = llm.bind_tools(tools)

# Define agent state
class AgentState(TypedDict):
    messages: Annotated[list, operator.add]

# Define nodes
async def agent_node(state: AgentState, config):
    """Agent decides what to do"""
    response = await llm_with_tools.ainvoke(state["messages"], config)
    return {"messages": [response]}

def should_continue(state: AgentState) -> Literal["tools", "end"]:
    """Route based on whether tools are needed"""
    last_message = state["messages"][-1]
    
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return "end"

# Build the graph
graph = StateGraph(AgentState)

graph.add_node("agent", agent_node)
graph.add_node("tools", ToolNode(tools))

graph.add_edge(START, "agent")
graph.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        "end": END
    }
)
graph.add_edge("tools", "agent")

app = graph.compile()

# Test Agentic RAG
print("=== Test 1: Math question (uses calculator, not retrieval) ===")
result1 = await app.ainvoke({
    "messages": [HumanMessage(content="What is 15 * 23?")]
})
print(result1["messages"][-1].content)

print("\n=== Test 2: Knowledge question (uses retrieval) ===")
result2 = await app.ainvoke({
    "messages": [HumanMessage(content="What is LangChain?")]
})
print(result2["messages"][-1].content)

print("\n=== Test 3: Mixed query (uses both tools intelligently) ===")
result3 = await app.ainvoke({
    "messages": [HumanMessage(content="What is RAG and how many letters are in the word 'RAG'? (calculate 3*1)")]
})
print(result3["messages"][-1].content)
```

## Advanced Agentic RAG: Multiple Knowledge Bases

An agent that can choose between different knowledge sources:

```python
from langchain_core.tools import tool
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()

# Create multiple specialized knowledge bases
technical_docs = FAISS.from_texts([
    "Python is a high-level programming language.",
    "LangChain uses LCEL (LangChain Expression Language).",
    "Vector embeddings are numerical representations of text.",
], embeddings)

business_docs = FAISS.from_texts([
    "AI agents can reduce customer support costs by 40%.",
    "RAG systems improve accuracy and reduce hallucinations.",
    "LangChain is used by Fortune 500 companies.",
], embeddings)

policy_docs = FAISS.from_texts([
    "All customer data must be encrypted at rest.",
    "AI systems must comply with GDPR regulations.",
    "Access to production systems requires MFA.",
], embeddings)

# Create specialized retrieval tools
@tool
def search_technical_docs(query: str) -> str:
    """Search technical documentation about programming, frameworks, and architecture.
    
    Use for questions about: code, APIs, libraries, technical implementation.
    
    Args:
        query: Technical search query
    """
    docs = technical_docs.similarity_search(query, k=2)
    return "\n".join([doc.page_content for doc in docs])

@tool
def search_business_docs(query: str) -> str:
    """Search business documentation about ROI, case studies, and business value.
    
    Use for questions about: costs, benefits, business cases, customers.
    
    Args:
        query: Business search query
    """
    docs = business_docs.similarity_search(query, k=2)
    return "\n".join([doc.page_content for doc in docs])

@tool
def search_policy_docs(query: str) -> str:
    """Search company policies and compliance documentation.
    
    Use for questions about: regulations, compliance, security policies, data governance.
    
    Args:
        query: Policy search query
    """
    docs = policy_docs.similarity_search(query, k=2)
    return "\n".join([doc.page_content for doc in docs])

# Create agent with multiple specialized retrievers
tools = [search_technical_docs, search_business_docs, search_policy_docs]

llm = ChatOpenAI(model="gpt-4o", temperature=0)
llm_with_tools = llm.bind_tools(tools)

# The agent will intelligently choose which knowledge base to query
from langgraph.prebuilt import create_react_agent

multi_source_agent = create_react_agent(llm, tools)

# Test different query types
result = await multi_source_agent.ainvoke({
    "messages": [("user", "What are the GDPR requirements for our AI system?")]
})
# Agent chooses search_policy_docs

result = await multi_source_agent.ainvoke({
    "messages": [("user", "What is LCEL in LangChain?")]
})
# Agent chooses search_technical_docs
```

## Agentic RAG with Query Refinement

An agent that can refine its search queries iteratively:

```python
from langgraph.graph import StateGraph, END, START
from typing_extensions import TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

class QueryRefinementState(TypedDict):
    original_query: str
    refined_queries: list[str]
    search_results: list[str]
    iteration: int
    final_answer: str

llm = ChatOpenAI(model="gpt-4o")

async def generate_queries(state: QueryRefinementState, config):
    """Generate multiple refined queries"""
    prompt = f"""Given this question: "{state['original_query']}"
    
    Generate 3 different search queries that would help answer it.
    Be specific and cover different aspects.
    
    Return as a numbered list."""
    
    response = await llm.ainvoke([HumanMessage(content=prompt)], config)
    
    # Parse queries (simplified)
    queries = [q.strip() for q in response.content.split('\n') if q.strip()]
    
    return {"refined_queries": queries}

async def search_with_queries(state: QueryRefinementState, config):
    """Search using refined queries"""
    results = []
    
    for query in state["refined_queries"][:3]:  # Limit to 3
        # Simulate search
        docs = vectorstore.similarity_search(query, k=1)
        if docs:
            results.append(docs[0].page_content)
    
    return {"search_results": results}

async def synthesize_answer(state: QueryRefinementState, config):
    """Create final answer from all results"""
    context = "\n\n".join(state["search_results"])
    
    prompt = f"""Based on this information:

{context}

Answer this question: {state['original_query']}

Provide a comprehensive answer."""
    
    response = await llm.ainvoke([HumanMessage(content=prompt)], config)
    
    return {"final_answer": response.content}

# Build graph
graph = StateGraph(QueryRefinementState)
graph.add_node("generate_queries", generate_queries)
graph.add_node("search", search_with_queries)
graph.add_node("synthesize", synthesize_answer)

graph.add_edge(START, "generate_queries")
graph.add_edge("generate_queries", "search")
graph.add_edge("search", "synthesize")
graph.add_edge("synthesize", END)

query_refinement_agent = graph.compile()

# Use the agent
result = await query_refinement_agent.ainvoke({
    "original_query": "How do I build production-ready AI agents?",
    "refined_queries": [],
    "search_results": [],
    "iteration": 0,
    "final_answer": ""
})

print(result["final_answer"])
```

## Agentic RAG with Self-Reflection

An agent that evaluates its retrieved results and re-searches if needed:

```python
from typing import Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END, START

class ReflectiveRAGState(TypedDict):
    question: str
    documents: list[str]
    answer: str
    quality_score: int
    iterations: int

async def retrieve_documents(state: ReflectiveRAGState, config):
    """Retrieve relevant documents"""
    docs = vectorstore.similarity_search(state["question"], k=3)
    return {
        "documents": [doc.page_content for doc in docs],
        "iterations": state.get("iterations", 0) + 1
    }

async def generate_answer(state: ReflectiveRAGState, config):
    """Generate answer from documents"""
    context = "\n\n".join(state["documents"])
    
    prompt = f"""Context: {context}
    
Question: {state['question']}

Answer:"""
    
    response = await llm.ainvoke([HumanMessage(content=prompt)], config)
    return {"answer": response.content}

async def evaluate_quality(state: ReflectiveRAGState, config):
    """Evaluate if the answer is good enough"""
    prompt = f"""Question: {state['question']}
Retrieved Documents: {state['documents']}
Generated Answer: {state['answer']}

On a scale of 1-10, rate how well the documents support answering the question.
Consider:
- Relevance of documents
- Completeness of information
- Confidence in answer

Return only a number 1-10."""
    
    response = await llm.ainvoke([HumanMessage(content=prompt)], config)
    
    try:
        score = int(response.content.strip())
    except:
        score = 5
    
    return {"quality_score": score}

def should_refine(state: ReflectiveRAGState) -> Literal["retrieve", "end"]:
    """Decide if we need to retrieve again"""
    # If quality is low and we haven't iterated too many times
    if state["quality_score"] < 7 and state["iterations"] < 3:
        return "retrieve"
    return "end"

# Build reflective RAG graph
graph = StateGraph(ReflectiveRAGState)

graph.add_node("retrieve", retrieve_documents)
graph.add_node("generate", generate_answer)
graph.add_node("evaluate", evaluate_quality)

graph.add_edge(START, "retrieve")
graph.add_edge("retrieve", "generate")
graph.add_edge("generate", "evaluate")
graph.add_conditional_edges(
    "evaluate",
    should_refine,
    {
        "retrieve": "retrieve",  # Try again with refined query
        "end": END
    }
)

reflective_agent = graph.compile()

# Test
result = await reflective_agent.ainvoke({
    "question": "How does LangGraph handle state?",
    "documents": [],
    "answer": "",
    "quality_score": 0,
    "iterations": 0
})

print(f"Final answer after {result['iterations']} iterations:")
print(result["answer"])
print(f"Quality score: {result['quality_score']}")
```

## Key Patterns in Agentic RAG

### 1. **Routing** - Choose the right knowledge source
```python
if query_about_technical:
    use_technical_db()
elif query_about_business:
    use_business_db()
```

### 2. **Query Decomposition** - Break complex queries into sub-queries
```python
"How does X work and what are alternatives?"
→ Query 1: "How does X work?"
→ Query 2: "What are alternatives to X?"
```

### 3. **Self-Correction** - Re-retrieve if results are poor
```python
if quality_score < threshold:
    refine_query()
    retrieve_again()
```

### 4. **Multi-Step Reasoning** - Chain multiple retrievals
```python
retrieve(initial_query)
→ analyze_results()
→ retrieve(refined_query)
→ synthesize()
```

## Benefits of Agentic RAG

| Benefit | Description |
|---------|-------------|
| **Efficiency** | Only retrieves when necessary |
| **Accuracy** | Can refine and re-search |
| **Flexibility** | Adapts strategy to query type |
| **Multi-source** | Searches appropriate knowledge bases |
| **Cost-effective** | Fewer unnecessary API calls |
| **Better UX** | More intelligent, context-aware responses |

## When to Use Agentic RAG

✅ **Use Agentic RAG when:**
- Queries vary widely in complexity
- Multiple knowledge sources exist
- Some queries need tools beyond retrieval
- Query refinement could improve results
- Cost efficiency matters

❌ **Traditional RAG is fine when:**
- All queries need document retrieval
- Single knowledge base
- Simple retrieve-and-answer pattern
- Low complexity queries

## Complete Production Example

```python
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

# Production-ready Agentic RAG
llm = ChatOpenAI(model="gpt-4o", temperature=0)

@tool
def search_documentation(query: str, doc_type: str = "general") -> str:
    """Search product documentation.
    
    Args:
        query: Search query
        doc_type: Type of docs ("general", "api", "tutorials")
    """
    # Your vector store logic here
    return f"Results for {query} in {doc_type} docs"

@tool  
def search_customer_data(customer_id: str) -> str:
    """Look up customer information."""
    # Your database logic here
    return f"Customer {customer_id} info"

@tool
def calculate_metric(metric_name: str, params: dict) -> str:
    """Calculate business metrics."""
    # Your calculation logic
    return f"Calculated {metric_name}"

# Create production agent
tools = [search_documentation, search_customer_data, calculate_metric]
agent = create_react_agent(llm, tools)

# The agent intelligently decides which tools to use and when
result = await agent.ainvoke({
    "messages": [("user", "What's our churn rate for customer CUST-123 and what does our documentation say about retention strategies?")]
})
```

## Installation

```bash
pip install -qU langgraph
pip install -qU langchain-openai
pip install -qU langchain-community
pip install -qU faiss-cpu  # or faiss-gpu
pip install -qU tiktoken
```

## Summary

**Agentic RAG** transforms passive document retrieval into an intelligent, decision-making system that:
- 🎯 **Decides when to retrieve** (not always)
- 🔄 **Iteratively refines** searches
- 🗂️ **Chooses appropriate sources** (multi-source)
- 🔧 **Combines with other tools** (calculator, APIs, etc.)
- 🤔 **Self-reflects** on result quality
- 📈 **Adapts strategies** based on query type

This makes RAG systems more accurate, efficient, and capable of handling complex real-world scenarios! 🚀
