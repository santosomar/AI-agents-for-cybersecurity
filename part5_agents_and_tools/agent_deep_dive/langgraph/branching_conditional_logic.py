# Branching Conditional Logic
# Branching conditional logic allows you to include conditional logic in a prompt template.
# The explanation is available at: https://cybercopilot.org/QOrM2Qm
# Instructor: Omar Santos @santosomar

# LangChain Chat Prompt Template Documents: https://python.langchain.com/docs/how_to/#prompt-templates 
# OpenAI Chat Model Documents: https://python.langchain.com/docs/how_to/#chat-models
# LangChain Expression Language (LCEL): https://python.langchain.com/docs/how_to/#langchain-expression-language-lcel
# LangGraph Documents: https://langchain-ai.github.io/langgraph/
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langchain.tools import Tool
from dotenv import load_dotenv
from typing import TypedDict, List

# Load environment variables from .env
load_dotenv()

# Define the state as a TypedDict for clarity and type checking
class IncidentState(TypedDict):
    messages: List[str]
    indicators_of_compromise: List[str]

# Create a ChatOpenAI model
model = ChatOpenAI(model="gpt-5.4-mini")

def initial_analysis(state: dict):
    """
    Perform initial analysis of the alert.
    
    Args:
        state (dict): The current state of the incident.
    
    Returns:
        dict: The updated state of the incident.
    """
    return {"messages": ["Initial analysis complete. Alert appears to be a phishing attempt."]}

def phishing_analysis(state: dict):
    """
    Perform detailed phishing analysis.
    Extract malicious URL from phishing email
    
    Args:
        state (dict): The current state of the incident.
    
    Returns:
        dict: The updated state of the incident.
    """
    return {"messages": ["Phishing email analyzed. Extracted malicious URL."], "indicators_of_compromise": ["https://malicious.h4cker.org"]}
    
    # Note: https://malicious.h4cker.org is not a real malicious URL, 
    # it is just an example I have created for my books and video courses.

def malware_analysis(state: dict):
    """
    Perform detailed malware analysis.
    
    Args:
        state (dict): The current state of the incident.
    
    Returns:
        dict: The updated state of the incident.
    """
    
    # Detonate malware in a sandbox
    
    return {"messages": ["Malware detonated. Identified C2 server."], "indicators_of_compromise": ["123.123.123.123"]}

def decide_next_step(state: dict):
    """
    Decide the next step based on the last message.
    
    Args:
        state (dict): The current state of the incident.
    
    Returns:
        str: The next step to take.
    """
    last_message = state["messages"][-1].lower()
    if "phishing" in last_message:
        return "phishing_analysis"
    elif "malware" in last_message:
        return "malware_analysis"
    else:
        return END

# Define the graph 
workflow = StateGraph(IncidentState)
workflow.add_node("initial_analysis", initial_analysis)
workflow.add_node("phishing_analysis", phishing_analysis)
workflow.add_node("malware_analysis", malware_analysis)
workflow.set_entry_point("initial_analysis")
workflow.add_conditional_edges(
    "initial_analysis",
    decide_next_step,
    {
        "phishing_analysis": "phishing_analysis",
        "malware_analysis": "malware_analysis",
        END: END
    }
)
# Add edges to the graph 
workflow.add_edge("phishing_analysis", END)
workflow.add_edge("malware_analysis", END)
app = workflow.compile()

# Run the workflow
result = app.invoke({"messages": [], "indicators_of_compromise": []})
print("Workflow result:", result)
