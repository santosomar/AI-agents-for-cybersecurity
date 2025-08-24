# This script demonstrates how to use the OpenAI API to generate embeddings for a given text string.
# The embeddings are numerical vectors that capture the semantic meaning of the text.
# The script uses the OpenAI client to create embeddings for the input text.
# The model used in this example is "text-embedding-3-small".

# Instructor: Omar Santos @santosomar

# Import the required libraries
from openai import OpenAI
client = OpenAI()

# Create embeddings for the input text using the "text-embedding-3-small" model
response = client.embeddings.create(
    input="This is an example from Omar.",
    model="text-embedding-3-small"
)

# Print the embeddings generated for the input text
print(response.data[0].embedding)