# We will create a branching chain that classifies the severity of a vulnerability and generates a response based on the severity level.
# The chain will consist of a classification template, a model, and branching chains for critical, high, medium, and low severity vulnerabilities.
# The branching chains will generate responses based on the severity level of the vulnerability.
# The classification and response generation chains will be combined into one chain.

# Instructor: Omar Santos @santosomar

# Import the required libraries
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnableBranch
from langchain_openai import ChatOpenAI

# Load environment variables from .env
load_dotenv()

# Create a ChatOpenAI model
model = ChatOpenAI(model="gpt-5-mini")

# Define prompt templates for different vulnerability types
critical_vuln_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are an expert ethical hacker and security analyst."),
        ("human",
         "Generate pen test plan, examples of tools, and a report with an urgent mitigation plan for this critical vulnerability: {vulnerability}."),
    ]
)

high_vuln_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are an expert ethical hacker and security analyst."),
        ("human",
         "Generate a detailed remediation strategy for this high-severity vulnerability: {vulnerability}."),
    ]
)

medium_vuln_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are an expert ethical hacker and security analyst."),
        (
            "human",
            "Propose a mitigation approach for this medium-severity vulnerability: {vulnerability}.",
        ),
    ]
)

low_vuln_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are an expert ethical hacker and security analyst."),
        (
            "human",
            "Suggest best practices to address this low-severity vulnerability: {vulnerability}.",
        ),
    ]
)

# Define the vulnerability classification template
classification_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are an expert ethical hacker and security analyst."),
        ("human",
         "Classify the severity of this vulnerability as critical, high, medium, or low: {vulnerability}."),
    ]
)

# Define the runnable branches for handling vulnerabilities
branches = RunnableBranch(
    (
        lambda x: "critical" in x.lower(),
        critical_vuln_template | model | StrOutputParser()  # Critical vulnerability chain
    ),
    (
        lambda x: "high" in x.lower(),
        high_vuln_template | model | StrOutputParser()  # High vulnerability chain
    ),
    (
        lambda x: "medium" in x.lower(),
        medium_vuln_template | model | StrOutputParser()  # Medium vulnerability chain
    ),
    low_vuln_template | model | StrOutputParser()  # Low vulnerability chain (default)
)

# Create the classification chain
classification_chain = classification_template | model | StrOutputParser()

# Combine classification and response generation into one chain
chain = classification_chain | branches

# Run the chain with an example vulnerability
# Critical vulnerability - "Unpatched remote code execution vulnerability in the web server"
# High vulnerability - "Weak encryption used for storing user passwords in the database"
# Medium vulnerability - "Cross-site scripting (XSS) vulnerability in the user input fields"
# Low vulnerability - "Outdated SSL/TLS version used in some non-critical services"

vulnerability = "Unpatched remote code execution vulnerability in an Apache httpd web server"
result = chain.invoke({"vulnerability": vulnerability})

# Output the result
print(result)