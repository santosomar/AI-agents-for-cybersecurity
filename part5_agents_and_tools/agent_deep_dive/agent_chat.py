# This is a basic example of using the Langchain agent with tools and memory.
# The agent maintains context using memory to remember the conversation history.
# It uses a structured chat prompt to guide the conversation and tools to perform actions.
# The agent can provide helpful answers using available tools and maintain context across interactions.
# It uses a ChatOpenAI model to generate responses based on the input query.
# The agent can handle parsing errors gracefully and provides detailed logging for debugging purposes.
# Instructor: Omar Santos @santosomar

from dotenv import load_dotenv
from langchain import hub
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI

# Load environment variables from .env file
load_dotenv()


# Define Tools for the Agent to Use 
def get_current_time(*args, **kwargs):
    """
    Returns the current time in H:MM AM/PM format.
    """
    import datetime

    now = datetime.datetime.now()
    return now.strftime("%I:%M %p")


def search_wikipedia(query):
    """
    Searches Wikipedia for information on the given query.
    """
    from wikipedia import summary

    try:
        # Limit to two sentences for brevity
        return summary(query, sentences=2)
    except:
        return "I couldn't find any information on that."


# List of tools available to the agent with descriptions and functions
tools = [
    Tool(
        name="Time",
        func=get_current_time,
        description="Useful for when you need to know the current time.",
    ),
    Tool(
        name="Wikipedia",
        func=search_wikipedia,
        description="Useful for when you need to know information about a topic.",
    ),
]

# Pull the structured chat prompt from the hub to guide the conversation with the agent
prompt = hub.pull("hwchase17/structured-chat-agent")

# Create a ChatOpenAI model for generating responses to user queries using gpt-5-mini model. You can use any other model as well.
llm = ChatOpenAI(model="gpt-5-mini")

# Create a structured Chat Agent with Conversation Buffer Memory
# ConversationBufferMemory stores the conversation history, allowing the agent to maintain context across interactions
memory = ConversationBufferMemory(
    memory_key="chat_history", return_messages=True)

# create_structured_chat_agent initializes a chat agent designed to interact using a structured prompt and tools
# It combines the language model (llm), tools, and prompt to create an interactive agent
agent = create_structured_chat_agent(llm=llm, tools=tools, prompt=prompt)

# AgentExecutor is responsible for managing the interaction between the user input, the agent, and the tools
# It also handles memory to ensure context is maintained throughout the conversation
# The handle_parsing_errors flag allows the agent to handle any parsing errors gracefully
# The verbose flag enables detailed logging for debugging purposes
agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    verbose=True,
    memory=memory,  # Pass the memory object to the AgentExecutor
    handle_parsing_errors=True,  # Handle parsing errors gracefully
)

# System prompt to set the context for the chat
# SystemMessage is used to define a message from the system to the agent,
# setting initial instructions or context
# The initial message provides an overview of the agent's capabilities to the user
initial_message = "You are an AI assistant that can provide helpful answers using available tools.\nIf you are unable to answer, you can use the following tools: Time and Wikipedia."
memory.chat_memory.add_message(SystemMessage(content=initial_message))

# Chat Loop to interact with the user
while True:
    user_input = input("User:  ")
    if user_input.lower() == "exit":
        break

    # Add the user's message to the conversation memory
    memory.chat_memory.add_message(HumanMessage(content=user_input))

    # Invoke the agent with the user input and the current chat history
    response = agent_executor.invoke({"input": user_input})
    print("Bot:", response["output"])

    # Add the agent's response to the conversation memory
    memory.chat_memory.add_message(AIMessage(content=response["output"]))
