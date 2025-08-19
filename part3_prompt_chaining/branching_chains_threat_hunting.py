# Threat Hunting Branching Chain Example
# This script demonstrates how to use branching chains in LangChain to create
# a threat hunting workflow that adapts based on the type of indicator.
# The chain will classify an indicator, then branch to specialized analysis
# paths for different indicator types (IP, domain, file hash, or behavior pattern).

# Instructor: Omar Santos @santosomar

# Import the required libraries
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnableBranch, RunnablePassthrough
from langchain_openai import ChatOpenAI

# Load environment variables from .env
load_dotenv()

# Create a ChatOpenAI model
model = ChatOpenAI(model="gpt-5-mini")

# Define prompt templates for different indicator types
ip_indicator_template = ChatPromptTemplate.from_messages([
    ("system", "You are an expert threat hunter specializing in network analysis."),
    ("human", """
    Generate a detailed threat hunting plan for this suspicious IP address: {indicator}
    
    Include:
    1. Initial data sources to check (logs, SIEM queries, etc.)
    2. Key artifacts to look for in network traffic
    3. Correlation strategies with other data points
    4. At least 3 specific hunt queries for common SIEM/EDR tools
    5. Recommendations for containment if malicious activity is confirmed
    """)
])

domain_indicator_template = ChatPromptTemplate.from_messages([
    ("system", "You are an expert threat hunter specializing in DNS and web traffic analysis."),
    ("human", """
    Generate a detailed threat hunting plan for this suspicious domain: {indicator}
    
    Include:
    1. Domain intelligence gathering techniques
    2. DNS query analysis approach
    3. Web traffic inspection methods
    4. At least 3 specific hunt queries for common SIEM/EDR tools
    5. Recommendations for containment if malicious activity is confirmed
    """)
])

hash_indicator_template = ChatPromptTemplate.from_messages([
    ("system", "You are an expert threat hunter specializing in malware analysis."),
    ("human", """
    Generate a detailed threat hunting plan for this suspicious file hash: {indicator}
    
    Include:
    1. File prevalence analysis approach
    2. Process execution context investigation
    3. File behavior and relationships to examine
    4. At least 3 specific hunt queries for common SIEM/EDR tools
    5. Recommendations for containment if malicious activity is confirmed
    """)
])

behavior_indicator_template = ChatPromptTemplate.from_messages([
    ("system", "You are an expert threat hunter specializing in adversary behavior analysis."),
    ("human", """
    Generate a detailed threat hunting plan for this suspicious behavior pattern: {indicator}
    
    Include:
    1. MITRE ATT&CK mapping
    2. Data sources needed to detect this behavior
    3. Timeline analysis approach
    4. At least 3 specific hunt queries for common SIEM/EDR tools
    5. Recommendations for containment if malicious activity is confirmed
    """)
])

# Define the indicator classification template
classification_template = ChatPromptTemplate.from_messages([
    ("system", "You are an expert threat intelligence analyst."),
    ("human", """
    Classify the following indicator as one of these types:
    - IP address
    - Domain
    - File hash
    - Behavior pattern
    
    Indicator: {indicator}
    
    Respond with ONLY the classification type, nothing else.
    """)
])

# Define a function to determine the indicator type more precisely
def determine_indicator_type(classification_result):
    classification = classification_result.strip().lower()
    
    if "ip" in classification:
        return "ip"
    elif "domain" in classification:
        return "domain"
    elif "hash" in classification or "file" in classification:
        return "hash"
    else:
        return "behavior"

# Define the runnable branches for handling different indicator types
branches = RunnableBranch(
    (
        lambda x: determine_indicator_type(x) == "ip",
        ip_indicator_template | model | StrOutputParser()
    ),
    (
        lambda x: determine_indicator_type(x) == "domain",
        domain_indicator_template | model | StrOutputParser()
    ),
    (
        lambda x: determine_indicator_type(x) == "hash",
        hash_indicator_template | model | StrOutputParser()
    ),
    behavior_indicator_template | model | StrOutputParser()  # Default branch for behavior patterns
)

# Create the classification chain
classification_chain = classification_template | model | StrOutputParser()

# Create a chain that combines classification with branching logic
from langchain.schema.runnable import RunnableMap

# Step 1: Create a map that runs classification and preserves input
input_and_classification = RunnableMap({
    "classification": lambda x: classification_chain.invoke({"indicator": x["indicator"]}),
    "indicator": lambda x: x["indicator"]
})

# Step 2: Create a function that routes to the appropriate branch based on classification
def route_to_branch(inputs):
    classification = inputs["classification"]
    indicator = inputs["indicator"]
    return branches.invoke(classification, {"indicator": indicator})

# Step 3: Chain them together
chain = input_and_classification.with_fallbacks([]).pipe(route_to_branch)

# Example indicators to test
examples = [
    "45.132.192.12",  # IP address
    "suspicious-malware-domain.net",  # Domain
    "a339b9fa2b8ddb3aefc35d9b2c37fd2f3f2b699f8c8f671d3d71f7b499fc9125",  # File hash
    "PowerShell execution with encoded commands followed by network connections to unusual ports"  # Behavior
]

# Function to run the chain with an example
def run_example(indicator):
    print(f"\n{'=' * 80}\nINDICATOR: {indicator}\n{'=' * 80}")
    result = chain.invoke({"indicator": indicator})
    print(result)

# Run examples if this script is executed directly
if __name__ == "__main__":
    print("THREAT HUNTING BRANCHING CHAIN EXAMPLE")
    print("This example demonstrates how to use branching chains to create specialized")
    print("threat hunting plans based on different types of indicators.")
    
    for example in examples:
        run_example(example)
