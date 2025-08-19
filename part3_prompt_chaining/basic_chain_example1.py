# This example demonstrates how to create a chain using LangChain Expression Language (LCEL) and run it.
# The chain consists of a prompt template, an OpenAI model, a string output parser, and two parallel branches for analyzing pros and cons.
# The pros and cons branches are combined into a final review using a lambda function.
# The chain is run with a product name as input, and the final review is printed.
# Instructor: Omar Santos @santosomar

# Import the required libraries
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnableLambda
from langchain_openai import ChatOpenAI

# Load environment variables from .env
load_dotenv()

# Create a ChatOpenAI model
model = ChatOpenAI(model="gpt-5-mini")

# Define prompt templates
prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are an ethical hacker providing guidance on {topic}."),
        ("human", "Provide {tip_count} techniques and examples of tools."),

    ]
)
# Define additional processing steps using RunnableLambda
uppercase_output = RunnableLambda(lambda x: x.upper())
count_words = RunnableLambda(lambda x: f"Word count: {len(x.split())}\n{x}")

# Create the combined chain using LangChain Expression Language (LCEL)
chain = prompt_template | model | StrOutputParser() | uppercase_output | count_words

# Run the chain
result = chain.invoke({"topic": "scanning a web application", "tip_count": 5})

# Output
print(result)
