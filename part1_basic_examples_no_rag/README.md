# Basic Examples Without RAG

This directory contains fundamental examples demonstrating various aspects of working with language models, embeddings, and chat functionalities without using Retrieval Augmented Generation (RAG).

## Overview

These examples cover:
- Basic chat interactions with OpenAI and other models
- Embedding generation and usage
- Interactive chatbot development
- Integration with different model providers (OpenAI, Hugging Face, Ollama)
- Document processing and multimodal capabilities

## Files

### Core Examples
- `chat_model_basic.py`: A foundational example showing how to use LangChain with OpenAI's chat models. Demonstrates basic model invocation, message handling, and response processing.

- `chatbot_example.py`: A complete Streamlit-based chatbot implementation using OpenAI. Features include:
  - Interactive chat interface
  - Conversation history management
  - Environment variable handling
  - User-friendly web interface

- `embeddings.py`: Demonstrates text embedding generation using OpenAI's API. Shows how to:
  - Generate embeddings for text input
  - Use the text-embedding-3-small model
  - Process and handle embedding vectors

### Advanced Integration Examples
- `huggingface_example.py`: Shows integration with Hugging Face's transformers library:
  - Sentiment analysis using DistilBERT
  - Pipeline setup and configuration
  - Model loading and inference
  - Compatible with PyTorch, TensorFlow, or Flax

### Ollama Integration
- `ollama/basic_ollama_api.py`: Comprehensive example of using Ollama's API:
  - Basic text generation
  - Chat with conversation history
  - Streaming responses
  - Multi-modal analysis with LLaVA model
  - Image analysis capabilities

### Documentation
- `chunking_and_images.md`: Detailed guide on handling documents with images:
  - Multimodal document analysis techniques
  - PDF and image processing best practices
  - OCR integration strategies
  - Chunking strategies for documents with images

## Prerequisites

- Python 3.x
- Required packages:
  - `langchain`
  - `langchain-openai`
  - `python-dotenv`

## Setup

1. Install the required packages:

```bash
pip install langchain langchain-openai python-dotenv
```

2. Create a `.env` file in the root directory with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```
**SECURITY NOTE**: Never commit your API keys to version control. Also, instead of using environment variables to store sensitive information, you can use a secrets management service like CyberArk Conjur, HashiCorp Vault or AWS Secrets Manager.

## Usage

Run the example script:
```bash
python chat_model_basic.py
```

The script will:
1. Load your OpenAI API key from the environment
2. Initialize a chat model (gpt-5-mini)
3. Send a query about Retrieval Augmented Generation in Cybersecurity
4. Display both the full response object and its content

## Notes

- The example uses the "gpt-5-mini" model, but you can modify this to use other OpenAI models
- Make sure to keep your API key secure and never commit it to version control
- This is a basic example without RAG capabilities - see other examples for more advanced features


## Additional Resources

- [LangChain Chat Model Documentation](https://python.langchain.com/v0.2/docs/integrations/chat/)
- [OpenAI Chat Model Documentation](https://python.langchain.com/v0.2/docs/integrations/chat/openai/)


## Files

- `chat_model_basic.py`: Basic implementation of chat functionality using LangChain and OpenAI
- `embeddings.py`: Demonstrates how to generate text embeddings using OpenAI's embedding models

## Examples

### Chat Model Example
Basic chat interaction with OpenAI models through LangChain.

### Embeddings Example
The `embeddings.py` script shows how to:
- Generate embeddings for text input using OpenAI's API
- Use the "text-embedding-3-small" model
- Process and display embedding vectors

Example usage:
```bash
python embeddings.py
```



## Streamlit Interface

The chatbot example includes a Streamlit web interface that provides:
- A clean, interactive chat interface
- Real-time streaming responses
- Persistent chat history within the session
- Easy-to-use input field for questions

To run the Streamlit interface: 
```bash
streamlit run chatbot_example.py
```


## Security Considerations

### API Key Management
- API keys are loaded from environment variables using python-dotenv
- Never hardcode API keys in your source code
- Add `.env` to your `.gitignore` file

### Best Practices
- Regularly rotate your API keys
- Monitor API usage for unusual patterns
- Implement rate limiting for production deployments
- Validate and sanitize user inputs

## Part 1Project Structure

- `chat_model_basic.py`: Basic implementation of chat functionality using LangChain and OpenAI
- `embeddings.py`: Demonstrates how to generate text embeddings using OpenAI's embedding models
- `chatbot_example.py`: Streamlit interface for the chatbot example
- `.env`: Environment variables file for API keys
- `requirements.txt`: List of required packages

