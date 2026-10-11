# This script demonstrates how to create a simple agent that uses tools to perform actions.
# The agent uses a ChatOpenAI model to generate responses and tools to perform actions.
# The agent can execute tools to perform actions based on the input query.
# The agent uses a ReAct (Reason and Action) template to generate responses based on the input query.

# Instructor: Omar Santos @santosomar

# Import the required libraries
from dotenv import load_dotenv
from langchain import hub
from langchain.agents import (
    AgentExecutor,
    create_react_agent,
)
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI

# Load environment variables from .env file
load_dotenv()


# Define a tool that checks if a given hash appears in known breached password databases
# using the Have I Been Pwned (HIBP) k-anonymity API.
def check_password_breach(password: str) -> str:
    """Checks if a password has appeared in known data breaches using the
    Have I Been Pwned k-anonymity API. Returns the number of times it has
    been seen, or confirms it has not been found in any known breach."""
    import hashlib
    import urllib.request

    sha1_hash = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()  # HIBP API requires SHA-1
    prefix, suffix = sha1_hash[:5], sha1_hash[5:]

    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    req = urllib.request.Request(url, headers={"User-Agent": "CyberAgent/1.0"})
    with urllib.request.urlopen(req) as response:
        body = response.read().decode("utf-8")

    for line in body.splitlines():
        hash_suffix, count = line.split(":")
        if hash_suffix == suffix:
            return (
                f"WARNING: This password has been seen {count} time(s) in data breaches. "
                "It should NOT be used."
            )

    return "This password was NOT found in any known data breaches."


# List of tools available to the agent
tools = [
    Tool(
        name="PasswordBreachCheck",
        func=check_password_breach,
        description=(
            "Checks whether a password has been exposed in known data breaches "
            "using the Have I Been Pwned API. Input should be the password string."
        ),
    ),
]

# Pull the prompt template from the hub
# ReAct = Reason and Action
# https://smith.langchain.com/hub/hwchase17/react
prompt = hub.pull("hwchase17/react")

# Initialize a ChatOpenAI model
llm = ChatOpenAI(
    model="gpt-5.4-mini", temperature=0
)

# Create the ReAct agent using the create_react_agent function
agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=prompt,
)

# Create an agent executor from the agent and tools
agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    verbose=True,
)

# Run the agent with a test query
response = agent_executor.invoke(
    {"input": "Is the password 'P@ssw0rd123' safe to use?"}
)

# Print the response from the agent
print("response:", response)
