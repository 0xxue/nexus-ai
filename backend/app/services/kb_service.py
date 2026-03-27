"""
Knowledge Base Service — Document upload, chunking, indexing, search

Full pipeline:
  Upload file → Parse (PDF/Word/Excel) → Chunk → Embed → Store in pgvector
  Query → Embed → Vector search → Return relevant chunks with source attribution
"""

import os
import json
import structlog
from typing import Optional
from datetime import datetime

from app.core.config import get_settings
from app.services.doc_parser import DocumentParser, ParsedChunk
from app.services.embedding import get_embedding_service

logger = structlog.get_logger()

# In-memory storage for demo (replace with PostgreSQL + pgvector in production)
_kb_store: dict = {
    "collections": {},   # id → {name, description, doc_count}
    "documents": {},     # id → {collection_id, filename, chunks}
    "chunks": [],        # [{id, doc_id, collection_id, content, metadata, embedding}]
}
_next_id = {"collection": 1, "document": 1, "chunk": 1}


def _gen_id(entity: str) -> int:
    current = _next_id[entity]
    _next_id[entity] += 1
    return current


class KnowledgeBaseService:
    """Manage knowledge bases, documents, and vector search."""

    def __init__(self):
        self.parser = DocumentParser(chunk_size=500, chunk_overlap=50)
        self.embedding_service = get_embedding_service()
        self.settings = get_settings()

    # ========== Collections ==========

    async def list_collections(self, owner_id: int = None) -> list[dict]:
        """List all knowledge bases."""
        collections = list(_kb_store["collections"].values())
        if owner_id:
            collections = [c for c in collections if c.get("owner_id") == owner_id]
        return collections

    async def create_collection(self, name: str, description: str = "", owner_id: int = None) -> dict:
        """Create a new knowledge base."""
        coll_id = _gen_id("collection")
        collection = {
            "id": coll_id,
            "name": name,
            "description": description,
            "owner_id": owner_id,
            "doc_count": 0,
            "status": "active",
            "created_at": datetime.now().isoformat(),
        }
        _kb_store["collections"][coll_id] = collection
        logger.info("Collection created", id=coll_id, name=name)
        return collection

    async def delete_collection(self, collection_id: int) -> bool:
        """Delete a knowledge base and all its documents."""
        if collection_id not in _kb_store["collections"]:
            return False

        # Remove all related documents and chunks
        doc_ids = [
            doc_id for doc_id, doc in _kb_store["documents"].items()
            if doc["collection_id"] == collection_id
        ]
        for doc_id in doc_ids:
            del _kb_store["documents"][doc_id]

        _kb_store["chunks"] = [
            c for c in _kb_store["chunks"]
            if c["collection_id"] != collection_id
        ]

        del _kb_store["collections"][collection_id]
        logger.info("Collection deleted", id=collection_id)
        return True

    # ========== Documents ==========

    async def upload_document(self, collection_id: int, file_path: str, filename: str) -> dict:
        """
        Upload and process a document:
        1. Parse file (PDF/Word/Excel/Text)
        2. Split into chunks
        3. Generate embeddings
        4. Store chunks with vectors
        """
        if collection_id not in _kb_store["collections"]:
            raise ValueError(f"Collection {collection_id} not found")

        doc_id = _gen_id("document")
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        file_type = os.path.splitext(filename)[1].lower().lstrip(".")

        document = {
            "id": doc_id,
            "collection_id": collection_id,
            "filename": filename,
            "file_type": file_type,
            "file_size": file_size,
            "chunk_count": 0,
            "status": "processing",
            "created_at": datetime.now().isoformat(),
        }
        _kb_store["documents"][doc_id] = document

        try:
            # Step 1: Parse
            logger.info("Parsing document", filename=filename, type=file_type)
            parsed_chunks = self.parser.parse(file_path)

            if not parsed_chunks:
                document["status"] = "failed"
                document["error_msg"] = "No content extracted"
                return document

            # Step 2: Generate embeddings
            logger.info("Generating embeddings", chunks=len(parsed_chunks))
            texts = [chunk.content for chunk in parsed_chunks]
            embeddings = await self.embedding_service.embed(texts)

            # Step 3: Store chunks with vectors
            for i, (chunk, embedding) in enumerate(zip(parsed_chunks, embeddings)):
                chunk_id = _gen_id("chunk")
                _kb_store["chunks"].append({
                    "id": chunk_id,
                    "document_id": doc_id,
                    "collection_id": collection_id,
                    "content": chunk.content,
                    "metadata": {**chunk.metadata, "filename": filename},
                    "embedding": embedding.tolist(),
                })

            document["chunk_count"] = len(parsed_chunks)
            document["status"] = "ready"

            # Update collection doc count
            coll = _kb_store["collections"][collection_id]
            coll["doc_count"] = coll.get("doc_count", 0) + 1

            logger.info("Document processed", doc_id=doc_id, chunks=len(parsed_chunks))
            return document

        except Exception as e:
            document["status"] = "failed"
            document["error_msg"] = str(e)
            logger.error("Document processing failed", error=str(e))
            return document

    async def delete_document(self, document_id: int) -> bool:
        """Delete a document and its chunks."""
        if document_id not in _kb_store["documents"]:
            return False

        doc = _kb_store["documents"][document_id]
        collection_id = doc["collection_id"]

        # Remove chunks
        _kb_store["chunks"] = [
            c for c in _kb_store["chunks"]
            if c["document_id"] != document_id
        ]

        # Update collection count
        if collection_id in _kb_store["collections"]:
            coll = _kb_store["collections"][collection_id]
            coll["doc_count"] = max(0, coll.get("doc_count", 1) - 1)

        del _kb_store["documents"][document_id]
        logger.info("Document deleted", id=document_id)
        return True

    async def list_documents(self, collection_id: int) -> list[dict]:
        """List documents in a collection."""
        return [
            doc for doc in _kb_store["documents"].values()
            if doc["collection_id"] == collection_id
        ]

    # ========== Search ==========

    async def search(self, query: str, collection_id: int = None, top_k: int = 5) -> list[dict]:
        """
        Semantic search across knowledge base.
        Returns relevant chunks with similarity scores and source attribution.
        """
        import numpy as np

        # Embed query
        query_embedding = await self.embedding_service.embed([query])
        query_vec = query_embedding[0]

        # Filter chunks by collection
        candidates = _kb_store["chunks"]
        if collection_id:
            candidates = [c for c in candidates if c["collection_id"] == collection_id]

        if not candidates:
            return []

        # Compute cosine similarity
        results = []
        for chunk in candidates:
            chunk_vec = np.array(chunk["embedding"])
            similarity = float(np.dot(query_vec, chunk_vec) / (
                np.linalg.norm(query_vec) * np.linalg.norm(chunk_vec) + 1e-8
            ))
            results.append({
                "chunk_id": chunk["id"],
                "document_id": chunk["document_id"],
                "collection_id": chunk["collection_id"],
                "content": chunk["content"],
                "metadata": chunk["metadata"],
                "similarity": round(similarity, 4),
            })

        # Sort by similarity descending
        results.sort(key=lambda x: x["similarity"], reverse=True)

        logger.info("KB search", query=query[:50], results=len(results[:top_k]))
        return results[:top_k]
