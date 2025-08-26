# RAG Examples for Cybersecurity

This directory provides a collection of Python scripts demonstrating various aspects of Retrieval-Augmented Generation (RAG) tailored for cybersecurity use cases. These examples cover fundamental RAG concepts such as document loading, text splitting, embedding generation, vector store creation, and querying, primarily using LangChain and OpenAI.

## Basic Examples Explained:

```mermaid
graph TD
    A[Input Ingestion<br>User Query Received]
    B1[Retriever<br>Fetch Relevant Documents]
    B2[RunnablePassthrough<br>Preserve Original Question]
    C[Context Packaging<br>Normalize and Structure Documents]
    D[Prompt Assembly<br>ChatPromptTemplate Combines Context and Question]
    E[LLM Response Generation<br>ChatOpenAI Produces Answer]
    F[Output Transformation<br>StrOutputParser Formats Response]

    A --> B1
    A --> B2
    B1 --> C
    B2 --> D
    C --> D
    D --> E
    E --> F
```

## Directory Structure

```
part4_rag_examples/
├── README.md                           # This documentation file
├── basic_rag_part1.py                  # Creates a Chroma vector store from a text file.
├── basic_rag_part2.py                  # Queries the vector store created by basic_rag_part1.py.
├── data/                               # Contains raw data files for ingestion.
│   ├── ssrf.txt                        # Text file about Server-Side Request Forgery.
│   ├── tesla.json                      # JSON file with Tesla-related data (e.g., for embedding/splitting demos).
│   └── tesla_hostnames.txt             # Text file listing Tesla-related hostnames.
├── db/                                 # Stores persisted Chroma vector databases.
│   ├── chroma_db/                      # Vector store for basic_rag_part1.py (ssrf.txt).
│   ├── chroma_db_char/                 # Vector store for text_splitting_deep_dive.py (character-based).
│   ├── chroma_db_custom/               # Vector store for text_splitting_deep_dive.py (custom splitting).
│   ├── chroma_db_huggingface/          # Vector store for embedding_deep_dive.py (Hugging Face embeddings).
│   ├── chroma_db_openai/               # Vector store for embedding_deep_dive.py (OpenAI embeddings).
│   ├── chroma_db_rec_char/             # Vector store for text_splitting_deep_dive.py (recursive character-based).
│   ├── chroma_db_secretcorp/           # Vector store for web_scrape_basic.py (secretcorp.org data).
│   ├── chroma_db_sent/                 # Vector store for text_splitting_deep_dive.py (sentence-based).
│   ├── chroma_db_token/                # Vector store for text_splitting_deep_dive.py (token-based).
│   └── chroma_db_with_metadata/        # Vector store for rag_basics_metadata_part1.py (multiple .txt files with metadata).
├── embedding_deep_dive.py              # Demonstrates using different embedding models (OpenAI, Hugging Face).
├── one_off_question.py                 # Answers a single question using a RAG approach with a pre-existing vector store.
├── rag_basics_metadata_part1.py        # Creates a vector store from multiple text files, adding source metadata.
├── rag_basics_metadata_part2.py        # Queries the metadata-rich vector store created by rag_basics_metadata_part1.py.
├── text_splitting_deep_dive.py         # Explores various text splitting techniques.
├── utils/                              # Utility scripts.
│   └── embedding_cost_calculator.py    # Calculates the estimated cost of embedding a document using OpenAI.
└── web_scrape_basic.py                 # Scrapes a web page, creates embeddings, and stores them in a vector store.
```

## File Descriptions

### Core Scripts

-   **`basic_rag_part1.py`**
    -   **Purpose**: Demonstrates the creation of a Chroma vector store from a single text file (`data/ssrf.txt`).
    -   **Functionality**: Loads text, splits it into chunks using `CharacterTextSplitter`, generates embeddings with `OpenAIEmbeddings` (model `text-embedding-3-small`), and persists the vector store to `db/chroma_db`.
    -   Checks if the store exists before initialization.

-   **`basic_rag_part2.py`**
    -   **Purpose**: Shows how to query an existing Chroma vector store (created by `basic_rag_part1.py`).
    -   **Functionality**: Loads the vector store from `db/chroma_db`, uses `OpenAIEmbeddings` for the query, and retrieves relevant documents based on a similarity score threshold.

-   **`embedding_deep_dive.py`**
    -   **Purpose**: Compares different embedding models (OpenAI's `text-embedding-ada-002` and Hugging Face's `sentence-transformers/all-mpnet-base-v2`).
    -   **Functionality**: Loads data from `data/tesla.json`, creates separate Chroma vector stores (`db/chroma_db_openai` and `db/chroma_db_huggingface`) for each embedding type, and queries both to compare results.

