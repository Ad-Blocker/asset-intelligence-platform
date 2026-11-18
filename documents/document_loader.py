"""
Document Loader Module.

Provides the DocumentLoader class responsible for locating PDF files,
validating file existence, extracting page-by-page text using PyMuPDF (fitz),
and returning page text tuples with error handling.
"""

import os
from typing import List, Tuple
import fitz  # PyMuPDF

from utils.logger import setup_logger
from utils.exceptions import DocumentException
from config import config

logger = setup_logger("documents.loader", config.log_level)


class DocumentLoader:
    """PDF text extractor leveraging PyMuPDF."""

    def __init__(self, base_dir: str = "documents") -> None:
        """
        Initialize DocumentLoader with default base search directory.

        Args:
            base_dir (str): Base directory for resolving relative PDF paths.
        """
        self.base_dir = base_dir

    def resolve_file_path(self, pdf_path: str) -> str:
        """
        Resolve relative or absolute PDF file path across common search locations.

        Args:
            pdf_path (str): PDF file path or filename.

        Returns:
            str: Resolved absolute path.

        Raises:
            DocumentException: If PDF file cannot be located on disk.
        """
        candidate_paths = [
            pdf_path,
            os.path.join(self.base_dir, pdf_path),
            os.path.join("documents", os.path.basename(pdf_path)),
            os.path.join(".", pdf_path)
        ]

        for path in candidate_paths:
            if os.path.isfile(path):
                return os.path.abspath(path)

        logger.error("PDF Document not found: '%s' (searched: %s)", pdf_path, candidate_paths)
        raise DocumentException(f"PDF Document '{pdf_path}' not found on disk.")

    def load_pdf(self, pdf_path: str) -> List[Tuple[int, str]]:
        """
        Extract page-by-page raw text from a target PDF document using PyMuPDF.

        Args:
            pdf_path (str): Path to PDF document.

        Returns:
            List[Tuple[int, str]]: List of (page_number, page_text) tuples (1-indexed).

        Raises:
            DocumentException: If PDF is missing, encrypted, unreadable, or empty.
        """
        resolved_path = self.resolve_file_path(pdf_path)
        logger.info("Loading PDF document from '%s'...", resolved_path)

        try:
            doc = fitz.open(resolved_path)
            if doc.is_encrypted:
                logger.error("Encrypted PDF document cannot be read: '%s'", resolved_path)
                raise DocumentException(f"PDF document '{resolved_path}' is encrypted.")

            if len(doc) == 0:
                logger.error("PDF document contains 0 pages: '%s'", resolved_path)
                raise DocumentException(f"PDF document '{resolved_path}' contains no pages.")

            pages: List[Tuple[int, str]] = []
            total_extracted_chars = 0

            for page_idx in range(len(doc)):
                page = doc[page_idx]
                page_text = page.get_text("text").strip()
                if page_text:
                    pages.append((page_idx + 1, page_text))
                    total_extracted_chars += len(page_text)

            doc.close()

            if not pages or total_extracted_chars == 0:
                logger.error("No readable text extracted from PDF '%s'.", resolved_path)
                raise DocumentException(f"No readable text could be extracted from PDF '{resolved_path}'.")

            logger.info("Extracted %d pages (%d characters) from '%s'.", len(pages), total_extracted_chars, resolved_path)
            return pages

        except DocumentException:
            raise
        except Exception as e:
            logger.error("Failed to extract text from PDF '%s': %s", resolved_path, e)
            raise DocumentException(f"Failed to read PDF document '{resolved_path}': {e}") from e
