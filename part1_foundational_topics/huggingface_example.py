''' 
This is a basic example of how to use the Hugging Face pipeline for 
sentiment analysis.
It uses the 'distilbert-base-uncased-finetuned-sst-2-english' model.
The model is a fine-tuned DistilBERT model for sentiment analysis.

Before running this example, make sure to install the required dependencies:
pip install transformers torch

Note: If you prefer TensorFlow or Flax instead of PyTorch, you can install:
pip install transformers tensorflow  # for TensorFlow
pip install transformers flax  # for Flax
'''

from transformers import pipeline

# Example usage
classifier = pipeline("sentiment-analysis")
result = classifier("Omar, I LOVE using Hugging Face!")
print(result)

