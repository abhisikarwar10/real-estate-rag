from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

def load_documents(file_path: str):
    """Load documents and return raw documents"""
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    print(f"Loaded {len(documents)} documents from {os.path.basename(file_path)}")
    return documents

def chunk_documents(documents):
    """split documents into smaller chunks for embeddings"""
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200,separators=["\n\n", "\n", ".", " ", ""])
    chunks = splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks")
    return chunks

