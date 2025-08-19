# This script demonstrates how to create a ChatPromptTemplate using a template string and a list of messages.
# The ChatPromptTemplate is used to generate prompts for the model.
# Instructor: Omar Santos @santosomar
# LangChain Prompt Template Docs: https://python.langchain.com/v0.2/docs/concepts/#prompt-templates

# Import the required libraries
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# Load environment variables from .env
load_dotenv()

# Create a ChatOpenAI model
model = ChatOpenAI(model="gpt-5-mini")

# EXAMPLE 1: Create a ChatPromptTemplate using a template string
# The template string contains a placeholder for the topic
print("-----EXAMPLE 1: Prompt from Template-----")
template = "Explain the security concept {topic}."
prompt_template = ChatPromptTemplate.from_template(template)

prompt = prompt_template.invoke({"topic": "XSS attacks"})
result = model.invoke(prompt)
print(result.content)

# EXAMPLE 2: Prompt with Multiple Placeholders
# Create a ChatPromptTemplate using a template string with multiple placeholders for adjectives and vulnerabilities
print("\n----- EXAMPLE 2: Prompt with Multiple Placeholders -----\n")
template_multiple = """You are a helpful ethical hacker assistant.
Human: Create a {adjective} explanation about a {vulnerability}.
Assistant:"""
prompt_multiple = ChatPromptTemplate.from_template(template_multiple)
prompt = prompt_multiple.invoke({"adjective": "detailed", "vulnerability": "XSS"})

result = model.invoke(prompt)
print(result.content)

# EXAMPLE 3: Prompt with System and Human Messages (Using Tuples)
# Create a ChatPromptTemplate using a list of messages with system and human messages as tuples with placeholders for vulnerability type and obfuscation count
print("\n----- EXAMPLE 3: Prompt with System and Human Messages (Tuple) -----\n")
messages = [
    ("system", "You are an ethical hacker and exploit developer that creates obfuscation techniques for this type of vulnerability {vulnerability_type}."),
    ("human", "Create  {obfuscation_count} obfuscation technique examples."),
]
prompt_template = ChatPromptTemplate.from_messages(messages)
prompt = prompt_template.invoke({"vulnerability_type": "XSS", "obfuscation_count": 3})
result = model.invoke(prompt)
print(result.content)
