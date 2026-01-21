from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from core.database import supabase, get_user_from_token, supabase_admin
import tempfile
import os
import pdfplumber
import pandas as pd
from io import BytesIO, StringIO
import csv
import base64
import fitz  # PyMuPDF for image extraction

router = APIRouter()


class ExtractTablesRequest(BaseModel):
    document_id: str


class TableData(BaseModel):
    table_id: str
    page: int
    data: List[List[str]]
    csv: str


class ExtractTablesResponse(BaseModel):
    tables: List[TableData]


class FigureData(BaseModel):
    figure_id: str
    page: int
    caption: Optional[str]
    image_data: str


class ExtractFiguresResponse(BaseModel):
    figures: List[FigureData]
    message: str


@router.post("/extract-tables", response_model=ExtractTablesResponse)
async def extract_tables(request: ExtractTablesRequest, token: str = None):
    """Extract tables from document using PDFPlumber"""
    user = await get_user_from_token(token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    doc_response = (
        supabase.table("documents")
        .select("*")
        .eq("id", request.document_id)
        .eq("user_id", user["id"])
        .execute()
    )

    if not doc_response.data:
        raise HTTPException(status_code=404, detail="Document not found")

    document = doc_response.data[0] if doc_response.data else None
    storage_key = document.get("storage_key") if document else None

    if not storage_key:
        raise HTTPException(status_code=400, detail="No storage key found for document")

    try:
        pdf_bytes = supabase.storage.from_("documents").download(storage_key)
        tables = extract_tables_from_pdf(pdf_bytes)
        return ExtractTablesResponse(tables=tables)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error extracting tables: {str(e)}"
        )


def extract_tables_from_pdf(pdf_bytes: bytes) -> List[TableData]:
    """Extract tables from PDF bytes using PDFPlumber"""
    tables = []

    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            # Extract tables from page
            page_tables = page.extract_tables()

            for table_idx, table in enumerate(page_tables, start=1):
                if table and len(table) > 0:
                    # Filter empty tables
                    if not any(any(cell for cell in row) for row in table):
                        continue

                    # Convert to list of lists (string format)
                    data = [
                        [str(cell) if cell else "" for cell in row] for row in table
                    ]

                    # Generate CSV
                    csv_buffer = StringIO()
                    csv_writer = csv.writer(csv_buffer)
                    csv_writer.writerows(data)
                    csv_content = csv_buffer.getvalue()

                    tables.append(
                        TableData(
                            table_id=f"{page_num}-{table_idx}",
                            page=page_num,
                            data=data,
                            csv=csv_content,
                        )
                    )

    return tables


def extract_figures_from_pdf(pdf_bytes: bytes) -> List[FigureData]:
    """Extract figures and captions from PDF bytes using PDFPlumber"""
    figures = []

    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""

            # Extract figure captions using pattern matching
            # Look for patterns like "Figure 1:", "Fig. 1", "Figure 1." etc.
            import re

            # Pattern to match figure captions
            figure_patterns = [
                r"Figure\s+\d+[:.]\s*(.+)",
                r"Fig\.?\s+\d+[:.]\s*(.+)",
                r"FIGURE\s+\d+[:.]\s*(.+)",
                r"FIG\.?\s+\d+[:.]\s*(.+)",
            ]

            figure_count = 0
            for pattern in figure_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    caption = match.group(1).strip()
                    figure_count += 1

                    figures.append(
                        FigureData(
                            figure_id=f"{page_num}-{figure_count}",
                            page=page_num,
                            caption=caption,
                            image_data="",  # Image extraction requires additional libraries (e.g., PyMuPDF)
                        )
                    )

            # Also detect image objects on the page
            if page.images and figure_count == 0:
                for img_idx, image in enumerate(page.images, start=1):
                    # Check if there's text near this image that might be a caption
                    bbox = (image["x0"], image["top"], image["x1"], image["bottom"])

                    # Look for text below the image
                    words = page.extract_words()
                    caption = None

                    for word in words:
                        if (
                            word["top"] > image["bottom"]
                            and abs(word["x0"] - image["x0"]) < 100
                        ):
                            if "fig" in word["text"].lower():
                                caption = word["text"]
                                break

                    figures.append(
                        FigureData(
                            figure_id=f"{page_num}-{img_idx}",
                            page=page_num,
                            caption=caption,
                            image_data="",  # Image extraction requires additional libraries
                        )
                    )

    return figures


@router.post("/extract-figures", response_model=ExtractFiguresResponse)
async def extract_figures(document_id: str, token: str = None):
    """Extract figures and captions from document"""
    user = await get_user_from_token(token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    doc_response = (
        supabase.table("documents")
        .select("*")
        .eq("id", document_id)
        .eq("user_id", user["id"])
        .execute()
    )

    if not doc_response.data:
        raise HTTPException(status_code=404, detail="Document not found")

    document = doc_response.data[0] if doc_response.data else None
    storage_key = document.get("storage_key") if document else None

    if not storage_key:
        return ExtractFiguresResponse(
            figures=[], message="No storage key found for document"
        )

    try:
        pdf_bytes = supabase.storage.from_("documents").download(storage_key)
        figures = extract_figures_from_pdf(pdf_bytes)
        return ExtractFiguresResponse(
            figures=figures, message=f"Extracted {len(figures)} figures"
        )
    except Exception as e:
        return ExtractFiguresResponse(
            figures=[], message=f"Error extracting figures: {str(e)}"
        )


@router.post("/export-csv")
async def export_to_csv(data: List[List[str]], filename: str = "tables.csv"):
    """Export tables to CSV"""
    import io
    import csv

    output = io.StringIO()
    writer = csv.writer(output)

    for row in data:
        writer.writerow(row)

    return {"csv": output.getvalue(), "filename": filename}


@router.post("/export-excel")
async def export_to_excel(data: List[List[str]], filename: str = "tables.xlsx"):
    """Export tables to Excel using openpyxl"""
    import openpyxl
    from io import BytesIO

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Extracted Tables"

    for row_idx, row in enumerate(data, start=1):
        for col_idx, cell in enumerate(row, start=1):
            ws.cell(row=row_idx, column=col_idx, value=cell)

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    return {"excel": buffer.getvalue().hex(), "filename": filename}
