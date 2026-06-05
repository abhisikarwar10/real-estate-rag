from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import shutil
import os

from app.core.ingestion import load_documents, chunk_documents
from app.core.retrieval import create_vectorstore, load_vectorstore
from app.core.hybrid_retrieval import hybrid_retrieve_with_transform
from app.core.generation import generate_answer

app = FastAPI(title="Real Estate RAG API", version="1.0.0")

UPLOAD_DIR = "data/raw"
CHROMA_PATH = "data/processed/chroma_db"

# Store chunks in memory after ingestion
chunks_store = {"chunks": None}

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: list[dict]

@app.get("/health")
def health_check():
    return {"status": "ok", "vectorstore_ready": os.path.exists(CHROMA_PATH)}

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a PDF and ingest it into the vectorstore"""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    
    # Save uploaded file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    # Ingest
    docs = load_documents(file_path)
    chunks = chunk_documents(docs)
    chunks_store["chunks"] = chunks
    create_vectorstore(chunks)
    
    return {
        "message": "Document ingested successfully",
        "filename": file.filename,
        "pages": len(docs),
        "chunks": len(chunks)
    }

@app.post("/query", response_model=QueryResponse)
async def query_document(request: QueryRequest):
    """Query the ingested document"""
    if not os.path.exists(CHROMA_PATH):
        raise HTTPException(status_code=400, detail="No document ingested yet. Upload a PDF first.")
    
    if chunks_store["chunks"] is None:
        # Reload chunks from disk if server restarted
        # Find the most recent PDF in upload dir
        pdfs = [f for f in os.listdir(UPLOAD_DIR) if f.endswith(".pdf")]
        if not pdfs:
            raise HTTPException(status_code=400, detail="No documents found")
        latest_pdf = os.path.join(UPLOAD_DIR, pdfs[-1])
        docs = load_documents(latest_pdf)
        chunks_store["chunks"] = chunk_documents(docs)
    
    vectorstore = load_vectorstore()
    results = hybrid_retrieve_with_transform(
        request.question,
        vectorstore,
        chunks_store["chunks"]
    )
    answer = generate_answer(request.question, results)
    
    sources = [
        {
            "page": doc.metadata.get("page", "unknown"),
            "content": doc.page_content[:200]
        }
        for doc, score in results
    ]
    
    return QueryResponse(
        question=request.question,
        answer=answer,
        sources=sources
    )