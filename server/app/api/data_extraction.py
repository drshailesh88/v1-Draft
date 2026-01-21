from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from core.database import supabase, get_user_from_token
import tempfile
import os

router = APIRouter()

class ExtractTablesRequest(BaseModel):
    document_id: str

class TableData(BaseModel):
    table_id: int
    page: int
    data: List[List[str]]
    csv: str

class ExtractTablesResponse(BaseModel):
    tables: List[TableData]

@router.post("/extract-tables", response_model=ExtractTablesResponse)
async def extract_tables(
    request: ExtractTablesRequest,
    token: str = None
):
    """Extract tables from document"""
    user = await get_user_from_token(token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Verify document belongs to user
    doc_response = supabase.table('documents').select('*').eq('id', request.document_id).eq('user_id', user['id']).execute()
    
    if not doc_response.data:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # TODO: Get file from storage (Supabase Storage)
    # For now, return placeholder
    return ExtractTablesResponse(tables=[])

@router.post("/extract-figures")
async def extract_figures(
    document_id: str,
    token: str = None
):
    """Extract figures and captions from document"""
    user = await get_user_from_token(token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Verify document belongs to user
    doc_response = supabase.table('documents').select('*').eq('id', document_id).eq('user_id', user['id']).execute()
    
    if not doc_response.data:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # TODO: Implement figure extraction using unstructured
    # For now, return placeholder
    return {
        "figures": [],
        "message": "Figure extraction not implemented yet"
    }

@router.post("/export-csv")
async def export_to_csv(
    data: List[List[str]],
    filename: str = "tables.csv"
):
    """Export tables to CSV"""
    import io
    import csv
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    for row in data:
        writer.writerow(row)
    
    return {
        "csv": output.getvalue(),
        "filename": filename
    }

@router.post("/export-excel")
async def export_to_excel(
    data: List[List[str]],
    filename: str = "tables.xlsx"
):
    """Export tables to Excel"""
    # TODO: Implement Excel export using openpyxl
    return {
        "message": "Excel export not implemented yet",
        "filename": filename
    }
