'''
This script performs clustering analysis on CVE embeddings using K-means clustering.
It reduces dimensionality with PCA and t-SNE for visualization, analyzes cluster 
characteristics, and generates comprehensive visualizations and summaries of the results.
'''

# Import required libraries
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set style for better-looking plots
plt.style.use('default')
sns.set_palette("husl")

# Get the directory where this script is located (optional)
script_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Script directory: {script_dir}")

# Load the CVE data files
print("Loading CVE data...")

# Load embeddings (vectors) - tab-separated values, no header
vectors_file = os.path.join(script_dir, 'CVE_vectors_1000.tsv')
metadata_file = os.path.join(script_dir, 'CVE_metadata_1000.tsv')

print(f"Loading vectors from: {vectors_file}")
print(f"Loading metadata from: {metadata_file}")

embeddings = np.loadtxt(vectors_file, delimiter='\t')
print(f"Loaded embeddings shape: {embeddings.shape}")

# Load metadata - tab-separated values with header
metadata = pd.read_csv(metadata_file, delimiter='\t')
print(f"Loaded metadata shape: {metadata.shape}")
print(f"Metadata columns: {list(metadata.columns)}")

# Perform clustering on embeddings
print("\nPerforming K-means clustering...")
n_clusters = 10
kmeans = KMeans(n_clusters=n_clusters, random_state=42)
cluster_labels = kmeans.fit_predict(embeddings)

# Analyze cluster characteristics
print(f"\nCluster Analysis (Total CVEs: {len(embeddings)}):")
print("=" * 60)

for cluster_id in range(n_clusters):
    cluster_mask = cluster_labels == cluster_id
    cluster_metadata = metadata[cluster_mask]
    
    print(f"Cluster {cluster_id}:")
    print(f"  Size: {cluster_mask.sum()}")
    
    # Top CWEs in this cluster
    if 'CWE' in cluster_metadata.columns:
        top_cwes = cluster_metadata['CWE'].value_counts().head(3)
        print(f"  Top CWEs: {top_cwes.to_dict()}")
    
    # Severity distribution
    if 'Severity' in cluster_metadata.columns:
        severity_dist = cluster_metadata['Severity'].value_counts()
        print(f"  Severity distribution: {severity_dist.to_dict()}")
    
    # Top vendors
    if 'Vendor' in cluster_metadata.columns:
        top_vendors = cluster_metadata['Vendor'].value_counts().head(2)
        print(f"  Top vendors: {top_vendors.to_dict()}")
    
    # Top impacts
    if 'Impact' in cluster_metadata.columns:
        top_impacts = cluster_metadata['Impact'].value_counts().head(2)
        print(f"  Top impacts: {top_impacts.to_dict()}")
    
    print()

print("Clustering analysis complete!")

# Create visualizations
print("\nCreating visualizations...")

# 1. Reduce dimensionality for visualization
print("Reducing dimensions with PCA...")
pca = PCA(n_components=2, random_state=42)
embeddings_2d_pca = pca.fit_transform(embeddings)

print("Reducing dimensions with t-SNE...")
tsne = TSNE(n_components=2, random_state=42, perplexity=30)
embeddings_2d_tsne = tsne.fit_transform(embeddings)

# Create a figure with multiple subplots
fig = plt.figure(figsize=(20, 15))

# 1. PCA Cluster Visualization
ax1 = plt.subplot(2, 3, 1)
scatter = plt.scatter(embeddings_2d_pca[:, 0], embeddings_2d_pca[:, 1], 
                     c=cluster_labels, cmap='tab10', alpha=0.7, s=50)
plt.title('CVE Clusters - PCA Visualization', fontsize=14, fontweight='bold')
plt.xlabel('First Principal Component')
plt.ylabel('Second Principal Component')
plt.colorbar(scatter, label='Cluster ID')
plt.grid(True, alpha=0.3)

# 2. t-SNE Cluster Visualization
ax2 = plt.subplot(2, 3, 2)
scatter2 = plt.scatter(embeddings_2d_tsne[:, 0], embeddings_2d_tsne[:, 1], 
                      c=cluster_labels, cmap='tab10', alpha=0.7, s=50)
plt.title('CVE Clusters - t-SNE Visualization', fontsize=14, fontweight='bold')
plt.xlabel('t-SNE Component 1')
plt.ylabel('t-SNE Component 2')
plt.colorbar(scatter2, label='Cluster ID')
plt.grid(True, alpha=0.3)

# 3. Cluster Size Distribution
ax3 = plt.subplot(2, 3, 3)
cluster_sizes = pd.Series(cluster_labels).value_counts().sort_index()
bars = plt.bar(cluster_sizes.index, cluster_sizes.values, color='skyblue', alpha=0.8)
plt.title('Cluster Size Distribution', fontsize=14, fontweight='bold')
plt.xlabel('Cluster ID')
plt.ylabel('Number of CVEs')
plt.grid(True, alpha=0.3, axis='y')
# Add value labels on bars
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 1,
             f'{int(height)}', ha='center', va='bottom')