-   **`one_off_question.py`**
    -   **Purpose**: Illustrates answering a single user question by retrieving relevant documents from a pre-existing vector store (`db/chroma_db_with_metadata`) and feeding them to an LLM (`gpt-5-mini`).
    -   **Functionality**: Retrieves documents, combines them with the user query into a prompt, and uses `ChatOpenAI` to generate an answer. Responds "I'm not sure" if the answer isn't in the documents.

-   **`rag_basics_metadata_part1.py`**
    -   **Purpose**: Focuses on creating a vector store from multiple text files within the `data/` directory, attaching metadata (source filename) to each document chunk.
    -   **Functionality**: Loads all `.txt` files, adds `source` metadata, splits documents, creates embeddings (`text-embedding-3-small`), and persists to `db/chroma_db_with_metadata`.

-   **`rag_basics_metadata_part2.py`**
    -   **Purpose**: Demonstrates querying the metadata-enriched vector store created by `rag_basics_metadata_part1.py`.
    -   **Functionality**: Loads `db/chroma_db_with_metadata` and displays retrieved documents along with their source metadata.

-   **`text_splitting_deep_dive.py`**
    -   **Purpose**: Explores and compares various text splitting strategies available in LangChain.
    -   **Functionality**: Uses `data/tesla.json` and applies `CharacterTextSplitter`, `SentenceTransformersTokenTextSplitter`, `TokenTextSplitter`, `RecursiveCharacterTextSplitter`, and a custom splitter. Each strategy creates its own vector store (e.g., `db/chroma_db_char`, `db/chroma_db_sent`, etc.) and is then queried.

-   **`web_scrape_basic.py`**
    -   **Purpose**: Shows how to scrape content from a web page, process it, and store it in a vector database for RAG.
    -   **Functionality**: Uses `WebBaseLoader` to fetch content from `https://secretcorp.org`, splits it, creates embeddings (`text-embedding-3-small`), and persists to `db/chroma_db_secretcorp`. It then queries this store.

### Utility Scripts

-   **`utils/embedding_cost_calculator.py`**
    -   **Purpose**: Provides an estimation of the cost to embed a given text file using OpenAI's API.
    -   **Functionality**: Reads `data/ssrf.txt`, tokenizes it using `tiktoken` (with `cl100k_base` encoding), and calculates the cost based on a predefined rate (e.g., $0.02 per million tokens for `text-embedding-3-small`).

### Data Directory (`data/`)

This directory holds the source documents used by the example scripts:
-   `ssrf.txt`: Contains textual information about Server-Side Request Forgery vulnerabilities, used by `basic_rag_part1.py` and `embedding_cost_calculator.py`.
-   `tesla.json`: A JSON file with data related to Tesla, used as a larger document for `embedding_deep_dive.py` and `text_splitting_deep_dive.py` to demonstrate embeddings and splitting on more extensive content.
-   `tesla_hostnames.txt`: A list of Tesla-related hostnames, likely used as one of the `.txt` files for `rag_basics_metadata_part1.py`.

### Database Directory (`db/`)

This directory is where Chroma vector stores are persisted by the scripts. Each subdirectory typically corresponds to a vector store created by a specific script or with a particular configuration:
-   `chroma_db/`: Created by `basic_rag_part1.py` from `ssrf.txt`.
-   `chroma_db_char/`, `chroma_db_custom/`, `chroma_db_rec_char/`, `chroma_db_sent/`, `chroma_db_token/`: Created by `text_splitting_deep_dive.py`, each using a different text splitting method on `tesla.json`.
-   `chroma_db_huggingface/`, `chroma_db_openai/`: Created by `embedding_deep_dive.py`, using Hugging Face and OpenAI embeddings respectively on `tesla.json`.
-   `chroma_db_secretcorp/`: Created by `web_scrape_basic.py` from the content of `secretcorp.org`.
-   `chroma_db_with_metadata/`: Created by `rag_basics_metadata_part1.py` from various `.txt` files in the `data/` directory, including source metadata.

## Prerequisites

-   Python 3.x
-   An OpenAI API key, set as an environment variable `OPENAI_API_KEY`.
-   Required Python packages. You can install them using pip:
    ```bash
    pip install langchain langchain-openai langchain-community langchain-chroma chromadb tiktoken sentence-transformers dotenv
    ```
    (Consider creating a `requirements.txt` file for easier dependency management.)

## Getting Started

