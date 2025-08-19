# This script puts it all together by showing how to use a RAG chain with a 
# vector store to answer questions based on a knowledge base.

# Instructor: Omar Santos @santosomar

# Import necessary libraries
import os
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# --- 1. Setup the Environment ---
# Define the persistent directory for the Chroma vector store
current_dir = os.path.dirname(os.path.abspath(__file__))
persistent_directory = os.path.join(current_dir, "db", "chroma_db_security")

# --- 2. Load the Vector Store ---
# Initialize the embedding model
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Load the existing vector store
db = Chroma(persist_directory=persistent_directory, embedding_function=embeddings)

# --- 3. Create the Retriever ---
# A retriever is a component that fetches relevant documents from the vector store based on a query.
retriever = db.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"k": 5, "score_threshold": 0.5},
)

# --- 4. Define the RAG Chain ---
# Define the prompt template for the RAG chain
prompt_template = """
You are a cybersecurity expert. Answer the question based only on the following context:

{context}

Question: {question}
"""

prompt = ChatPromptTemplate.from_template(prompt_template)

# Initialize the language model
llm = ChatOpenAI(model="gpt-5-mini")

# Helper function to format the retrieved documents
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# Create the RAG chain using LangChain Expression Language (LCEL)
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# --- 5. Invoke the Chain and Get the Answer ---
if __name__ == "__main__":
    # Define the user's question
    query = "What is SSRF? Provide an example of an SSRF attack."

    # Invoke the RAG chain with the query
    response = rag_chain.invoke(query)

    # Print the response
    print("\n--- AI-Generated Answer ---")
    print(response)
