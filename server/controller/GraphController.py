from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from pydantic import BaseModel
import os
import uuid
import shutil
from typing import Optional

from services.StorageService import StorageService
from services.RetrievalService import RetrievalService

router = APIRouter(prefix="/api", tags=["GraphRAG"])

# Ensure the secure upload directory exists
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)

class QueryRequest(BaseModel):
    query: str

@router.post("/upload")
def upload_data(
    request: Request,
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None)
):
    """
    Accepts either an uploaded file (video, audio, pdf, image) OR a raw text string.
    Processes the data through the GraphRAG pipeline (Embedding + Graph Extraction).
    """
    if not file and not text:
        raise HTTPException(status_code=400, detail="Must provide either a file or text content.")

    if file:
        # Securely save the uploaded file to prevent naming collisions
        filename = getattr(file, "filename", "") or ""
        file_ext = filename.split('.')[-1] if '.' in filename else 'tmp'
        unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
        file_path = os.path.join(DATA_DIR, unique_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Process the physical file
        storage_service = StorageService(request.app.state.kg_db, request.app.state.vector_db, request.app.state.extractor)
        result = storage_service.process_file(file_path)
        return {"message": f"Successfully processed file {getattr(file, 'filename', 'unknown')}", "details": result}
        
    elif text:
        # Process raw text directly
        storage_service = StorageService(request.app.state.kg_db, request.app.state.vector_db, request.app.state.extractor)
        result = storage_service.process_file(text)
        return {"message": "Successfully processed raw text", "details": result}


@router.post("/query")
def query_graph(request: Request, query_req: QueryRequest):
    """
    Queries the dual GraphRAG architecture (ChromaDB + Neo4j) to formulate an answer.
    """
    if not query_req.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
        
    retrieval_service = RetrievalService(request.app.state.kg_db, request.app.state.vector_db)
    result = retrieval_service.answer_question(query_req.query)
    return {
        "query": query_req.query, 
        "answer": result["answer"], 
        "context": result["context"]
    }
