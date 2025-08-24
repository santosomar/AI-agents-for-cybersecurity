# PDFs, Images, and Chunking

To chunk a document with images, such as architecture diagrams, and make sure that results returned for any query against embeddings display the relevant image from the original document, you can follow some "best practices" and use some tools:

## 1. **Multimodal Document Analysis**

- Analyze the document to identify where images are located. This can be done using document parsing libraries like `PyPDF2` for PDFs or `Pillow` for image processing.
- **Associate Images with Text**: Use Optical Character Recognition (OCR) tools to extract text near images and associate them with the images. This helps in linking images to specific sections of the document.


## 2. **Chunking Strategy**

- **Text Chunking**: Divide the text into meaningful chunks based on sections, headings, or paragraphs. Ensure that each chunk is associated with relevant metadata, including image references.
- **Image Embeddings**: Generate embeddings for images using models like `CLIP` or `Vision Transformers`. These embeddings can be used to retrieve images based on their similarity to text queries.


## 3. **Metadata Management**

- **Create Metadata Index**: Create an index that maps each text chunk to its associated images. This metadata can include image URLs, base64 encoded images, or paths to local image files.
- **Use Embeddings for Retrieval**: Use text and image embeddings to retrieve relevant chunks and images when a query is made.


## 4. **Query Processing and Display**

- **Query Embeddings**: Generate embeddings for incoming queries using a text embedding model.
- **Similarity Search**: Perform similarity searches against the text chunk embeddings to find relevant sections.
- **Retrieve Associated Images**: Use the metadata index to retrieve images associated with the relevant text chunks.
- **Display Results**: Display both the retrieved text and associated images in the response.


## Example Implementation

Example using Python to illustrate how you might chunk a document and associate images with text chunks:

```python
import PyPDF2
from PIL import Image
import torch
from transformers import AutoModel, AutoTokenizer
from sentence_transformers import SentenceTransformer

# Load document and extract text and images
def extract_text_and_images(document_path):
    pdf = PyPDF2.PdfReader(document_path)
    text = ''
    for page in range(len(pdf.pages)):
        text += pdf.pages[page].extract_text()
    
    # Extract images using OCR or image processing libraries
    # For simplicity, assume images are stored in a separate folder
    images = []
    for file in os.listdir('images'):
        if file.endswith('.jpg'):
            images.append(os.path.join('images', file))
    
    return text, images

# Chunk text and associate with images
def chunk_text_and_associate_images(text, images):
    chunks = []
    # Simple chunking strategy: split text into paragraphs
    paragraphs = text.split('\n\n')
    
    for i, paragraph in enumerate(paragraphs):
        chunk = {
            'text': paragraph,
            'image': images[i] if i < len(images) else None
        }
        chunks.append(chunk)
    
    return chunks

# Generate embeddings for text chunks and images
def generate_embeddings(chunks):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    image_model = torch.hub.load('facebookresearch/dino:main', 'dino_vitb8')
    
    for chunk in chunks:
        chunk['text_embedding'] = model.encode(chunk['text'])
        
        if chunk['image']:
            image = Image.open(chunk['image'])
            image_embedding = image_model(image).detach().numpy()
            chunk['image_embedding'] = image_embedding
    
    return chunks

# Process query and retrieve relevant chunks and images
def process_query(query, chunks):
    query_embedding = model.encode(query)
    
    relevant_chunks = []
    for chunk in chunks:
        similarity = torch.cosine_similarity(torch.tensor(query_embedding), torch.tensor(chunk['text_embedding']))
        if similarity > 0.5:  # Threshold for relevance
            relevant_chunks.append(chunk)
    
    return relevant_chunks

# Display results
def display_results(relevant_chunks):
    for chunk in relevant_chunks:
        print(chunk['text'])
        if chunk['image']:
            print(f"Displaying image: {chunk['image']}")

# Example usage
document_path = 'example.pdf'
text, images = extract_text_and_images(document_path)
chunks = chunk_text_and_associate_images(text, images)
chunks = generate_embeddings(chunks)

query = "What is the architecture of the system?"
relevant_chunks = process_query(query, chunks)
display_results(relevant_chunks)
```

