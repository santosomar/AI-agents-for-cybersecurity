# LangGraph Example: CISA KEV Analysis Agent
#
# This script builds a LangGraph agent that retrieves the last 3 vulnerabilities
# from CISA's Known Exploited Vulnerability (KEV) catalog and then uses an AI
# to summarize the potential impact of each one.
#
# Instructor: Omar Santos @santosomar

import requests
import json
from typing import TypedDict, List

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from pydantic.v1 import BaseModel, Field
from langgraph.graph import StateGraph, END

# Load environment variables from .env file
load_dotenv()

# --- 0. Initialize the AI Model ---
# We'll use this LLM to summarize the vulnerabilities.
model = ChatOpenAI(temperature=0.2, model="gpt-5-mini")

# CISA KEV Catalog URL
CISA_KEV_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"

# --- 1. Define the State ---
# This holds the data that flows through our graph.

class ExploitationInsights(BaseModel):
    """A model to hold the AI's analysis of a vulnerability's exploitation.
    """
    cwe_id: str = Field(description="The most likely CWE ID for the vulnerability (e.g., 'CWE-78').")
    cwe_explanation: str = Field(description="A brief explanation of the CWE.")
    attack_vector_summary: str = Field(description="A summary of how an attacker might exploit this vulnerability.")


class AgentState(TypedDict):
    """
    Represents the state of our CISA KEV analysis agent.

    Attributes:
        vulnerabilities: A list of the latest vulnerabilities from the KEV catalog.
        summaries: A list of AI-generated impact summaries.
        exploitation_insights: A list of AI-generated exploitation analyses.
    """
    vulnerabilities: List[dict]
    summaries: List[dict]
    exploitation_insights: List[dict]


# --- 2. Define Tools and Nodes ---

def get_kev_vulnerabilities_node(state: AgentState) -> AgentState:
    """
    Fetches the latest known exploited vulnerabilities from the CISA catalog.
    """
    print("--- NODE: Fetching KEV Vulnerabilities ---")
    try:
        response = requests.get(CISA_KEV_URL)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        
        # Get the last 3 vulnerabilities (they are sorted by dateAdded descending)
        latest_vulnerabilities = data.get("vulnerabilities", [])[:3]
        print(f"--- Found {len(latest_vulnerabilities)} vulnerabilities ---")
        return {"vulnerabilities": latest_vulnerabilities}
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return {"vulnerabilities": []}

def summarize_vulnerabilities_node(state: AgentState) -> AgentState:
    """
    Uses an AI model to summarize the potential impact of each vulnerability.
    """
    print("--- NODE: Summarizing Vulnerabilities ---")
    vulnerabilities = state.get("vulnerabilities", [])
    summaries = []

    prompt = ChatPromptTemplate.from_template(
        """You are a senior cybersecurity analyst. 
        Based on the following vulnerability details, provide a concise, one-sentence summary of its potential impact on an organization.

        Vulnerability Details:
        - Name: {vulnerabilityName}
        - Description: {shortDescription}
        - Required Action: {requiredAction}

        Potential Impact Summary:"""
    )

    # Create the summarization chain
    summarize_chain = prompt | model | StrOutputParser()


    for vuln in vulnerabilities:
        print(f"--- Summarizing: {vuln['vulnerabilityName']} ({vuln['cveID']}) ---")
        summary = summarize_chain.invoke(vuln)
        summaries.append({"cveID": vuln['cveID'], "summary": summary})
    
    return {"summaries": summaries}


def analyze_exploitation_node(state: AgentState) -> AgentState:
    """
    Uses an AI model to analyze exploitation vectors and associated CWEs.
    """
    print("--- NODE: Analyzing Exploitation Vectors and CWEs ---")
    vulnerabilities = state.get("vulnerabilities", [])
    insights = []

    parser = JsonOutputParser(pydantic_object=ExploitationInsights)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert vulnerability researcher. For the given vulnerability, provide:
        1. The most likely CWE ID.
        2. A brief explanation of that CWE.
        3. A summary of how an attacker could exploit the vulnerability.

        {format_instructions}"""),
        ("human", "Vulnerability Details:\n\n- Name: {vulnerabilityName}\n- Description: {shortDescription}\n- Required Action: {requiredAction}")
    ]).partial(format_instructions=parser.get_format_instructions())

    analysis_chain = prompt | model | parser

    for vuln in vulnerabilities:
        print(f"--- Analyzing: {vuln['vulnerabilityName']} ({vuln['cveID']}) ---")
        insight = analysis_chain.invoke(vuln)
        insights.append({"cveID": vuln['cveID'], "insight": insight})

    return {"exploitation_insights": insights}


def report_results_node(state: AgentState):
    """
    A terminal node that prints the final, combined report.
    """
    print("\n--- FINAL REPORT: CISA KEV Vulnerability Analysis ---")
    summaries = state.get("summaries", [])
    insights = state.get("exploitation_insights", [])

    # Create a dictionary for quick lookup of insights by CVE ID
    insights_map = {item['cveID']: item['insight'] for item in insights}

    if not summaries:
        print("No analysis was generated.")
        return

    for summary_item in summaries:
        cve_id = summary_item['cveID']
        insight = insights_map.get(cve_id)

        print(f"\n------------------ {cve_id} ------------------")
        print(f"Impact Summary: {summary_item['summary']}")
        if insight:
            print(f"Potential CWE: {insight['cwe_id']} - {insight['cwe_explanation']}")
            print(f"Attack Vector: {insight['attack_vector_summary']}")
        else:
            print("No exploitation analysis available.")
    
    print("\n-----------------------------------------------------")


# --- 3. Assemble the Graph ---

# Instantiate the graph and pass it our state object definition
workflow = StateGraph(AgentState)

# Add the nodes to the graph
workflow.add_node("fetch_vulnerabilities", get_kev_vulnerabilities_node)
workflow.add_node("summarize_vulnerabilities", summarize_vulnerabilities_node)
workflow.add_node("analyze_exploitation", analyze_exploitation_node) # New node
workflow.add_node("report_results", report_results_node)

# Define the edges for the new, extended workflow
workflow.set_entry_point("fetch_vulnerabilities")
workflow.add_edge("fetch_vulnerabilities", "summarize_vulnerabilities")
workflow.add_edge("summarize_vulnerabilities", "analyze_exploitation")
workflow.add_edge("analyze_exploitation", "report_results")
workflow.add_edge("report_results", END)

# Compile the graph into a runnable application
app = workflow.compile()


# --- 4. Run the Graph ---
if __name__ == "__main__":
    # Run the agent with an empty initial state
    app.invoke({})
