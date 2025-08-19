# Threat Hunting Parallel Chain Example
# This script demonstrates how to use parallel chains in LangChain to create
# a comprehensive threat hunting workflow that analyzes indicators from multiple perspectives simultaneously.
# The chain will process an indicator through multiple specialized analysis paths in parallel
# and combine the results into a comprehensive threat hunting report.

# Instructor: Omar Santos @santosomar

# Import the required libraries
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnableParallel, RunnableLambda
from langchain_openai import ChatOpenAI

# Load environment variables from .env
load_dotenv()

# Create a ChatOpenAI model
model = ChatOpenAI(model="gpt-5-mini")

# Define the initial indicator assessment template
initial_assessment_template = ChatPromptTemplate.from_messages([
    ("system", "You are an expert threat intelligence analyst."),
    ("human", """
    Provide a brief initial assessment of the following potential threat indicator:
    
    {indicator}
    
    Include:
    1. Type of indicator (IP, domain, hash, behavior pattern, etc.)
    2. Initial risk assessment (low, medium, high)
    3. Potential threat categories associated with this indicator
    """)
])

# Define specialized analysis templates for different perspectives

# Technical Analysis Template
technical_analysis_template = ChatPromptTemplate.from_messages([
    ("system", "You are a technical threat analyst specializing in IOC analysis."),
    ("human", """
    Analyze the following indicator from a technical perspective:
    
    {indicator}
    
    Provide:
    1. Technical characteristics and attributes
    2. Associated TTPs (Tactics, Techniques, and Procedures)
    3. Potential malware families or threat actors known to use similar indicators
    4. Technical detection methods (regex patterns, YARA rules, etc.)
    """)
])

# Threat Context Template
threat_context_template = ChatPromptTemplate.from_messages([
    ("system", "You are a threat intelligence analyst specializing in threat context."),
    ("human", """
    Provide threat context for the following indicator:
    
    {indicator}
    
    Include:
    1. Historical usage of similar indicators
    2. Known threat campaigns that might be associated
    3. Geographic and industry targeting patterns
    4. Temporal patterns (is this a new or evolving threat?)
    """)
])

# Hunting Strategy Template
hunting_strategy_template = ChatPromptTemplate.from_messages([
    ("system", "You are a threat hunter specializing in detection strategies."),
    ("human", """
    Develop a hunting strategy for the following indicator:
    
    {indicator}
    
    Include:
    1. Data sources to query (logs, SIEM, EDR, etc.)
    2. At least 3 specific hunt queries for common security tools
    3. Artifacts and evidence to look for
    4. False positive scenarios to consider
    """)
])

# Mitigation Template
mitigation_template = ChatPromptTemplate.from_messages([
    ("system", "You are a security operations specialist."),
    ("human", """
    Recommend mitigation and response actions for the following potential threat indicator:
    
    {indicator}
    
    Include:
    1. Immediate containment actions if the indicator is confirmed malicious
    2. Monitoring recommendations
    3. Long-term defensive measures
    4. Stakeholder communication recommendations
    """)
])

# Define functions for each analysis branch

def perform_technical_analysis(indicator_info):
    """
    Performs technical analysis on the indicator.
    
    Args:
        indicator_info (str): The indicator to analyze
        
    Returns:
        str: Formatted prompt for technical analysis
    """
    return technical_analysis_template.format_prompt(indicator=indicator_info)

def gather_threat_context(indicator_info):
    """
    Gathers threat context information for the indicator.
    
    Args:
        indicator_info (str): The indicator to analyze
        
    Returns:
        str: Formatted prompt for threat context analysis
    """
    return threat_context_template.format_prompt(indicator=indicator_info)

def develop_hunting_strategy(indicator_info):
    """
    Develops a hunting strategy for the indicator.
    
    Args:
        indicator_info (str): The indicator to analyze
        
    Returns:
        str: Formatted prompt for hunting strategy development
    """
    return hunting_strategy_template.format_prompt(indicator=indicator_info)

def recommend_mitigations(indicator_info):
    """
    Recommends mitigations for the indicator.
    
    Args:
        indicator_info (str): The indicator to analyze
        
    Returns:
        str: Formatted prompt for mitigation recommendations
    """
    return mitigation_template.format_prompt(indicator=indicator_info)

# Create the combined threat hunting report
def create_threat_hunting_report(initial_assessment, technical_analysis, threat_context, hunting_strategy, mitigations):
    """
    Combines all analysis components into a comprehensive threat hunting report.
    
    Args:
        initial_assessment (str): Initial assessment of the indicator
        technical_analysis (str): Technical analysis of the indicator
        threat_context (str): Threat context information
        hunting_strategy (str): Hunting strategy
        mitigations (str): Recommended mitigations
        
    Returns:
        str: Comprehensive threat hunting report
    """
    report = f"""
# COMPREHENSIVE THREAT HUNTING REPORT

## EXECUTIVE SUMMARY
{initial_assessment}

## TECHNICAL ANALYSIS
{technical_analysis}

## THREAT CONTEXT
{threat_context}

## HUNTING STRATEGY
{hunting_strategy}

## RECOMMENDED MITIGATIONS
{mitigations}
"""
    return report

# Define the parallel branches using LCEL
technical_branch = (
    RunnableLambda(lambda x: perform_technical_analysis(x)) | model | StrOutputParser()
)

context_branch = (
    RunnableLambda(lambda x: gather_threat_context(x)) | model | StrOutputParser()
)

hunting_branch = (
    RunnableLambda(lambda x: develop_hunting_strategy(x)) | model | StrOutputParser()
)

mitigation_branch = (
    RunnableLambda(lambda x: recommend_mitigations(x)) | model | StrOutputParser()
)

# Create the initial assessment chain
initial_assessment_chain = initial_assessment_template | model | StrOutputParser()

# Create the parallel analysis chain
parallel_analysis = RunnableParallel(
    technical_analysis=technical_branch,
    threat_context=context_branch,
    hunting_strategy=hunting_branch,
    mitigations=mitigation_branch
)

# Create the full chain that:
# 1. Performs initial assessment
# 2. Passes the indicator to parallel analysis branches
# 3. Combines all results into a comprehensive report
def process_indicator_and_run_parallel(inputs):
    indicator = inputs["indicator"]
    initial_assessment = inputs["initial_assessment"]
    
    # Run parallel analyses
    parallel_results = parallel_analysis.invoke(indicator)
    
    # Create comprehensive report
    return create_threat_hunting_report(
        initial_assessment,
        parallel_results["technical_analysis"],
        parallel_results["threat_context"],
        parallel_results["hunting_strategy"],
        parallel_results["mitigations"]
    )

# Create a map that runs initial assessment and preserves input
input_and_assessment = RunnableParallel({
    "indicator": lambda x: x["indicator"],
    "initial_assessment": lambda x: initial_assessment_chain.invoke({"indicator": x["indicator"]})
})

# Chain everything together
chain = input_and_assessment | RunnableLambda(process_indicator_and_run_parallel)

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
    print("THREAT HUNTING PARALLEL CHAIN EXAMPLE")
    print("This example demonstrates how to use parallel chains to analyze threat indicators")
    print("from multiple perspectives simultaneously and generate a comprehensive report.")
    
    # Run with a single example to demonstrate
    run_example(examples[0])  # Using the IP address example
    
    # Uncomment to run all examples
    # for example in examples:
    #     run_example(example)
