"""
Knowledge Base API — Upload documents, manage collections, semantic search

POST /kb/collections           → Create knowledge base
GET  /kb/collections           → List knowledge bases
DELETE /kb/collections/{id}    → Delete knowledge base
POST /kb/collections/{id}/documents → Upload document (PDF/Word/Excel)
GET  /kb/collections/{id}/documents → List documents
DELETE /kb/documents/{id}      → Delete document
POST /kb/search                → Semantic search across knowledge base
"""

import os
import shutil
import structlog
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from typing import Optional

from app.services.auth import get_current_user
from app.services.kb_service import KnowledgeBaseService
from app.core.config import get_settings

router = APIRouter()
logger = structlog.get_logger()


def _get_kb_service() -> KnowledgeBaseService:
    return KnowledgeBaseService()


# ========== Collections ==========

@router.get("/collections")
async def list_collections(user=Depends(get_current_user)):
    """List all knowledge bases."""
    svc = _get_kb_service()
    collections = await svc.list_collections(owner_id=int(user.id))
    return {"collections": collections}


@router.post("/collections")
async def create_collection(
    name: str = Form(...),
    description: str = Form(""),
    user=Depends(get_current_user),
):
    """Create a new knowledge base."""
    svc = _get_kb_service()
    collection = await svc.create_collection(name, description, owner_id=int(user.id))
    return collection


@router.delete("/collections/{collection_id}")
async def delete_collection(collection_id: int, user=Depends(get_current_user)):
    """Delete a knowledge base and all its documents."""
    svc = _get_kb_service()
    deleted = await svc.delete_collection(collection_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Collection not found")
    return {"status": "deleted"}


# ========== Documents ==========

@router.get("/collections/{collection_id}/documents")
async def list_documents(collection_id: int, user=Depends(get_current_user)):
    """List documents in a knowledge base."""
    svc = _get_kb_service()
    documents = await svc.list_documents(collection_id)
    return {"documents": documents}


@router.post("/collections/{collection_id}/documents")
async def upload_document(
    collection_id: int,
    file: UploadFile = File(...),
    user=Depends(get_current_user),
):
    """
    Upload a document to a knowledge base.
    Supports: PDF, Word (.docx), Excel (.xlsx/.csv), Text (.txt/.md)
    """
    settings = get_settings()

    # Validate file type
    ext = os.path.splitext(file.filename)[1].lower()
    allowed = {".pdf", ".docx", ".doc", ".xlsx", ".xls", ".csv", ".txt", ".md"}
    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}. Allowed: {allowed}")

    # Save uploaded file
    upload_dir = os.path.join(settings.upload_dir, str(collection_id))
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    logger.info("File uploaded", filename=file.filename, size=file.size, collection=collection_id)

    # Process document (parse → chunk → embed → store)
    svc = _get_kb_service()
    result = await svc.upload_document(collection_id, file_path, file.filename)

    if result["status"] == "failed":
        raise HTTPException(status_code=500, detail=f"Processing failed: {result.get('error_msg')}")

    return result


@router.delete("/documents/{document_id}")
async def delete_document(document_id: int, user=Depends(get_current_user)):
    """Delete a document and its chunks."""
    svc = _get_kb_service()
    deleted = await svc.delete_document(document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"status": "deleted"}


# ========== Search ==========

@router.post("/search")
async def search_knowledge_base(
    query: str = Form(...),
    collection_id: Optional[int] = Form(None),
    top_k: int = Form(5),
    user=Depends(get_current_user),
):
    """
    Semantic search across knowledge base.
    Returns relevant document chunks ranked by similarity.
    """
    svc = _get_kb_service()
    results = await svc.search(query, collection_id=collection_id, top_k=top_k)
    return {"query": query, "results": results, "total": len(results)}
