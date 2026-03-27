from sqlalchemy import Column, Integer, String, ForeignKey, Text, JSON
from pgvector.sqlalchemy import Vector
from app.models.base import Base, TimestampMixin


class KBCollection(Base, TimestampMixin):
    __tablename__ = "kb_collections"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"))
    doc_count = Column(Integer, default=0)
    status = Column(String(20), default="active")  # active / archived


class KBDocument(Base, TimestampMixin):
    __tablename__ = "kb_documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    collection_id = Column(Integer, ForeignKey("kb_collections.id"), nullable=False)
    filename = Column(String(500), nullable=False)
    file_type = Column(String(20))   # pdf / docx / xlsx / txt
    file_size = Column(Integer)       # bytes
    file_path = Column(String(500))   # storage path
    chunk_count = Column(Integer, default=0)
    status = Column(String(20), default="processing")  # processing / ready / failed
    error_msg = Column(Text)


class KBChunk(Base, TimestampMixin):
    __tablename__ = "kb_chunks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("kb_documents.id"), nullable=False)
    collection_id = Column(Integer, ForeignKey("kb_collections.id"), nullable=False)
    content = Column(Text, nullable=False)
    metadata_json = Column(JSON)      # page number, section, etc.
    embedding = Column(Vector(384))   # pgvector — dimension matches embedding model
