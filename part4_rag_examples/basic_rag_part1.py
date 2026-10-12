# This script demonstrates how to create a Chroma vector store from a text file
# and persist it to disk. The script checks if the vector store already exists
# in the persistent directory and initializes it if it does not exist.

# Instructor: Omar Santos @santosomar

# importing the required libraries
import os

from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader, UnstructuredMarkdownLoader
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import OpenAI


# Defining the directory containing the relevant data 
# In this example, the text file contains information about SSRF vulnerabilities
# # and attacks.
current_dir = os.path.dirname(os.path.abspath(__file__))
# List of files to load into the vector store
files_to_load = [
    os.path.join(current_dir, "data", "ssrf.txt"),
    os.path.join(current_dir, "data", "llm_cheatsheet.md"),
]
persistent_directory = os.path.join(current_dir, "db", "chroma_db_security")

# Checking if the Chroma vector store already exists
if not os.path.exists(persistent_directory):
    print("Persistent directory does not exist. Initializing vector store...")

    # Initialize the text splitter
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    # A list to hold all document chunks
    all_chunks = []

    print("\n--- Loading and Processing Documents ---")
    # Loop through each file
    for file_path in files_to_load:
        # Ensuring that the text file exists
        if not os.path.exists(file_path):
            print(f"Warning: The file {file_path} does not exist. Skipping.")
            continue

        print(f"\n-> Processing: {os.path.basename(file_path)}")
        # Use the appropriate loader based on file extension
        if file_path.endswith(".md"):
            loader = UnstructuredMarkdownLoader(file_path)
        else:
            loader = TextLoader(file_path)

        # Load and split the document
        documents = loader.load()
        docs = text_splitter.split_documents(documents)
        all_chunks.extend(docs)

        # Display information about the chunks for the current document
        print(f"Number of chunks: {len(docs)}")
        if docs:
            print(f"Sample chunk:\n{docs[0].page_content}\n")

    print("\n--- Summary ---")
    print(f"Total documents processed: {len(files_to_load)}")
    print(f"Total document chunks created: {len(all_chunks)}")

    if not all_chunks:
        raise ValueError("No documents were loaded. Please check the file paths.")

    # Creating embeddings
    # Define the embedding model (in this case, OpenAI's text-embedding-3-small. 
    # Note: You can also use other embedding models such as HuggingFace's SentenceTransformers, Cohere, or 
    # any other embedding model that is more appropriate for your use case. Refer to the "Selecting Embedding 
    # Models" white paper at:
    # https://sec.cloudapps.cisco.com/security/center/resources/selecting-embedding-models 
    # for some tips on selecting an embedding model.)
    print("\n--- Creating embeddings ---")
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small"
    )  # Update to a valid embedding model if needed
    print("\n--- Finished creating embeddings ---")

    # Creating the vector store/database
    print("\n--- Creating vector store ---")
    db = Chroma.from_documents(
        all_chunks, embeddings, persist_directory=persistent_directory
    )
    print("\n--- Finished creating vector store ---")

else:
    print("Vector store already exists. No need to initialize.")
