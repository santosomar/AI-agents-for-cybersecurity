# This is a basic example of using the Langchain OpenAI Chat Model.
# This example demonstrates how to invoke the model with a message and print the result.
# The model used in this example is "gpt-5-mini".
# Author: Omar Santos @santosomar

# LangChain Chat Model Documents: https://python.langchain.com/v0.2/docs/integrations/chat/
# OpenAI Chat Model Documents: https://python.langchain.com/v0.2/docs/integrations/chat/openai/

# Import the required libraries
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load environment variables from .env
load_dotenv()

# Create an instance of the ChatOpenAI model with the model name
model = ChatOpenAI(model="gpt-5-mini")

# Interact with the model by invoking it with a message
# The message is a string that represents the input to the model
# The result is a dictionary that contains the response from the model

result = model.invoke("What is Retrieval Augmented Generation and how can it be used for Cybersecurity?")
print("Full result:")
print(result)
print("Content only:")
print(result.content)
