# LangGraph Basic Example: A Simple Malicious URL Analysis Agent
# This script demonstrates the core concepts of LangGraph by building an agent
# that analyzes a URL and decides if it's malicious or benign.
#
# Instructor: Omar Santos @santosomar

# LangGraph Documents: https://langchain-ai.github.io/langgraph/

# Import the required libraries
import json
from typing import TypedDict, Literal

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic.v1 import BaseModel, Field

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# Load environment variables from .env file
load_dotenv()

# --- 0. Initialize the AI Model ---
# We'll use this LLM to make decisions in our graph.
model = ChatOpenAI(temperature=0.2, model="gpt-5-mini")


# --- Pydantic model for structured output ---
class AIVerdict(BaseModel):
    """The AI's verdict and explanation."""
    verdict: Literal["malicious", "benign"] = Field(description="The final verdict, either 'malicious' or 'benign'.")
    explanation: str = Field(description="A brief explanation for the verdict.")


# --- 1. Define the State ---
# The state is the "memory" of our graph. It's a dictionary that gets passed
# between nodes. Each node can read from it and write to it.

class AgentState(TypedDict):
    """
    Represents the state of our agent.

    Attributes:
        url: The URL to be analyzed.
        analysis_results: A dictionary holding results from our analysis tool.
        verdict: A dictionary containing the AI's verdict and explanation.
    """
    url: str
    analysis_results: dict
    verdict: dict


# --- 2. Define Tools and Nodes ---
# Nodes are the fundamental building blocks of the graph. They are Python functions
# that perform actions. Each node receives the current state and returns an
# updated version of the state.

def analyze_url_tool(url: str) -> dict:
    """
    A mock tool that "analyzes" a URL.
    In a real-world scenario, this would make an API call to a service like
    VirusTotal.
    """
    print(f"--- TOOL: Analyzing URL: {url} ---")
    if "malicious.h4cker.org" in url:
        return {"threat_level": "malicious", "details": "Confirmed phishing domain based on internal threat intel."}
    elif "hackertraining.org" in url:
        return {"threat_level": "benign", "details": "Domain is a known partner and is on the allowlist."}
    else:
        return {"threat_level": "unknown", "details": "Domain not found in threat feeds."}

def enrich_url_node(state: AgentState) -> AgentState:
    """
    This node calls our analysis tool to enrich the URL.
    It updates the state with the tool's findings.
    """
    print("--- NODE: Enriching URL ---")
    url_to_check = state["url"]
    results = analyze_url_tool(url_to_check)
    return {"analysis_results": results}

def report_malicious_node(state: AgentState):
    """A terminal node that simply ends the malicious path."""
    print("--- NODE: Malicious Path Complete ---")
    # The verdict is already set by the AI, so we just end.
    return {}

def report_benign_node(state: AgentState):
    """A terminal node that simply ends the benign path."""
    print("--- NODE: Benign Path Complete ---")
    # The verdict is already set by the AI, so we just end.
    return {}


# --- 3. Define Conditional Edges ---
# Conditional edges are the "brains" of the graph. They are functions that
# inspect the current state and decide which node to go to next.

def ai_triage_node(state: AgentState) -> AgentState:
    """
    Uses the AI model to decide if the URL is malicious or benign and provide an explanation.
    """
    print("--- NODE: AI Triage --- ")

    # Use a JSON parser that is aware of our desired output structure
    parser = JsonOutputParser(pydantic_object=AIVerdict)

    prompt = ChatPromptTemplate.from_messages(
        [("system",
          """You are a cybersecurity analyst. Based on the provided analysis, 
          classify the URL's threat level and provide an explanation for your decision.
          Return your response in a JSON object with 'verdict' and 'explanation' keys.
          
          {format_instructions}"""),
         ("human", "Analysis results:\n\n{analysis}")]
    ).partial(format_instructions=parser.get_format_instructions())

    # The AI model will make the decision and format it as JSON
    chain = prompt | model | parser

    # Get the analysis from the state
    analysis = json.dumps(state['analysis_results'])

    # Get the structured response from the AI
    ai_response = chain.invoke({"analysis": analysis})

    # Print the explanation for clarity
    print(f"--- AI Verdict: {ai_response['verdict']} ---")
    print(f"--- AI Explanation: {ai_response['explanation']} ---")

    # Return the entire structured response
    return {"verdict": ai_response}


def triage_decision(state: AgentState) -> Literal["malicious", "benign"]:
    """
    Inspects the AI's verdict and decides the next step.
    """
    print("--- CONDITIONAL EDGE: Routing based on AI Verdict ---")
    # The 'verdict' in the state is now a dictionary, so we extract the final decision
    return state["verdict"]["verdict"]

# --- 4. Assemble the Graph ---
# Now we wire all our nodes and edges together to create the final flowchart.

# Instantiate the graph and pass it our state object definition
workflow = StateGraph(AgentState)

# Add the nodes to the graph
workflow.add_node("enrich_url", enrich_url_node)
workflow.add_node("ai_triage", ai_triage_node) # New AI decision node
workflow.add_node("report_malicious", report_malicious_node)
workflow.add_node("report_benign", report_benign_node)

# Set the entry point of the graph
workflow.set_entry_point("enrich_url")

# Add the connections (edges) between the nodes
# First, add the conditional edge. After the 'enrich_url' node, call the
# 'triage_decision' function. Based on its return value, route to the
# specified node.
# The conditional edge now comes AFTER the AI triage node
workflow.add_edge("enrich_url", "ai_triage")

workflow.add_conditional_edges(
    "ai_triage",
    triage_decision,
    {
        "malicious": "report_malicious",
        "benign": "report_benign",
    },
)

# Add the final edges from our reporting nodes to the special END state.
# This tells the graph that the process is complete.
workflow.add_edge("report_malicious", END)
workflow.add_edge("report_benign", END)


# Compile the graph into a runnable application
app = workflow.compile()


# --- 5. Run the Graph ---
# Let's test our agent with a few different URLs.

# Run 1: Testing a malicious URL (FYI: this is not a real malicious URL, 
# it's a site that I created for my books and video courses)
print("--- RUN 1: Testing a malicious URL ---")
# This domain is recognized by our mock tool as malicious
initial_state_malicious = {"url": "https://malicious.h4cker.org/"} 
final_state_malicious = app.invoke(initial_state_malicious)
print("\nFinal State for Malicious URL:")
print(json.dumps(final_state_malicious, indent=2))
print("------------------------------\n")

# Run 2: Testing a benign URL
print("--- RUN 2: Testing a benign URL ---")
# This domain is recognized by our mock tool as benign
initial_state_benign = {"url": "https://hackertraining.org"} 
final_state_benign = app.invoke(initial_state_benign)
print("\nFinal State for Benign URL:")
print(json.dumps(final_state_benign, indent=2))
print("------------------------------\n")

# Run 3: Testing an unknown URL
print("--- RUN 3: Testing an unknown URL ---")
# This domain is not in our mock tool's database
initial_state_unknown = {"url": "https://www.some-other-site.com"} 
final_state_unknown = app.invoke(initial_state_unknown)
print("\nFinal State for Unknown URL:")
print(json.dumps(final_state_unknown, indent=2))
print("------------------------------")
