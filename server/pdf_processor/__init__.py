"""
PDF Processor Module
Handles PDF text extraction with page number tracking for the Chat with PDF feature.
"""

import pypdf
from typing import List, Dict, Tuple


async def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file (simple version)"""
    try:
        with open(file_path, "rb") as file:
            reader = pypdf.PdfReader(file)
            text = ""

            for page in reader.pages:
                text += page.extract_text() + "\n"

            return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        raise


async def extract_text_with_pages(file_path: str) -> List[Dict[str, any]]:
    """
    Extract text from PDF file with page number tracking.

    Returns:
        List of dicts with 'text' and 'page_number' (1-indexed) for each page
    """
    try:
        pages_data = []
        with open(file_path, "rb") as file:
            reader = pypdf.PdfReader(file)

            for page_num, page in enumerate(reader.pages, start=1):
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    pages_data.append({
                        "text": page_text,
                        "page_number": page_num
                    })

        return pages_data
    except Exception as e:
        print(f"Error extracting text with pages from PDF: {e}")
        raise


async def extract_page_text(file_path: str, page_number: int) -> str:
    """Extract text from specific page (0-indexed)"""
    try:
        with open(file_path, "rb") as file:
            reader = pypdf.PdfReader(file)

            if page_number >= len(reader.pages):
                return ""

            page = reader.pages[page_number]
            return page.extract_text()
    except Exception as e:
        print(f"Error extracting page {page_number}: {e}")
        return ""


def count_pages(file_path: str) -> int:
    """Count total pages in PDF"""
    try:
        with open(file_path, "rb") as file:
            reader = pypdf.PdfReader(file)
            return len(reader.pages)
    except Exception as e:
        print(f"Error counting pages: {e}")
        return 0


def get_pdf_metadata(file_path: str) -> Dict[str, any]:
    """Extract PDF metadata"""
    try:
        with open(file_path, "rb") as file:
            reader = pypdf.PdfReader(file)
            metadata = reader.metadata

            return {
                "title": metadata.title if metadata and metadata.title else None,
                "author": metadata.author if metadata and metadata.author else None,
                "subject": metadata.subject if metadata and metadata.subject else None,
                "creator": metadata.creator if metadata and metadata.creator else None,
                "total_pages": len(reader.pages)
            }
    except Exception as e:
        print(f"Error extracting PDF metadata: {e}")
        return {"total_pages": 0}