# 4. Severity Distribution by Cluster
ax4 = plt.subplot(2, 3, 4)
if 'Severity' in metadata.columns:
    severity_cluster = pd.crosstab(metadata['Severity'], cluster_labels)
    severity_cluster.plot(kind='bar', stacked=True, ax=ax4, colormap='viridis')
    plt.title('Severity Distribution by Cluster', fontsize=14, fontweight='bold')
    plt.xlabel('Severity Level')
    plt.ylabel('Count')
    plt.legend(title='Cluster ID', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xticks(rotation=45)

# 5. Top CWEs Distribution
ax5 = plt.subplot(2, 3, 5)
if 'CWE' in metadata.columns:
    top_cwes = metadata['CWE'].value_counts().head(10)
    bars = plt.barh(range(len(top_cwes)), top_cwes.values, color='lightcoral', alpha=0.8)
    plt.yticks(range(len(top_cwes)), top_cwes.index)
    plt.title('Top 10 CWE Types', fontsize=14, fontweight='bold')
    plt.xlabel('Count')
    plt.grid(True, alpha=0.3, axis='x')
    # Add value labels
    for i, bar in enumerate(bars):
        width = bar.get_width()
        plt.text(width + 1, bar.get_y() + bar.get_height()/2.,
                 f'{int(width)}', ha='left', va='center')

# 6. Impact Types Distribution
ax6 = plt.subplot(2, 3, 6)
if 'Impact' in metadata.columns:
    impact_counts = metadata['Impact'].value_counts()
    plt.pie(impact_counts.values, labels=impact_counts.index, autopct='%1.1f%%', 
            startangle=90, colors=sns.color_palette("husl", len(impact_counts)))
    plt.title('Impact Types Distribution', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('cve_clustering_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

print("\nVisualization complete!")
print("Saved comprehensive analysis as 'cve_clustering_analysis.png'")

# Additional detailed cluster analysis with t-SNE colored by metadata
if 'Severity' in metadata.columns:
    fig2, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Color by Severity
    severity_colors = {'Critical': 'red', 'High': 'orange', 'Medium': 'yellow', 'Low': 'green'}
    colors = [severity_colors.get(sev, 'gray') for sev in metadata['Severity']]
    ax1.scatter(embeddings_2d_tsne[:, 0], embeddings_2d_tsne[:, 1], c=colors, alpha=0.7, s=50)
    ax1.set_title('CVE Embeddings Colored by Severity', fontsize=14, fontweight='bold')
    ax1.set_xlabel('t-SNE Component 1')
    ax1.set_ylabel('t-SNE Component 2')
    ax1.grid(True, alpha=0.3)
    
    # Create custom legend for severity
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=color, label=severity) 
                      for severity, color in severity_colors.items()]
    ax1.legend(handles=legend_elements, title='Severity')
    
    # Color by top vendors
    if 'Vendor' in metadata.columns:
        top_vendors = metadata['Vendor'].value_counts().head(5).index
        vendor_colors = dict(zip(top_vendors, sns.color_palette("Set1", len(top_vendors))))
        colors = [vendor_colors.get(vendor, 'lightgray') for vendor in metadata['Vendor']]
        ax2.scatter(embeddings_2d_tsne[:, 0], embeddings_2d_tsne[:, 1], c=colors, alpha=0.7, s=50)
        ax2.set_title('CVE Embeddings Colored by Top Vendors', fontsize=14, fontweight='bold')
        ax2.set_xlabel('t-SNE Component 1')
        ax2.set_ylabel('t-SNE Component 2')
        ax2.grid(True, alpha=0.3)
        
        # Vendor legend
        legend_elements = [Patch(facecolor=color, label=vendor) 
                          for vendor, color in vendor_colors.items()]
        ax2.legend(handles=legend_elements, title='Vendor', bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Cluster centers on t-SNE
    ax3.scatter(embeddings_2d_tsne[:, 0], embeddings_2d_tsne[:, 1], 
               c=cluster_labels, cmap='tab10', alpha=0.5, s=30)
    
    # Add cluster centers
    cluster_centers_2d = []
    for i in range(n_clusters):
        cluster_points = embeddings_2d_tsne[cluster_labels == i]
        center = cluster_points.mean(axis=0)
        cluster_centers_2d.append(center)
        ax3.scatter(center[0], center[1], c='red', s=200, marker='x', linewidths=3)
        ax3.annotate(f'C{i}', (center[0], center[1]), xytext=(5, 5), 
                    textcoords='offset points', fontweight='bold')
    
    ax3.set_title('Cluster Centers on t-SNE', fontsize=14, fontweight='bold')
    ax3.set_xlabel('t-SNE Component 1')
    ax3.set_ylabel('t-SNE Component 2')
    ax3.grid(True, alpha=0.3)
    
    # Year distribution
    if 'Year' in metadata.columns:
        year_dist = metadata['Year'].value_counts().sort_index()
        ax4.plot(year_dist.index, year_dist.values, marker='o', linewidth=2, markersize=6)
        ax4.set_title('CVE Distribution by Year', fontsize=14, fontweight='bold')
        ax4.set_xlabel('Year')
        ax4.set_ylabel('Number of CVEs')
        ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('cve_detailed_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("Saved detailed analysis as 'cve_detailed_analysis.png'")

print("\n" + "="*60)
print("CLUSTERING ANALYSIS SUMMARY")
print("="*60)
print(f"Total CVEs analyzed: {len(embeddings)}")
print(f"Embedding dimensions: {embeddings.shape[1]}")
print(f"Number of clusters: {n_clusters}")
print(f"PCA explained variance ratio: {pca.explained_variance_ratio_}")
print(f"Total variance explained by 2D PCA: {pca.explained_variance_ratio_.sum():.3f}")
print("\nVisualization files created:")
print("- cve_clustering_analysis.png (comprehensive overview)")
print("- cve_detailed_analysis.png (detailed metadata analysis)")
print("\nAll visualizations displayed above!")