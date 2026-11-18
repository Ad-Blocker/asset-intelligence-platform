"""
Technical Documents Package.

Provides document loading, paragraph chunking, vector embedding generation,
local vector indexing, and semantic RAG retrieval over engineering manuals.
"""

from .document_loader import DocumentLoader
from .chunker import DocumentChunker, DocumentChunk
from .embedding_service import EmbeddingService
from .vector_store import VectorStore
from .document_service import DocumentService, RetrievedDocumentChunk

__all__ = [
    "DocumentLoader",
    "DocumentChunker",
    "DocumentChunk",
    "EmbeddingService",
    "VectorStore",
    "DocumentService",
    "RetrievedDocumentChunk"
]
