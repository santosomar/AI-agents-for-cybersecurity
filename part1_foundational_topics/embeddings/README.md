# Embeddings Directory

This directory contains example files and scripts for working with embeddings in cybersecurity contexts, specifically focused on Common Vulnerabilities and Exposures (CVE) data.

## Contents

### Files

- **`embeddings.py`** - Basic Python script demonstrating how to generate embeddings using OpenAI's API
- **`CVE_vectors_1000.tsv`** - Tab-separated file containing 1000 embedding vectors for CVE data
- **`CVE_metadata_1000.tsv`** - Tab-separated file containing metadata for the corresponding CVE entries

### Data Format

#### CVE_vectors_1000.tsv
This file contains 1000 rows of numerical embedding vectors. Each row represents a high-dimensional vector (embedding) that captures the semantic meaning of a CVE entry. The vectors are tab-separated floating-point numbers.

**Format**: Each line contains multiple tab-separated floating-point values representing the embedding dimensions.

#### CVE_metadata_1000.tsv
This file contains structured metadata for each CVE entry with the following columns:

| Column | Description |
|--------|-------------|
| `CVE_ID` | Common Vulnerabilities and Exposures identifier |
| `Year` | Year the vulnerability was disclosed |
| `Severity` | Severity level (Critical, High, Medium, Low) |
| `Vendor` | Vendor/organization associated with the vulnerability |
| `Product` | Product or system affected |
| `CWE` | Common Weakness Enumeration classification |
| `Impact` | Primary impact type (RCE, DoS, Data Leakage, etc.) |
| `Description` | Brief description of the vulnerability |

## Using with TensorFlow Embedding Projector

The TSV files in this directory are specifically formatted for use with [TensorFlow's Embedding Projector](https://projector.tensorflow.org/), a powerful tool for visualizing high-dimensional data. This allows you to visualize the embeddings in a 2D or 3D space, and to color-code and filter points based on CVE attributes like severity, vendor, CWE type, etc. This is a great way to explore the data and learn about vector embeddings.

### How to Use

1. **Visit the Embedding Projector**: Go to [https://projector.tensorflow.org/](https://projector.tensorflow.org/)

2. **Load the Vector Data**:
   - Click "Load data from your computer"
   - In Step 1, upload `CVE_vectors_1000.tsv` as your vectors file
   - This file contains the high-dimensional embeddings for each CVE

3. **Load the Metadata** (Optional but Recommended):
   - In Step 2, upload `CVE_metadata_1000.tsv` as your metadata file
   - This will allow you to color-code and filter points based on CVE attributes like severity, vendor, CWE type, etc.

4. **Explore the Visualization**:
   - Use different projection methods (t-SNE, UMAP, PCA) to visualize the data
   - Color points by different metadata fields (Severity, Vendor, CWE, Impact)
   - Search for specific CVEs or filter by attributes
   - Identify clusters of similar vulnerabilities

### Visualization Benefits

Using the Embedding Projector with this CVE data allows you to:

- **Identify Patterns**: Discover clusters of similar vulnerabilities
- **Explore Relationships**: See how different CVEs relate to each other semantically
- **Filter by Attributes**: Focus on specific vendors, severity levels, or vulnerability types
- **Interactive Analysis**: Click on points to see detailed metadata and find nearest neighbors

### Example Use Cases

1. **Threat Intelligence**: Identify patterns in vulnerability types across different vendors
2. **Risk Assessment**: Visualize the distribution of severity levels and impact types
3. **Research**: Explore relationships between different CWE categories
4. **Training**: Use as educational material to understand vulnerability landscapes

## Getting Started with Embeddings

The `embeddings.py` script demonstrates the basic process of generating embeddings using OpenAI's API. This is useful for:

- Understanding how text is converted to numerical vectors
- Creating your own embeddings for custom security data
- Experimenting with different embedding models

### Prerequisites

To run the embedding script, you'll need:

```bash
pip install openai
```

And set your OpenAI API key as an environment variable:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

## Educational Value

This directory serves as a practical introduction to:

- **Vector Embeddings**: Understanding how text becomes numerical representations
- **High-Dimensional Data Visualization**: Using tools like t-SNE and UMAP
- **Cybersecurity Data Analysis**: Applying ML techniques to vulnerability data
- **Interactive Data Exploration**: Leveraging web-based visualization tools

## Next Steps

After exploring this data, consider:

1. Creating embeddings for your own security datasets
2. Experimenting with different embedding models
3. Building RAG (Retrieval-Augmented Generation) systems using these embeddings
4. Developing custom visualization tools for your specific use cases

---

*This is part of the AI Agents for Cybersecurity educational series by Omar Santos (@santosomar)*
