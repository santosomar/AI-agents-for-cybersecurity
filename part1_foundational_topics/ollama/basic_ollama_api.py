#!/usr/bin/env python3
# This is a basic example of using the Ollama API
# You can run this file directly with `python basic_ollama_api.py`
# Author: Omar Santos @santosomar

# Ollama API Documentation: https://ollama.com/docs/api

# Import the required libraries
import ollama

# Basic text generation
def simple_generation(prompt: str, model: str = "llama3.2"):
    response = ollama.generate(model=model, prompt=prompt)
    return response['response']

# Chat with conversation history
def chat_with_history(messages: list, model: str = "llama3.2"):
    response = ollama.chat(
        model=model,
        messages=messages,
    )
    return response['message']['content']

# Streaming response handler
def streaming_chat(messages: list, model: str = "llama3.2"):
    full_response = ""
    for chunk in ollama.chat(
        model=model,
        messages=messages,
        stream=True
    ):
        content = chunk['message']['content']
        full_response += content
        print(content, end='', flush=True)  # Real-time display
    return full_response

# Multi-modal analysis (requires LLaVA model)
def analyze_image(image_path: str, question: str):
    with open(image_path, 'rb') as file:
        response = ollama.chat(
            model='llava',
            messages=[{
                'role': 'user',
                'content': question,
                'images': [file.read()]
            }]
        )
    return response['message']['content']

# Example usage
if __name__ == "__main__":
    # Basic generation
    print(simple_generation("Explain quantum computing in simple terms"))
    
    # Chat conversation
    messages = [
        {'role': 'user', 'content': 'What causes northern lights?'}
    ]
    print(chat_with_history(messages))
    
    # Streaming chat
    messages = [
        {'role': 'user', 'content': 'Write a short poem about AI'}
    ]
    streaming_chat(messages)
    
    # Image analysis (requires ollama pull llava)
    # print(analyze_image('diagram.png', 'Explain this technical diagram'))
