# Security Incident Analysis Chain Example
# This example demonstrates a more complex chain for security incident analysis using LangChain Expression Language (LCEL).
# The chain consists of multiple analysis branches that handle different aspects of a security incident.
# Instructor: Omar Santos @santosomar

# Import the required libraries
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnableLambda, RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableBranch
import json

# Load environment variables from .env
load_dotenv()

# Create a ChatOpenAI model
model = ChatOpenAI(model="gpt-5-mini")

# Define the initial incident analysis prompt template
initial_analysis_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a cybersecurity analyst. Analyze the following security incident details."),
        ("human", "Incident details: {incident_details}\n\nProvide an initial assessment of this security incident.")
    ]
)

# Define specialized analysis prompt templates
threat_actor_analysis_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a threat intelligence specialist focused on threat actor attribution."),
        ("human", "Based on this incident information: {incident_details}\n\nAnd this initial analysis: {initial_analysis}\n\nIdentify possible threat actors, their TTPs (Tactics, Techniques, and Procedures), and confidence level of attribution.")
    ]
)

impact_assessment_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a business impact analyst for cybersecurity incidents."),
        ("human", "Based on this incident information: {incident_details}\n\nAnd this initial analysis: {initial_analysis}\n\nAssess the potential business impact, regulatory implications, and data exposure risks.")
    ]
)

mitigation_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a cybersecurity incident response specialist."),
        ("human", "Based on this incident information: {incident_details}\n\nAnd this initial analysis: {initial_analysis}\n\nProvide immediate containment steps, mitigation strategies, and recommended tools for incident response.")
    ]
)

# Define the final recommendation prompt template that integrates all analyses
final_recommendation_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a CISO (Chief Information Security Officer) providing executive summaries of security incidents."),
        ("human", """
        Incident Details: {incident_details}
        
        Initial Analysis: {initial_analysis}
        
        Threat Actor Analysis: {threat_analysis}
        
        Impact Assessment: {impact_assessment}
        
        Mitigation Recommendations: {mitigation_recommendations}
        
        Based on all this information, provide an executive summary, strategic recommendations, and next steps for handling this security incident.
        """)
    ]
)

# Define JSON formatter for structured output
def format_to_json(content, section_name):
    return json.dumps({section_name: content}, indent=2)

# Create the initial analysis chain
initial_analysis_chain = initial_analysis_prompt | model | StrOutputParser()

# Create specialized analysis chains with JSON formatting
threat_analysis_chain = (
    threat_actor_analysis_prompt 
    | model 
    | StrOutputParser() 
    | RunnableLambda(lambda x: format_to_json(x, "threat_analysis"))
)

impact_assessment_chain = (
    impact_assessment_prompt 
    | model 
    | StrOutputParser() 
    | RunnableLambda(lambda x: format_to_json(x, "impact_assessment"))
)

mitigation_chain = (
    mitigation_prompt 
    | model 
    | StrOutputParser() 
    | RunnableLambda(lambda x: format_to_json(x, "mitigation"))
)

# Define a conditional branch to customize analysis based on incident type
def determine_incident_type(inputs):
    incident_text = inputs["incident_details"].lower()
    if "malware" in incident_text or "ransomware" in incident_text:
        return "malware"
    elif "phishing" in incident_text or "social engineering" in incident_text:
        return "phishing"
    elif "data breach" in incident_text or "exfiltration" in incident_text:
        return "data_breach"
    else:
        return "general"

# Define specialized malware chain
malware_specific_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a malware analyst."),
    ("human", "Analyze this malware incident: {incident_details}\n\nProvide malware family identification, IOCs (Indicators of Compromise), and specific malware removal steps.")
])

malware_chain = malware_specific_prompt | model | StrOutputParser() | RunnableLambda(lambda x: format_to_json(x, "malware_analysis"))

# Define specialized phishing chain
phishing_specific_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a phishing attack specialist."),
    ("human", "Analyze this phishing incident: {incident_details}\n\nIdentify phishing campaign patterns, email indicators, and compromised credential risks.")
])

phishing_chain = phishing_specific_prompt | model | StrOutputParser() | RunnableLambda(lambda x: format_to_json(x, "phishing_analysis"))

# Define specialized data breach chain
data_breach_specific_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a data breach investigator."),
    ("human", "Analyze this data breach incident: {incident_details}\n\nDetermine data types exposed, regulatory reporting requirements, and data protection recommendations.")
])

data_breach_chain = data_breach_specific_prompt | model | StrOutputParser() | RunnableLambda(lambda x: format_to_json(x, "data_breach_analysis"))

# Create the incident type-specific analysis branch
incident_specific_chain = RunnableBranch(
    (lambda x: x["incident_type"] == "malware", malware_chain),
    (lambda x: x["incident_type"] == "phishing", phishing_chain),
    (lambda x: x["incident_type"] == "data_breach", data_breach_chain),
    RunnableLambda(lambda x: format_to_json("General incident analysis - no specific chain available", "general_analysis"))
)


# Create the complete analysis pipeline
def full_analysis_chain():
    # Step 1: Initial analysis
    initial_chain = RunnablePassthrough.assign(
        initial_analysis=initial_analysis_chain
    )
    
    # Step 2: Add incident type classification
    with_incident_type = initial_chain.assign(
        incident_type=RunnableLambda(determine_incident_type)
    )
    
    # Step 3: Run specialized analyses in parallel
    parallel_analysis = with_incident_type.assign(
        threat_analysis=threat_analysis_chain,
        impact_assessment=impact_assessment_chain,
        mitigation_recommendations=mitigation_chain,
        specialized_analysis=incident_specific_chain
    )
    
    # Step 4: Generate final recommendation
    final_chain = parallel_analysis.assign(
        executive_summary=lambda x: (
            final_recommendation_prompt | model | StrOutputParser()
        ).invoke(x)
    )
    
    return final_chain

# Create the final chain
security_incident_chain = full_analysis_chain()

# Example usage
if __name__ == "__main__":
    # Example security incident
    incident_details = """
    On May 15, 2026, our SOC detected unusual network traffic from the finance department servers at 2:30 AM. 
    Investigation revealed PowerShell scripts executing on multiple workstations and data being exfiltrated to an 
    unknown IP address (198.51.100.123). Approximately 2GB of data was transferred before the connection was terminated. 
    Multiple sensitive files appear to be encrypted with a .locked extension. A ransomware note was found requesting 
    5 Bitcoin payment within 48 hours. Initial endpoint logs show the compromise began via a phishing email with 
    an Excel attachment containing macros.
    """
    
    # Run the analysis chain
    result = security_incident_chain.invoke({"incident_details": incident_details})
    
    # Output the executive summary
    print("EXECUTIVE SUMMARY:\n")
    print(result["executive_summary"])
    
    # Optionally, print the full analysis results
    print("\nFULL INCIDENT ANALYSIS:\n")
    print(json.dumps(
        {
            "threat_analysis": json.loads(result["threat_analysis"])["threat_analysis"],
            "impact_assessment": json.loads(result["impact_assessment"])["impact_assessment"],
            "mitigation_recommendations": json.loads(result["mitigation_recommendations"])["mitigation"],
            "specialized_analysis": json.loads(result["specialized_analysis"])
        }, 
        indent=2
    ))
