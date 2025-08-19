# This script demonstrates a basic agentic RAG implementation using LangGraph.
# It builds a small vector store from cybersecurity data and uses an agent to
# decide when to search the documents. The example is adapted from the LangGraph
# agentic RAG tutorial but focuses on answering cybersecurity questions.
#
# Instructor: Omar Santos @santosomar

import os
from typing import TypedDict, List

from dotenv import load_dotenv
from langgraph.graph import END, StateGraph
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_chroma import Chroma
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


# Load environment variables from a .env file
load_dotenv()


# Define paths for the dataset and persistent vector store
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(
    os.path.dirname(CURRENT_DIR), "..", "part4_rag_examples", "data", "ssrf.txt"
)
PERSIST_PATH = os.path.join(CURRENT_DIR, "db", "chroma_db")


# Initialize or load the Chroma vector store
if not os.path.exists(PERSIST_PATH):
    os.makedirs(PERSIST_PATH, exist_ok=True)
    loader = TextLoader(DATA_PATH)
    documents = loader.load()
    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=10)
    docs = splitter.split_documents(documents)
    embeddings = OpenAIEmbeddings()
    vectordb = Chroma.from_documents(docs, embeddings, persist_directory=PERSIST_PATH)
else:
    vectordb = Chroma(persist_directory=PERSIST_PATH, embedding_function=OpenAIEmbeddings())

retriever = vectordb.as_retriever()

# Initialize the language model used by the agent
llm = ChatOpenAI(model="gpt-5-mini", temperature=0)


class AgentState(TypedDict):
    """State for the agent graph."""

    messages: List[BaseMessage]


def agent_node(state: AgentState) -> AgentState:
    """Use the LLM to decide the next step or provide an answer."""

    response = llm.invoke(state["messages"])
    return {"messages": state["messages"] + [response]}


def search_node(state: AgentState) -> AgentState:
    """Search the vector store for relevant documents."""

    query = state["messages"][-1].content
    docs = retriever.invoke(query)
    results = "\n\n".join(doc.page_content for doc in docs)
    return {"messages": state["messages"] + [AIMessage(content=results)]}


def decide_next(state: AgentState) -> str:
    """Decide whether to search again or finish."""

    last_msg = state["messages"][-1].content
    if "FINAL" in last_msg.upper():
        return END
    if "SEARCH" in last_msg.upper():
        return "search"
    return END


# Build the LangGraph state machine
workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)
workflow.add_node("search", search_node)
workflow.set_entry_point("agent")
workflow.add_edge("search", "agent")
workflow.add_conditional_edges("agent", decide_next, {"search": "search", END: END})
app = workflow.compile()

if __name__ == "__main__":
    user_question = "How can I prevent SSRF attacks?"
    events = app.stream({"messages": [HumanMessage(content=user_question)]})
    for event in events:
        if isinstance(event, dict) and "messages" in event:
            message = event["messages"][-1]
            if isinstance(message, AIMessage):
                print(message.content)
