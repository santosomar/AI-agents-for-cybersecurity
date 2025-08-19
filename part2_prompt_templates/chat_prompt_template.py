# We will create a chat prompt template that will be used to generate a response to a user's question.
# The explanation is available at: https://cybercopilot.org/Rmr98k1
# Instructor: Omar Santos @santosomar

# LangChain Chat Prompt Template Documents: https://python.langchain.com/docs/how_to/#prompt-templates 
# OpenAI Chat Model Documents: https://python.langchain.com/docs/how_to/#chat-models
# LangChain Expression Language (LCEL): https://python.langchain.com/docs/how_to/#langchain-expression-language-lcel

# Import the required libraries
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Create a ChatOpenAI model
model = ChatOpenAI(model="gpt-5-mini")

# Define the chat structure with a system message for context and a user message for the query.
chat_prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are a senior cybersecurity analyst. Your role is to explain threats clearly and suggest mitigation strategies."),
    ("user", "We received an alert about the following activity: {alert_details}. What is our primary concern here?")
])

# Provide the specific details for the user's question.
chat_prompt_value = chat_prompt_template.invoke({
    "alert_details": "Unusual outbound traffic to an IP address in a high-risk country from a developer's workstation."
})

# The chat_prompt_value now contains a structured list of messages.
print(chat_prompt_value.to_messages())

# Invoke the model with the chat prompt value
result = model.invoke(chat_prompt_value)

# Output
print(result.content)

# Output:
# [SystemMessage(content='You are a senior cybersecurity analyst. Your role is to explain threats clearly and suggest mitigation strategies.'),
#  HumanMessage(content="We received an alert about the following activity: Unusual outbound traffic to an IP address in a high-risk country from a developer's workstation. What is our primary concern here?")]