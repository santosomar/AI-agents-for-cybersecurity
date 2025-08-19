# Prompt Template Examples

This directory contains examples and documentation about creating and using `ChatPromptTemplate` with LangChain for generating prompts for models, with a focus on cybersecurity applications.

## Files Overview

### `chat_prompt_template.py`
This script demonstrates the use of `ChatPromptTemplate` from LangChain. It sets up a system message to define the AI's role as a senior cybersecurity analyst and a user message that includes a placeholder for `alert_details` (e.g., "Unusual outbound traffic..."). The script then invokes this template with specific alert details and utilizes a `ChatOpenAI` model (specifically `gpt-5-mini`) to generate a response. Finally, it prints both the structured list of messages sent to the model and the AI's contentful response, illustrating a clear example of crafting and using chat prompts for cybersecurity analysis.

### `messages_placeholders.py`
This script illustrates the use of `MessagesPlaceholder` within a `ChatPromptTemplate` in LangChain. This feature is designed to dynamically insert a sequence of messages, such as a conversation history, into a prompt. The script initializes a `ChatOpenAI` model (`gpt-5-mini`) and creates a chat prompt template that includes a system message, a `MessagesPlaceholder` for a `chat_history` variable, and a placeholder for new `user_input`. It demonstrates invoking this template with a predefined chat history and a new user question, then prints both the fully constructed prompt messages and the AI's generated response, showcasing how to maintain context in conversational AI.

### `prompt_template_example.py`
This script provides several examples of creating and using `ChatPromptTemplate` in LangChain, all utilizing the `ChatOpenAI` model (`gpt-5-mini`):
1.  **Prompt from Template**: Shows creating a simple prompt template from a string with a single placeholder (`{topic}`) (e.g., "Explain the security concept {topic}.").
2.  **Prompt with Multiple Placeholders**: Illustrates a template with multiple placeholders (`{adjective}`, `{vulnerability}`) to generate more complex prompts (e.g., "Create a {adjective} explanation about a {vulnerability}.").
3.  **Prompt with System and Human Messages**: Demonstrates creating a prompt template from a list of messages (tuples defining "system" and "human" roles) with placeholders (`{vulnerability_type}`, `{obfuscation_count}`) for scenarios like generating obfuscation techniques.
The script executes these examples and prints the generated prompts and model responses, offering a practical guide to different prompting strategies for cybersecurity tasks.

### `prompt_engineering_techniques.md`
This Markdown file serves as a comprehensive guide to various advanced prompt engineering techniques. It presents a table detailing methods such as:
- Chain-of-Thought (CoT)
- Tree-of-Thought (ToT)
- ReAct (Reason+Act)
- Self-Correction/Reflection
- Meta Prompting
- Iterative Refinement
- System-Level Instructions
- Contextual Priming
For each technique, the document provides a brief description, a key idea for its implementation in a prompt, and notes on its integration within LangChain Expression Language (LCEL) or LangGraph. It aims to help users enhance the reasoning, reliability, and adaptability of large language models by applying these structured and meta-level prompting strategies.

### Examples

1. **Prompt from Template**
   - Uses a template string with a placeholder for the topic.
   - Example: "Explain the security concept {topic}."
   - Generates a prompt explaining the security concept of "XSS attacks".

2. **Prompt with Multiple Placeholders**
   - Uses a template string with multiple placeholders for adjectives and vulnerabilities.
   - Example: "Create a {adjective} explanation about a {vulnerability}."
   - Generates a detailed explanation about an XSS vulnerability.

3. **Prompt with System and Human Messages (Using Tuples)**
   - Uses a list of messages with system and human messages as tuples.
   - Example: System message for setting context and human message for specific instructions.
   - Generates obfuscation technique examples for a specified vulnerability type (XSS) and count.

### Usage

Ensure you have the required libraries installed and environment variables set up as specified in the `.env` file.

Run the script:
```bash
python prompt_template_example.py
```

This will execute the examples and print the generated prompts and model responses.

### Dependencies

- `dotenv`: For loading environment variables.
- `langchain`: For creating and managing prompt templates.
- `langchain_openai`: For interacting with the OpenAI model.

**SECURITY NOTE**: Never commit your API keys to version control. Also, instead of using environment variables to store sensitive information, you can use a secrets management service like CyberArk Conjur, HashiCorp Vault or AWS Secrets Manager.

### Instructor

Omar Santos [@santosomar](https://github.com/santosomar)

