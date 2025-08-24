# Embeddings Directory

This directory contains example files and scripts for working with embeddings in cybersecurity contexts, specifically focused on Common Vulnerabilities and Exposures (CVE) data.

## Contents

### Files

- **`embeddings.py`** - Basic Python script demonstrating how to generate embeddings using OpenAI's API
- **`clustering.py`** - Advanced clustering analysis script with comprehensive visualizations
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

## Clustering Analysis with Python Visualizations

The `clustering.py` script provides a comprehensive clustering analysis of the CVE embeddings with built-in visualizations. This script performs K-means clustering and creates detailed visual analyses without requiring external tools.

### Features

- **K-means Clustering**: Groups similar CVEs into clusters based on their embedding vectors
- **Dimensionality Reduction**: Uses PCA and t-SNE to visualize high-dimensional data in 2D
- **Comprehensive Visualizations**: Creates multiple charts and plots for analysis
- **Statistical Analysis**: Provides detailed cluster characteristics and summaries
- **High-Quality Exports**: Saves publication-ready PNG files at 300 DPI

### Generated Visualizations

The script creates two comprehensive visualization files:

1. **`cve_clustering_analysis.png`** - Main analysis dashboard containing:
   - PCA and t-SNE cluster visualizations
   - Cluster size distribution
   - Severity distribution by cluster
   - Top 10 CWE types
   - Impact types distribution

2. **`cve_detailed_analysis.png`** - Detailed metadata analysis containing:
   - t-SNE plots colored by severity levels
   - t-SNE plots colored by top vendors
   - Cluster centers with labels
   - CVE distribution timeline by year

### Prerequisites

To run the clustering script, install the required packages:

```bash
pip install pandas numpy scikit-learn matplotlib seaborn
```

### Usage

```bash
python3 clustering.py
```

The script will:
1. Load the CVE vectors and metadata
2. Perform K-means clustering (default: 10 clusters)
3. Reduce dimensionality using PCA and t-SNE
4. Generate comprehensive visualizations
5. Display plots on screen and save as PNG files
6. Print detailed cluster analysis to console

## Using with TensorFlow Embedding Projector (Alternative)

The TSV files in this directory are also specifically formatted for use with [TensorFlow's Embedding Projector](https://projector.tensorflow.org/), a powerful web-based tool for visualizing high-dimensional data. This provides an interactive alternative to the Python clustering script.

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

### Basic Embeddings (`embeddings.py`)

The `embeddings.py` script demonstrates the basic process of generating embeddings using OpenAI's API. This is useful for:

- Understanding how text is converted to numerical vectors
- Creating your own embeddings for custom security data
- Experimenting with different embedding models

#### Prerequisites

To run the embedding script, you'll need:

```bash
pip install openai
```

And set your OpenAI API key as an environment variable:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

### Advanced Analysis (`clustering.py`)

For comprehensive clustering analysis and visualization of the provided CVE dataset, use the `clustering.py` script. This provides immediate insights without requiring API keys or external services.

## Educational Value

This directory serves as a practical introduction to:

- **Vector Embeddings**: Understanding how text becomes numerical representations
- **Machine Learning Clustering**: Applying K-means clustering to cybersecurity data
- **High-Dimensional Data Visualization**: Using PCA, t-SNE, and statistical plots
- **Cybersecurity Data Analysis**: Applying ML techniques to vulnerability data
- **Python Data Science**: Using pandas, scikit-learn, matplotlib, and seaborn
- **Interactive Data Exploration**: Both programmatic and web-based visualization tools

## Next Steps

After exploring this data, consider:

1. **Modify Clustering Parameters**: Experiment with different numbers of clusters or algorithms
2. **Create Custom Embeddings**: Generate embeddings for your own security datasets using `embeddings.py`
3. **Advanced Analysis**: Add more sophisticated clustering algorithms (DBSCAN, hierarchical clustering)
4. **Build RAG Systems**: Use these embeddings for Retrieval-Augmented Generation applications
5. **Develop Custom Tools**: Create specialized visualization tools for your specific use cases
6. **Time Series Analysis**: Analyze how vulnerability patterns change over time

---

*This is part of the AI Agents for Cybersecurity educational series by Omar Santos (@santosomar)*