1.  **Clone the repository** (if you haven't already).
2.  **Install dependencies**:
    ```bash
    pip install langchain langchain-openai langchain-community langchain-chroma chromadb tiktoken sentence-transformers dotenv
    ```
3.  **Set up your OpenAI API Key**: Export it as an environment variable.
    ```bash
    export OPENAI_API_KEY='your-actual-openai-api-key'
    ```
    Alternatively, create a `.env` file in the `part4_rag_examples` directory with the line `OPENAI_API_KEY='your-actual-openai-api-key'` (scripts using `load_dotenv()` will pick it up).

    **SECURITY NOTE**: Never commit your API keys to version control. Also, instead of using environment variables to store sensitive information, you can use a secrets management service like CyberArk Conjur, HashiCorp Vault or AWS Secrets Manager.

4.  **Run the example scripts**: Start with the basic examples:
    -   To create an initial vector store:
        ```bash
        python basic_rag_part1.py
        ```
    -   To query the store created above:
        ```bash
        python basic_rag_part2.py
        ```
    Explore other scripts to understand different RAG aspects.

## Key Concepts Demonstrated

-   **Document Loading**: Using `TextLoader`, `WebBaseLoader` to ingest data from files and web pages.
-   **Text Splitting**: Employing various strategies like `CharacterTextSplitter`, `RecursiveCharacterTextSplitter`, `SentenceTransformersTokenTextSplitter`, `TokenTextSplitter`, and custom splitters to break down documents into manageable chunks.
-   **Embeddings**: Generating numerical representations of text using `OpenAIEmbeddings` (e.g., `text-embedding-3-small`, `text-embedding-ada-002`) and Hugging Face models (`sentence-transformers/all-mpnet-base-v2`).
-   **Vector Stores**: Using `Chroma` as a vector database to store embeddings and perform similarity searches.
-   **Persistence**: Saving and loading vector stores to/from disk.
-   **Retrieval**: Querying vector stores to find relevant document chunks based on semantic similarity to a user's question, using techniques like similarity score thresholds.
-   **Metadata**: Attaching and utilizing metadata (like document source) during RAG.
-   **Question Answering**: Combining retrieved documents with a query to generate answers using an LLM (`ChatOpenAI`).
-   **Cost Estimation**: Using `tiktoken` to estimate token count and potential costs for OpenAI embeddings.

## Notes

-   Most scripts are designed to be run independently, but some (like `_part2.py` scripts) depend on vector stores created by their `_part1.py` counterparts.
-   The `db/` directory will be populated as you run the scripts that create persistent vector stores.
-   Ensure your OpenAI API key has sufficient quota/billing set up if you plan to run these scripts multiple times, especially `embedding_deep_dive.py` or `text_splitting_deep_dive.py` which process larger data or create multiple stores.

   ```bash
   python text_splitting_deep_dive.py
   ```

## Query Example

The script includes a sample query:
```python
query = "What hosts are in Amazon?"
```

This query is executed against all five vector stores, allowing you to compare how different splitting methods affect retrieval results.

## Configuration

- Embedding model: text-embedding-3-small
- Similarity score threshold: 0.1
- Results per query: 1 document
- Search type: similarity_score_threshold

---

# Web Scraping RAG Example

This script demonstrates how to create a RAG (Retrieval-Augmented Generation) system that scrapes web content, processes it, and stores it in a vector database for semantic search capabilities.

## Overview

The script performs the following operations:
1. Scrapes content from specified web pages using WebBaseLoader
2. Splits the content into manageable chunks
3. Creates embeddings using OpenAI's embedding model
4. Stores the embeddings in a Chroma vector database
5. Performs semantic search queries on the stored content

## Prerequisites

- Python 3.x
- Required packages:
  ```bash
  pip install langchain langchain-openai chromadb python-dotenv
  ```
- OpenAI API key set in your `.env` file

## Project Structure

```
part4_rag_examples/
├── web_scrape_basic.py
└── db/
    └── chroma_db_secretcorp/  # Directory where the vector store is persisted
```

## Features

- **Web Scraping**: Automatically extracts content from specified URLs
- **Content Processing**: 
  - Splits content into 1000-character chunks
  - No overlap between chunks for efficiency
- **Vector Storage**:
  - Persistent Chroma database
  - Automatic initialization check
  - Source URL metadata preservation
- **Semantic Search**:
  - Similarity-based retrieval
  - Returns top 3 most relevant results
  - Includes source metadata in results

## Usage

1. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

2. Modify the `urls` list to include your target websites:
   ```python
   urls = ["https://secretcorp.org"]
   ```

3. Run the script:
   ```bash
   python web_scrape_basic.py
   ```

## Configuration

- Embedding model: text-embedding-3-small
- Chunk size: 1000 characters
- Search results: Top 3 most relevant documents
- Search type: similarity

## Example Query

The script includes a sample query:
```python
query = "What is secretcorp all about?"
```

## Output

The script provides:
- Number of document chunks created
- Sample of processed content
- Vector store creation status
- Relevant documents for the query with their sources

## Author

Instructor: Omar Santos (@santosomar)
