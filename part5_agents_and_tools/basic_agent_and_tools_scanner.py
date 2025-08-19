# This script demonstrates how to create a simple agent that uses tools to perform actions.
# The agent uses a ChatOpenAI model to generate responses and tools to perform actions.
# The agent can execute tools to perform actions based on the input query.
# The agent uses a ReAct (Reason and Action) template to generate responses based on the input query.

# Instructor: Omar Santos @santosomar

# Import the required libraries

# For nmap you can install it using pip install python-nmap
import nmap

from dotenv import load_dotenv
from langchain import hub
from langchain.agents import (
    AgentExecutor,
    create_react_agent,
)
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

# Load environment variables from .env file
load_dotenv()


# Define a very simple tool function that returns the current time
def get_current_time(*args, **kwargs):
    """Returns the current time in H:MM AM/PM format."""
    import datetime  # Import datetime module to get current time

    now = datetime.datetime.now()  # Get current time
    return now.strftime("%I:%M %p")  # Format time in H:MM AM/PM format

def scanner(ip_address):
    """Scans the specified IP address or range using nmap."""
    nm = nmap.PortScanner()
    nm.scan(ip_address)
    return nm.all_hosts()



# Define a Pydantic model for the scanner input
class ScannerInput(BaseModel):
    ip_address: str = Field(..., description="The IP address or range to scan")

# List of tools available to the agent
tools = [
    Tool(
        name="Time",
        func=get_current_time,
        description="Useful for when you need to know the current time",
    ),
    StructuredTool(
        name="Scanner",
        func=scanner,
        description="Useful for scanning IP addresses or ranges",
        args_schema=ScannerInput,
    ),
]

# Pull the prompt template from the hub
# ReAct = Reason and Action
# https://smith.langchain.com/hub/hwchase17/react
prompt = hub.pull("hwchase17/react")

# Initialize a ChatOpenAI model
llm = ChatOpenAI(
    model="gpt-5-mini", temperature=0
)

# Create the ReAct agent using the create_react_agent function
agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=prompt,
    stop_sequence=True,
)

# Create an agent executor from the agent and tools
agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    verbose=True,
)

# Run the agent with a test query including an IP address
# In this case, the agent will scan the IP address 8.8.8.8 and return the results
response = agent_executor.invoke({"input": "Scan the IP address 192.168.25.48"})

# Print the response from the agent
print("response:", response)