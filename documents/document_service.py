"""
Document Service Module.

Provides the DocumentService class which acts as the sole high-level coordinator interface
for document loading, paragraph chunking, vector embedding generation, indexing, and semantic retrieval.
Returns clean, structured RetrievedDocumentChunk domain dataclass instances.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
import os

from .document_loader import DocumentLoader
from .chunker import DocumentChunker, DocumentChunk
from .embedding_service import EmbeddingService
from .vector_store import VectorStore
from utils.logger import setup_logger
from utils.exceptions import DocumentException
from config import config

logger = setup_logger("documents.service", config.log_level)


@dataclass
class RetrievedDocumentChunk:
    """Structured domain object representing a semantic search result."""
    chunk_id: str
    page_number: int
    similarity_score: float
    text: str
    source_document: str


class DocumentService:
    """High-level document processing, vector indexing, and RAG retrieval coordinator."""

    def __init__(
        self,
        base_dir: Optional[str] = None,
        chunk_size: int = 500,
        chunk_overlap: int = 75
    ) -> None:
        """
        Initialize DocumentService pipeline components.

        Args:
            base_dir (Optional[str]): Base directory for PDF document resolution.
            chunk_size (int): Character size limit per chunk.
            chunk_overlap (int): Overlap character count between chunks.
        """
        self.base_dir = base_dir or config.documents.documents_dir
        self.loader = DocumentLoader(base_dir=self.base_dir)
        self.chunker = DocumentChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()

        # In-memory cache structures
        self._document_cache: Dict[str, List[DocumentChunk]] = {}
        self._is_indexed: bool = False

    def load_document(self, pdf_path: str) -> List[DocumentChunk]:
        """
        Load a PDF document, extract text per page, and generate chunks (cached).

        Args:
            pdf_path (str): Relative or absolute path to PDF file.

        Returns:
            List[DocumentChunk]: List of DocumentChunk instances.

        Raises:
            DocumentException: If loading or chunking fails.
        """
        resolved_path = self.loader.resolve_file_path(pdf_path)

        if resolved_path in self._document_cache:
            logger.info("Document chunk cache hit for '%s'.", resolved_path)
            return self._document_cache[resolved_path]

        logger.info("Document chunk cache miss for '%s'. Extracting & chunking...", resolved_path)
        pages = self.loader.load_pdf(resolved_path)
        chunks = self.chunker.chunk_document(pages, source_doc=resolved_path)

        self._document_cache[resolved_path] = chunks
        return chunks

    def build_index(self, document_paths: List[str], force_rebuild: bool = False) -> None:
        """
        Load document paths, generate vector embeddings, and build local vector index.

        Args:
            document_paths (List[str]): List of PDF document paths to index.
            force_rebuild (bool): Force rebuild index even if already built.

        Raises:
            DocumentException: If document loading or embedding generation fails.
        """
        if self._is_indexed and not force_rebuild:
            logger.info("Vector index already built. Skipping build_index call.")
            return

        all_chunks: List[DocumentChunk] = []
        for path in document_paths:
            chunks = self.load_document(path)
            all_chunks.extend(chunks)

        if not all_chunks:
            logger.warning("No chunks available to build vector index.")
            return

        logger.info("Generating vector embeddings for %d total chunks...", len(all_chunks))
        chunk_texts = [c.text for c in all_chunks]
        embeddings = self.embedding_service.embed_chunks(chunk_texts)

        self.vector_store.add_embeddings(all_chunks, embeddings)
        self._is_indexed = True
        logger.info("Vector index build completed successfully (%d chunks indexed).", len(all_chunks))

    def query(self, question: str, top_k: int = 5) -> List[RetrievedDocumentChunk]:
        """
        Execute semantic vector similarity search for a natural language question.

        Args:
            question (str): User question string.
            top_k (int): Number of top matching chunks to retrieve.

        Returns:
            List[RetrievedDocumentChunk]: Structured domain objects with text, page numbers, and similarity scores.

        Raises:
            DocumentException: If index is not built or search fails.
        """
        if not self._is_indexed:
            raise DocumentException("DocumentService index has not been built. Call build_index() first.")

        if not question.strip():
            raise DocumentException("Query question string cannot be empty.")

        logger.info("Executing semantic search for query: '%s' (top_k=%d)...", question, top_k)
        query_embedding = self.embedding_service.embed_text(question)
        matches = self.vector_store.similarity_search(query_embedding, top_k=top_k)

        retrieved_chunks: List[RetrievedDocumentChunk] = []
        for chunk, score in matches:
            retrieved_chunks.append(RetrievedDocumentChunk(
                chunk_id=chunk.chunk_id,
                page_number=chunk.page_number,
                similarity_score=round(float(score), 4),
                text=chunk.text,
                source_document=chunk.source_document
            ))

        logger.info("Retrieved %d matching chunks for question: '%s'", len(retrieved_chunks), question)
        return retrieved_chunks

    def clear_cache(self) -> None:
        """Clear all loaded document caches and vector index state."""
        self._document_cache.clear()
        self.vector_store = VectorStore()
        self._is_indexed = False
        logger.info("DocumentService cache and vector store cleared.")
