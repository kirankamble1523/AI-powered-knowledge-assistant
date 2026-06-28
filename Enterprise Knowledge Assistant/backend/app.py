import os
from pathlib import Path
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any

from backend.config import DATA_DIR, VECTOR_STORE_DIR
from backend.pdf_generator import generate_sample_pdfs
from backend.text_extractor import TextExtractor
from backend.chunker import Chunker
from backend.embeddings import EmbeddingGenerator
from backend.custom_vector_store import CustomVectorStore
from backend.llm_client import LLMClient

# Initialize FastAPI App
app = FastAPI(title="Enterprise Knowledge Assistant API", version="1.0.0")

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG Components
vector_store = CustomVectorStore()
embedding_gen = EmbeddingGenerator()
chunker = Chunker()
llm_client = LLMClient()

# Generate sample documents on startup if they don't exist
generate_sample_pdfs(DATA_DIR)

class QuestionRequest(BaseModel):
    question: str

class CitationResponse(BaseModel):
    document: str
    page: int

class AskResponse(BaseModel):
    answer: str
    sources: List[CitationResponse]
    confidence: float

def ingest_file_pipeline(file_path: Path):
    """
    Background task/helper to extract text, chunk, embed, and index a single file.
    Resilient to embedding generation failure (falls back to zero-embeddings padding).
    """
    print(f"[API Pipeline] Starting ingestion for {file_path.name}...")
    try:
        # 1. Text extraction
        pages = TextExtractor.extract_file(file_path)
        if not pages:
            print(f"[API Pipeline] No text extracted from {file_path.name}.")
            return False
            
        # 2. Chunking
        chunks = chunker.chunk_pages(pages)
        print(f"[API Pipeline] Split {file_path.name} into {len(chunks)} chunks.")
        
        # 3. Embedding generation
        texts = [c["text"] for c in chunks]
        embeddings = embedding_gen.get_embeddings(texts)
        
        # 4. Save to vector store (handles None embeddings gracefully)
        vector_store.add_chunks(chunks, embeddings)
        print(f"[API Pipeline] Successfully ingested and indexed {file_path.name}!")
        return True
    except Exception as e:
        print(f"[API Pipeline] Error during ingestion of {file_path.name}: {e}")
        return False

@app.on_event("startup")
def startup_event():
    """
    Automatically ingest files in data/ if vector store is empty.
    """
    if len(vector_store.chunks) == 0:
        print("[API Startup] Vector store is empty. Ingesting files from data/ directory...")
        for file_path in DATA_DIR.glob("*"):
            if file_path.suffix.lower() in [".pdf", ".txt", ".md"] and "AI Engineer Assignment" not in file_path.name:
                ingest_file_pipeline(file_path)

@app.post("/ask", response_model=AskResponse)
async def ask_question(request: QuestionRequest):
    """
    Endpoint to answer questions from the document collection.
    """
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
        
    if len(vector_store.chunks) == 0:
        return AskResponse(
            answer="No documents are ingested in the knowledge base yet. Please upload files to begin.",
            sources=[],
            confidence=0.0
        )
        
    try:
        # 1. Generate query embedding (can return None if API key fails)
        query_emb = embedding_gen.get_embedding(question)
        
        # 2. Retrieve top matching chunks (performs keyword search if query_emb is None)
        retrieved = vector_store.search(query_emb, k=4, query_text=question)
        
        if not retrieved:
            return AskResponse(
                answer="I'm sorry, but I couldn't find information about that in the provided documents.",
                sources=[],
                confidence=0.0
            )
            
        chunks_only = [item[0] for item in retrieved]
        
        # 3. Generate answer (falls back to local rules if LLM fails)
        result = llm_client.generate_answer(question, chunks_only)
        
        sources_list = []
        for src in result.get("sources", []):
            sources_list.append(CitationResponse(
                document=src.get("document", ""),
                page=src.get("page", 1)
            ))
            
        return AskResponse(
            answer=result.get("answer", ""),
            sources=sources_list,
            confidence=result.get("confidence", 0.0)
        )
    except Exception as e:
        print(f"[API Ask] Error processing question: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents")
async def list_documents():
    """
    Endpoint to list all indexed documents.
    """
    return vector_store.get_all_documents()

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Endpoint to upload a file and index it.
    """
    allowed_exts = [".pdf", ".txt", ".md"]
    suffix = Path(file.filename).suffix.lower()
    if suffix not in allowed_exts:
        raise HTTPException(status_code=400, detail="Only PDF, TXT, and MD files are supported.")
        
    clean_filename = Path(file.filename).name
    save_path = DATA_DIR / clean_filename
    
    try:
        with open(save_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
            
        # Ingest file immediately
        success = ingest_file_pipeline(save_path)
        if not success:
            if save_path.exists():
                save_path.unlink()
            raise HTTPException(status_code=500, detail="Ingestion failed. Text could not be extracted.")
            
        return {"status": "success", "message": f"File {clean_filename} uploaded and ingested successfully."}
    except Exception as e:
        print(f"[API Upload] Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/document/{filename}")
async def delete_document(filename: str):
    """
    Endpoint to delete a document and its chunks.
    """
    clean_filename = Path(filename).name
    file_path = DATA_DIR / clean_filename
    
    all_docs = [d["filename"] for d in vector_store.get_all_documents()]
    if clean_filename not in all_docs and not file_path.exists():
        raise HTTPException(status_code=404, detail="Document not found.")
        
    try:
        if file_path.exists():
            file_path.unlink()
            
        vector_store.delete_document(clean_filename)
        return {"status": "success", "message": f"Document {clean_filename} deleted successfully."}
    except Exception as e:
        print(f"[API Delete] Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest")
async def trigger_ingestion():
    """
    Manually trigger re-ingestion of all files in data/
    """
    try:
        vector_store.clear()
        count = 0
        for file_path in DATA_DIR.glob("*"):
            if file_path.suffix.lower() in [".pdf", ".txt", ".md"] and "AI Engineer Assignment" not in file_path.name:
                success = ingest_file_pipeline(file_path)
                if success:
                    count += 1
        return {"status": "success", "message": f"Successfully re-ingested {count} documents."}
    except Exception as e:
        print(f"[API Ingest] Error triggering ingestion: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Serve Frontend static files
frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
else:
    print("[API Warning] Frontend directory not found. API endpoints are running, but static files will not be served.")
