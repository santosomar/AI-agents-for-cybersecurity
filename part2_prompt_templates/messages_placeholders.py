# Messages Placeholders
# Messages placeholders allow you to include a list of messages in a prompt template.
# The explanation is available at: https://cybercopilot.org/QOrM2Qm
# Instructor: Omar Santos @santosomar

# LangChain Chat Prompt Template Documents: https://python.langchain.com/docs/how_to/#prompt-templates 
# OpenAI Chat Model Documents: https://python.langchain.com/docs/how_to/#chat-models
# LangChain Expression Language (LCEL): https://python.langchain.com/docs/how_to/#langchain-expression-language-lcel

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Create a ChatOpenAI model
model = ChatOpenAI(model="gpt-5-mini")
prompt_with_history = ChatPromptTemplate.from_messages([
 ("system", "You are a helpful assistant."),
 MessagesPlaceholder(variable_name="chat_history"),
 ("user", "{user_input}")
])
history = [
 HumanMessage(content="What is a CVE?"),
 AIMessage(content="A CVE is a Common Vulnerabilities and Exposures identifier."),
 HumanMessage(content="What is a Common Vulnerabilities and Exposures identifier?")
]
final_prompt_value = prompt_with_history.invoke({
 "chat_history": history,
 "user_input": "What is a CVE?"
})
print(final_prompt_value.to_messages())

result = model.invoke(final_prompt_value)
print(result.content)
