"""
Document Chunker Module.

Provides the DocumentChunker class responsible for splitting extracted document text
into paragraph-aware chunks with configurable size and overlap while tracking page attribution.
"""

from dataclasses import dataclass
from typing import List, Tuple
import os

from utils.logger import setup_logger
from config import config

logger = setup_logger("documents.chunker", config.log_level)


@dataclass
class DocumentChunk:
    """Represents a single text chunk extracted from a document page."""
    chunk_id: str
    page_number: int
    text: str
    source_document: str


class DocumentChunker:
    """Paragraph-aware text chunking engine."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 75) -> None:
        """
        Initialize DocumentChunker with chunk size and overlap limits.

        Args:
            chunk_size (int): Target character count per chunk (default: ~500).
            chunk_overlap (int): Overlap character count between consecutive chunks (default: ~75).
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_page_text(self, page_number: int, text: str, source_doc: str) -> List[DocumentChunk]:
        """
        Chunk text from a single document page while respecting paragraph breaks.

        Args:
            page_number (int): Page number (1-indexed).
            text (str): Raw text of the page.
            source_doc (str): Source document name/path.

        Returns:
            List[DocumentChunk]: List of generated DocumentChunk objects.
        """
        doc_basename = os.path.basename(source_doc)
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        if not paragraphs:
            paragraphs = [text.strip()]

        chunks: List[DocumentChunk] = []
        current_chunk_text = ""
        chunk_counter = 0

        for para in paragraphs:
            # If paragraph itself is larger than chunk_size, split by sentences or sliding windows
            if len(para) > self.chunk_size:
                start = 0
                while start < len(para):
                    end = min(start + self.chunk_size, len(para))
                    sub_text = para[start:end].strip()
                    if sub_text:
                        chunk_counter += 1
                        chunk_id = f"{doc_basename}_p{page_number}_c{chunk_counter}"
                        chunks.append(DocumentChunk(
                            chunk_id=chunk_id,
                            page_number=page_number,
                            text=sub_text,
                            source_document=source_doc
                        ))
                    start += (self.chunk_size - self.chunk_overlap)
                continue

            # Accumulate paragraph text if within chunk_size
            if len(current_chunk_text) + len(para) + 2 <= self.chunk_size:
                current_chunk_text = f"{current_chunk_text}\n\n{para}".strip()
            else:
                if current_chunk_text:
                    chunk_counter += 1
                    chunk_id = f"{doc_basename}_p{page_number}_c{chunk_counter}"
                    chunks.append(DocumentChunk(
                        chunk_id=chunk_id,
                        page_number=page_number,
                        text=current_chunk_text,
                        source_document=source_doc
                    ))
                # Start new chunk with overlap
                overlap_text = current_chunk_text[-self.chunk_overlap:] if len(current_chunk_text) > self.chunk_overlap else ""
                current_chunk_text = f"{overlap_text}\n\n{para}".strip() if overlap_text else para

        # Flush final accumulated chunk
        if current_chunk_text:
            chunk_counter += 1
            chunk_id = f"{doc_basename}_p{page_number}_c{chunk_counter}"
            chunks.append(DocumentChunk(
                chunk_id=chunk_id,
                page_number=page_number,
                text=current_chunk_text,
                source_document=source_doc
            ))

        return chunks

    def chunk_document(self, pages: List[Tuple[int, str]], source_doc: str) -> List[DocumentChunk]:
        """
        Process page text tuples into a unified list of DocumentChunk objects across a document.

        Args:
            pages (List[Tuple[int, str]]): List of (page_number, page_text) tuples.
            source_doc (str): Source document path/identifier.

        Returns:
            List[DocumentChunk]: Complete list of DocumentChunk instances.
        """
        all_chunks: List[DocumentChunk] = []
        for page_num, text in pages:
            page_chunks = self.chunk_page_text(page_num, text, source_doc)
            all_chunks.extend(page_chunks)

        logger.info("Generated %d chunks across %d pages for document '%s'.", len(all_chunks), len(pages), source_doc)
        return all_chunks
