import pypdf
from typing import List


async def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file"""
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


async def extract_page_text(file_path: str, page_number: int) -> str:
    """Extract text from specific page"""
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
