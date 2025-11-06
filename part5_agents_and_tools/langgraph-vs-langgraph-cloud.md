# LangGraph Cloud

**LangGraph Cloud** is a managed service for deploying and running LangGraph agents in production. It's the official hosting platform from LangChain for your LangGraph applications.

## What is LangGraph Cloud?

LangGraph Cloud is a **deployment platform** that provides:

- 🚀 **Managed Infrastructure**: Deploy agents without managing servers
- 🔄 **Built-in Persistence**: Automatic state management and checkpointing
- 📡 **Streaming Support**: Real-time updates from your agents
- 🔌 **REST API**: Interact with your agents via HTTP endpoints
- 🔐 **Authentication & Security**: Built-in auth and access control
- 📊 **Monitoring & Observability**: Track agent performance and behavior
- ⚡ **Scalability**: Automatically scales based on demand
- 🔄 **Version Management**: Deploy multiple versions of your agents

## Key Features

### 1. **Stateful Agent Hosting**
Unlike stateless function deployments, LangGraph Cloud maintains agent state across invocations:

```python
# Your agent runs with persistent state across conversations
config = {"configurable": {"thread_id": "user-123"}}
response = await client.runs.create(
    assistant_id="my-agent",
    input={"messages": [{"role": "user", "content": "Hello"}]},
    config=config
)
```

### 2. **Multiple Invocation Modes**

**Streaming Mode** - Get real-time updates:
```python
async for chunk in client.runs.stream(
    assistant_id="my-agent",
    input={"messages": [{"role": "user", "content": "Analyze this..."}]}
):
    print(chunk)
```

**Batch Mode** - Process multiple inputs:
```python
results = await client.runs.batch(
    assistant_id="my-agent",
    inputs=[input1, input2, input3]
)
```

**Background Mode** - Long-running tasks:
```python
run = await client.runs.create(
    assistant_id="my-agent",
    input={"task": "complex_analysis"},
    mode="background"
)
```

### 3. **Human-in-the-Loop**

Automatically handles agent interruptions for human approval:

```python
# Agent pauses and waits for approval
run = await client.runs.wait(run_id)

if run.status == "interrupted":
    # Human reviews and approves
    await client.runs.resume(
        run_id=run_id,
        input={"approved": True}
    )
```

### 4. **Cron Jobs & Scheduling**

Schedule agents to run automatically:

```python
# Run daily reports
cron = await client.crons.create(
    assistant_id="report-agent",
    schedule="0 9 * * *",  # Every day at 9 AM
    input={"report_type": "daily"}
)
```

### 5. **Multi-Tenancy**

Built-in support for multiple users/organizations:

```python
# Each user gets isolated state
config = {
    "configurable": {
        "thread_id": f"user-{user_id}-conversation-1",
        "user_id": user_id
    }
}
```

## Architecture

```
Your LangGraph App
       ↓
   langgraph.json (config)
       ↓
   Deploy to Cloud
       ↓
   REST API Endpoints
       ↓
   Your Application/Frontend
```

## Project Structure

```
my-agent/
├── langgraph.json          # Deployment configuration
├── agent.py                # Your LangGraph agent code
├── requirements.txt        # Python dependencies
└── .env                    # Environment variables
```

### Example `langgraph.json`:

```json
{
  "dependencies": ["."],
  "graphs": {
    "my_agent": "./agent.py:graph"
  },
  "env": {
    "OPENAI_API_KEY": "env:OPENAI_API_KEY"
  }
}
```

## Deployment Workflow

### 1. **Install CLI**

```bash
pip install langgraph-cli
```

### 2. **Create LangGraph Project**

```bash
langgraph init my-agent
cd my-agent
```

### 3. **Test Locally**

```bash
langgraph dev
```

This starts a local development server that mimics LangGraph Cloud.

### 4. **Deploy to Cloud**

```bash
langgraph deploy
```

### 5. **Interact with Deployed Agent**

```python
from langgraph_sdk import get_client

client = get_client(url="https://your-deployment.langraph.app")

# Run your agent
response = await client.runs.create(
    assistant_id="my-agent",
    input={"messages": [{"role": "user", "content": "Hello!"}]},
    config={"configurable": {"thread_id": "thread-1"}}
)

print(response)
```

## API Client Examples

### Python SDK

