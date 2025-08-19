# This script demonstrates how to scrape a web page, split the content into chunks, create embeddings for the chunks,
# persist the vector store, and use a RAG chain to answer questions based on the scraped content.

# Instructor: Omar Santos @santosomar

# Import the required libraries
import os

from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain.text_splitter import CharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Load environment variables from .env
load_dotenv()

# Define the persistent directory
current_dir = os.path.dirname(os.path.abspath(__file__))
db_dir = os.path.join(current_dir, "db")
persistent_directory = os.path.join(db_dir, "hacker_training")

# Step 1: Scrape the content from hackertraining.org using WebBaseLoader
# WebBaseLoader loads web pages and extracts their content
urls = ["https://hackertraining.org"]

# Create a loader for web content
loader = WebBaseLoader(urls)
documents = loader.load()

# Step 2: Split the scraped content into chunks
# CharacterTextSplitter splits the text into smaller chunks
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
docs = text_splitter.split_documents(documents)

# Display information about the split documents
print("\n--- Document Chunks Information ---")
print(f"Number of document chunks: {len(docs)}")
print(f"Sample chunk:\n{docs[0].page_content}\n")

# Step 3: Create embeddings for the document chunks
# OpenAIEmbeddings turns text into numerical vectors that capture semantic meaning
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Step 4: Create and persist the vector store with the embeddings
# Chroma stores the embeddings for efficient searching
if not os.path.exists(persistent_directory):
    print(f"\n--- Creating vector store in {persistent_directory} ---")
    db = Chroma.from_documents(docs, embeddings, persist_directory=persistent_directory)
    print(f"--- Finished creating vector store in {persistent_directory} ---")
else:
    print(f"Vector store {persistent_directory} already exists. No need to initialize.")
    db = Chroma(persist_directory=persistent_directory, embedding_function=embeddings)

# Step 5: Query the vector store
# Create a retriever for querying the vector store
retriever = db.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3},
)

# Define the user's question
query = "What is hackertraining.org all about?"

# Retrieve relevant documents based on the query
relevant_docs = retriever.invoke(query)

# Display the relevant results with metadata
print("\n--- Relevant Documents from the vector store ---")
for i, doc in enumerate(relevant_docs, 1):
    print(f"Document {i}:\n{doc.page_content}\n")
    if doc.metadata:
        print(f"Source: {doc.metadata.get('source', 'Unknown')}\n")

# Step 6: Create a RAG chain to answer the question
print("\n--- Putting it all together. Answering the question using the RAG chain ---")


# Define the LLM (gpt-5-mini in this example)
llm = ChatOpenAI(model="gpt-5-mini")

# Define the prompt template
template = """
You are a cybersecurity expert. Answer the question based only on the following context:
{context}

Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)


# Define a function to format the documents
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


# Create the RAG chain
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# Invoke the chain with the user's query
print("\n--- AI-Generated Answer ---")
answer = rag_chain.invoke(query)
print(answer)
