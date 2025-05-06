from chromadb.config import Settings
import chromadb
from langchain_huggingface  import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from docx import Document
import fitz
import uuid
import os
import hashlib

def read_document_content(file):
    """Reads text from supported file types and returns content + raw bytes."""
    filename = file.filename.lower()
    ext = os.path.splitext(filename)[1]
    raw_bytes = file.read()

    if ext == '.txt':
        return raw_bytes.decode('utf-8'), raw_bytes

    elif ext == '.docx':
        document = Document(file)
        return '\n'.join([p.text for p in document.paragraphs]), raw_bytes

    elif ext == '.pdf':
        with fitz.open(stream=raw_bytes, filetype='pdf') as pdf_file:
            text = ''.join([page.get_text() for page in pdf_file])
        return text, raw_bytes

    else:
        raise ValueError("Unsupported file type. Only .txt, .docx, and .pdf are supported.")
    

def compute_file_hash(file_bytes):
    """Generate SHA256 hash from file content (bytes)."""
    return hashlib.sha256(file_bytes).hexdigest()

def get_chroma_client():
    """Initialize and return a ChromaDB client."""
    return chromadb.HttpClient(host="localhost", port=8000)


def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 100):
    """Split text into overlapping chunks."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split_text(text)


def embed_chunks(client, chunks: list, file_hash: str, asset_id: str):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    collection = client.get_or_create_collection(name='documents')

    ids = []
    for chunk in chunks:
        emb = embeddings.embed_query(chunk)
        uid = str(uuid.uuid4())
        collection.add(
            ids=[uid],
            embeddings=[emb],
            metadatas=[{'text': chunk, 'file_hash': file_hash, 'asset_id': asset_id}]
        )
        ids.append(uid)

    return ids