```python
from langgraph_sdk import get_client

client = get_client(url="YOUR_DEPLOYMENT_URL", api_key="YOUR_API_KEY")

# Create a run
run = await client.runs.create(
    assistant_id="my-agent",
    input={"query": "What's the weather?"},
    config={"configurable": {"thread_id": "conversation-1"}}
)

# Get run status
status = await client.runs.get(run_id=run["run_id"])

# Stream results
async for event in client.runs.stream(
    assistant_id="my-agent",
    input={"query": "Tell me a story"}
):
    print(event)

# Get thread history
history = await client.threads.get_history(thread_id="conversation-1")
```

### REST API (cURL)

```bash
# Create a run
curl -X POST https://your-deployment.langraph.app/runs \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "assistant_id": "my-agent",
    "input": {"messages": [{"role": "user", "content": "Hello"}]},
    "config": {"configurable": {"thread_id": "thread-1"}}
  }'
```

### JavaScript/TypeScript SDK

```typescript
import { Client } from "@langchain/langgraph-sdk";

const client = new Client({
  apiUrl: "YOUR_DEPLOYMENT_URL",
  apiKey: "YOUR_API_KEY"
});

// Run agent
const run = await client.runs.create({
  assistantId: "my-agent",
  input: { query: "Hello!" },
  config: { configurable: { threadId: "thread-1" } }
});

// Stream results
for await (const event of client.runs.stream({
  assistantId: "my-agent",
  input: { query: "Tell me about AI" }
})) {
  console.log(event);
}
```

## Pricing Tiers

LangGraph Cloud typically offers:

- **Free Tier**: Limited runs for development/testing
- **Pro Tier**: Higher limits, SLA guarantees
- **Enterprise**: Custom limits, dedicated support, on-premise options

*(Check the official LangChain website for current pricing)*

## Use Cases

1. **Customer Support Bots**: Stateful conversations with memory
2. **Research Assistants**: Long-running analysis with multiple tool calls
3. **Workflow Automation**: Scheduled tasks and background processing
4. **Multi-Agent Systems**: Coordinated agents working together
5. **Interactive Applications**: Real-time streaming responses

## Advantages Over DIY Hosting

| Feature | LangGraph Cloud | DIY |
|---------|----------------|-----|
| State Management | ✅ Built-in | ⚠️ Build yourself |
| Streaming | ✅ Native support | ⚠️ Configure manually |
| Scaling | ✅ Automatic | ⚠️ Manage infrastructure |
| Human-in-the-Loop | ✅ Built-in | ⚠️ Custom implementation |
| Monitoring | ✅ Included | ⚠️ Set up separately |
| Deployment | ✅ CLI command | ⚠️ Complex setup |

## Alternatives to LangGraph Cloud

If you prefer self-hosting:

1. **Docker Container**: Package your agent and deploy anywhere
2. **FastAPI**: Wrap your agent in a REST API
3. **Modal/Replicate**: General-purpose serverless platforms
4. **Kubernetes**: For large-scale deployments

Example self-hosted wrapper:

```python
from fastapi import FastAPI
from langgraph.checkpoint.postgres import PostgresSaver

app = FastAPI()
checkpointer = PostgresSaver.from_conn_string("postgresql://...")
agent = graph.compile(checkpointer=checkpointer)

@app.post("/invoke")
async def invoke_agent(input: dict, thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    result = await agent.ainvoke(input, config)
    return result
```

## Getting Started

1. **Sign up**: Visit [LangSmith/LangGraph Cloud](https://smith.langchain.com/)
2. **Install CLI**: `pip install langgraph-cli`
3. **Create project**: `langgraph init my-first-agent`
4. **Test locally**: `langgraph dev`
5. **Deploy**: `langgraph deploy`

## Documentation & Resources

- **Official Docs**: [langchain.com/langgraph-cloud](https://langchain.com/langgraph-cloud)
- **GitHub**: LangGraph examples and templates
- **Discord**: LangChain community for support
- **LangSmith**: Observability platform (integrates with LangGraph Cloud)

## Summary

**LangGraph Cloud** is the production-ready platform for deploying LangGraph agents with:
- Managed infrastructure
- Built-in persistence and state management
- Streaming, batching, and background execution
- Human-in-the-loop workflows
- REST API access
- Enterprise-grade security and scaling

It eliminates the complexity of deploying stateful AI agents, letting you focus on building great agent experiences! 🚀
