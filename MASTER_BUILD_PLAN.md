# V1 DRAFT - MASTER BUILD PLAN
# FOR ANY LLM TO FOLLOW

## WHAT IS THIS PROJECT?

V1 Draft is an **academic research platform** that helps researchers:
- Search academic papers across multiple databases
- Chat with PDFs using AI
- Write research papers with AI assistance
- Generate citations automatically
- Detect AI-generated content
- Conduct systematic reviews

**Live URL**: https://v1-draft-production.up.railway.app

---

## CURRENT STATUS SUMMARY

### WORKING FEATURES (8/12) - DO NOT TOUCH UNLESS BROKEN
| Feature | Status | Backend | Frontend |
|---------|--------|---------|----------|
| AI Writer | WORKING | `server/app/api/ai_writer.py` | `client/src/app/ai-writer/` |
| Deep Review | WORKING | `server/app/api/deep_review.py` | `client/src/app/deep-review/` |
| Paraphraser | WORKING | `server/app/api/paraphraser.py` | `client/src/app/paraphraser/` |
| Systematic Review | WORKING | `server/app/api/systematic_review.py` | `client/src/app/systematic-review/` |
| AI Detector | WORKING | `server/app/api/ai_detector.py` | `client/src/app/ai-detector/` |
| Topic Discovery | WORKING | `server/app/api/topics.py` | `client/src/app/topics/` |
| Payments | WORKING | `server/app/api/payments.py` | `client/src/app/subscription/` |
| Citations | WORKING | `server/app/api/citations.py` | `client/src/app/citations/` |

### BROKEN/INCOMPLETE FEATURES (4/12) - THESE NEED FIXING
| Feature | Status | Problem | Priority |
|---------|--------|---------|----------|
| Literature Search | PARTIAL | MCP servers not integrated properly | HIGH |
| Chat with PDF | BROKEN | Missing `pdf_processor` and `langchain_chains` modules | HIGH |
| Citation Booster | PARTIAL | Depends on Literature Search | MEDIUM |
| Data Extraction | STUB | Only placeholder code, no real implementation | LOW |

---

## WHAT NEEDS TO BE BUILT

### TASK 1: FIX LITERATURE SEARCH (HIGH PRIORITY)
**Current Problem**: MCP integration is broken/incomplete
**Location**: `server/app/api/literature.py`

**WHAT TO DO**:
Instead of MCP, use direct Python libraries that WORK:

**REPOS TO USE**:
1. `arxiv` - MIT License - https://github.com/lukasschwab/arxiv.py
2. `scholarly` - MIT License - https://github.com/scholarly-python-package/scholarly
3. `biopython` (for PubMed) - BSD License - https://github.com/biopython/biopython
4. `semanticscholar` - MIT License - https://github.com/danielnsilva/semanticscholar

**STEP BY STEP**:
```
STEP 1: Install libraries
   pip install arxiv scholarly biopython semanticscholar

STEP 2: Create file: server/core/literature_clients.py
   - ArxivClient class using arxiv library
   - PubMedClient class using Bio.Entrez
   - ScholarClient class using scholarly
   - SemanticScholarClient class using semanticscholar

STEP 3: Update server/app/api/literature.py
   - Remove MCP code (lines 60-120)
   - Import from literature_clients.py
   - Call each client and merge results
   - Deduplicate by DOI

STEP 4: Test
   curl -X POST http://localhost:8000/api/literature/search \
     -H "Content-Type: application/json" \
     -d '{"query": "machine learning", "sources": ["arxiv", "pubmed"]}'
```

**EXPECTED OUTPUT**:
```python
# server/core/literature_clients.py

import arxiv
from Bio import Entrez
from scholarly import scholarly
from semanticscholar import SemanticScholar

Entrez.email = "your@email.com"  # Required for PubMed

class ArxivClient:
    def search(self, query: str, max_results: int = 10):
        search = arxiv.Search(query=query, max_results=max_results)
        results = []
        for paper in search.results():
            results.append({
                "title": paper.title,
                "authors": [a.name for a in paper.authors],
                "abstract": paper.summary,
                "url": paper.pdf_url,
                "published": str(paper.published),
                "source": "arxiv"
            })
        return results

class PubMedClient:
    def search(self, query: str, max_results: int = 10):
        handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
        record = Entrez.read(handle)
        ids = record["IdList"]

        if not ids:
            return []

        handle = Entrez.efetch(db="pubmed", id=ids, rettype="xml")
        records = Entrez.read(handle)

        results = []
        for article in records["PubmedArticle"]:
            medline = article["MedlineCitation"]
            article_data = medline["Article"]
            results.append({
                "title": article_data["ArticleTitle"],
                "authors": [a.get("LastName", "") for a in article_data.get("AuthorList", [])],
                "abstract": article_data.get("Abstract", {}).get("AbstractText", [""])[0],
                "pmid": str(medline["PMID"]),
                "source": "pubmed"
            })
        return results

class SemanticScholarClient:
    def __init__(self):
        self.sch = SemanticScholar()

    def search(self, query: str, max_results: int = 10):
        results = self.sch.search_paper(query, limit=max_results)
        return [{
            "title": p.title,
            "authors": [a.name for a in (p.authors or [])],
            "abstract": p.abstract or "",
            "url": p.url,
            "year": p.year,
            "source": "semantic_scholar"
        } for p in results]
```

---

### TASK 2: FIX CHAT WITH PDF (HIGH PRIORITY)
**Current Problem**: Missing `pdf_processor` and `langchain_chains` modules
**Location**: `server/app/api/chat.py` imports these but they don't exist

**REPOS TO USE**:
1. `langchain` - MIT License - https://github.com/langchain-ai/langchain
2. `pdfplumber` - MIT License - https://github.com/jsvine/pdfplumber
3. `openai` - MIT License - Already installed

**STEP BY STEP**:
```
STEP 1: Create file: server/pdf_processor/processor.py

STEP 2: Create file: server/langchain_chains/rag_chain.py

STEP 3: Update imports in server/app/api/chat.py

STEP 4: Enable the router in server/main.py (uncomment line 65)

STEP 5: Test
   - Upload a PDF
   - Ask a question about it
```

**EXPECTED OUTPUT**:
```python
# server/pdf_processor/processor.py

import pdfplumber
from typing import List, Dict

def extract_text_from_pdf(file_path: str) -> str:
    """Extract all text from a PDF file."""
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
            text += "\n\n"
    return text

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    chunk_id = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        chunks.append({
            "id": chunk_id,
            "content": chunk,
            "start": start,
            "end": end
        })

        chunk_id += 1
        start = end - overlap

    return chunks

def process_pdf(file_path: str) -> List[Dict]:
    """Main function: extract text and chunk it."""
    text = extract_text_from_pdf(file_path)
    chunks = chunk_text(text)
    return chunks
```

```python
# server/langchain_chains/rag_chain.py

from openai import OpenAI
from typing import List, Dict

client = OpenAI()

def get_embeddings(texts: List[str]) -> List[List[float]]:
    """Get embeddings for a list of texts."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )
    return [item.embedding for item in response.data]

def find_similar_chunks(query: str, chunks: List[Dict], embeddings: List[List[float]], top_k: int = 3) -> List[Dict]:
    """Find most similar chunks to query using cosine similarity."""
    import numpy as np

    query_embedding = get_embeddings([query])[0]

    # Calculate cosine similarity
    similarities = []
    for i, emb in enumerate(embeddings):
        sim = np.dot(query_embedding, emb) / (np.linalg.norm(query_embedding) * np.linalg.norm(emb))
        similarities.append((i, sim))

    # Sort by similarity
    similarities.sort(key=lambda x: x[1], reverse=True)

    # Return top_k chunks
    return [chunks[i] for i, _ in similarities[:top_k]]

def answer_question(question: str, context_chunks: List[Dict]) -> str:
    """Answer question using context chunks."""
    context = "\n\n".join([c["content"] for c in context_chunks])

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful research assistant. Answer questions based only on the provided context. If the answer is not in the context, say so."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
        ]
    )

    return response.choices[0].message.content
```

---

### TASK 3: FIX CITATION BOOSTER (MEDIUM PRIORITY)
**Current Problem**: Depends on Literature Search which is broken
**Location**: `server/app/api/citation_booster.py`

**WHAT TO DO**:
Once Task 1 (Literature Search) is fixed, Citation Booster will work.

**VERIFICATION**:
```
STEP 1: Complete Task 1 first

STEP 2: Test Citation Booster
   curl -X POST http://localhost:8000/api/citation-booster/analyze \
     -H "Content-Type: application/json" \
     -d '{"text": "Machine learning has revolutionized healthcare..."}'
```

---

### TASK 4: IMPLEMENT DATA EXTRACTION (LOW PRIORITY)
**Current Problem**: Only placeholder code exists
**Location**: `server/app/api/data_extraction.py`

**REPOS TO USE**:
1. `pdfplumber` - MIT License - Already installed (for tables)
2. `camelot-py` - MIT License - https://github.com/camelot-dev/camelot
3. `unstructured` - Apache 2.0 - https://github.com/Unstructured-IO/unstructured

**STEP BY STEP**:
```
STEP 1: Install libraries
   pip install camelot-py[cv] unstructured

STEP 2: Update server/app/api/data_extraction.py
   - Implement extract_tables using pdfplumber
   - Implement extract_figures using unstructured
   - Implement CSV/Excel export

STEP 3: Enable router in server/main.py (uncomment line 79)

STEP 4: Test
   - Upload a PDF with tables
   - Extract tables
   - Export to CSV
```

**EXPECTED OUTPUT**:
```python
# Updated server/app/api/data_extraction.py

import pdfplumber
import pandas as pd
from io import BytesIO, StringIO
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import StreamingResponse

router = APIRouter()

@router.post("/extract-tables")
async def extract_tables(file: UploadFile = File(...)):
    """Extract tables from PDF."""
    content = await file.read()

    tables = []
    with pdfplumber.open(BytesIO(content)) as pdf:
        for page_num, page in enumerate(pdf.pages):
            page_tables = page.extract_tables()
            for table_num, table in enumerate(page_tables):
                if table:
                    # Convert to list of dicts
                    headers = table[0] if table else []
                    rows = table[1:] if len(table) > 1 else []

                    tables.append({
                        "page": page_num + 1,
                        "table_number": table_num + 1,
                        "headers": headers,
                        "rows": rows,
                        "row_count": len(rows)
                    })

    return {"tables": tables, "total_tables": len(tables)}

@router.post("/export-csv")
async def export_csv(table_data: dict):
    """Export table to CSV."""
    headers = table_data.get("headers", [])
    rows = table_data.get("rows", [])

    df = pd.DataFrame(rows, columns=headers)

    output = StringIO()
    df.to_csv(output, index=False)
    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=table.csv"}
    )

@router.post("/export-excel")
async def export_excel(table_data: dict):
    """Export table to Excel."""
    headers = table_data.get("headers", [])
    rows = table_data.get("rows", [])

    df = pd.DataFrame(rows, columns=headers)

    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=table.xlsx"}
    )
```

---

### TASK 5: ENABLE REMAINING ROUTERS (AFTER TASKS 1-4)
**Location**: `server/main.py`

**WHAT TO DO**:
```python
# Currently commented out - UNCOMMENT after fixing:

# Line 65: Uncomment after Task 2
from app.api import chat
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])

# Line 78: Already enabled (citations)
# app.include_router(citations.router, prefix="/api/citations", tags=["citations"])

# Line 79: Uncomment after Task 4
from app.api import data_extraction
app.include_router(data_extraction.router, prefix="/api/data-extraction", tags=["data-extraction"])

# Line 80: Already working, just enable
from app.api import ai_detector
app.include_router(ai_detector.router, prefix="/api/ai-detector", tags=["ai-detector"])
```

---

## FILE STRUCTURE REFERENCE

```
/Users/shaileshsingh/V1 draft/
├── server/                          # BACKEND (FastAPI)
│   ├── main.py                      # Entry point - enable routers here
│   ├── requirements.txt             # Python dependencies
│   ├── app/
│   │   └── api/                     # ALL API ENDPOINTS
│   │       ├── literature.py        # TASK 1: Fix this
│   │       ├── chat.py              # TASK 2: Fix this (needs modules)
│   │       ├── citation_booster.py  # TASK 3: Fix after Task 1
│   │       ├── data_extraction.py   # TASK 4: Implement this
│   │       ├── ai_writer.py         # WORKING - don't touch
│   │       ├── deep_review.py       # WORKING - don't touch
│   │       ├── paraphraser.py       # WORKING - don't touch
│   │       ├── systematic_review.py # WORKING - don't touch
│   │       ├── ai_detector.py       # WORKING - don't touch
│   │       ├── topics.py            # WORKING - don't touch
│   │       ├── payments.py          # WORKING - don't touch
│   │       └── citations.py         # WORKING - don't touch
│   ├── core/
│   │   ├── database.py              # Supabase client
│   │   ├── openai_client.py         # OpenAI client
│   │   └── literature_clients.py    # TASK 1: Create this file
│   ├── pdf_processor/
│   │   └── processor.py             # TASK 2: Create this file
│   └── langchain_chains/
│       └── rag_chain.py             # TASK 2: Create this file
│
├── client/                          # FRONTEND (Next.js)
│   └── src/app/                     # All pages exist, connected to backend
│
├── .env                             # Environment variables (DO NOT COMMIT)
├── Dockerfile                       # Docker config for Railway
└── railway.toml                     # Railway deployment config
```

---

## DEPENDENCIES TO ADD

Add these to `server/requirements.txt`:
```
# For Literature Search (Task 1)
arxiv>=2.0.0
scholarly>=1.7.0
biopython>=1.80
semanticscholar>=0.8.0

# For Data Extraction (Task 4)
camelot-py[cv]>=0.11.0
```

---

## HOW TO TEST LOCALLY

```bash
# 1. Go to server directory
cd "/Users/shaileshsingh/V1 draft/server"

# 2. Activate virtual environment
source ../venv/bin/activate

# 3. Install new dependencies
pip install -r requirements.txt

# 4. Run server
python main.py

# 5. Server runs at http://localhost:8000
# 6. API docs at http://localhost:8000/docs
```

---

## HOW TO DEPLOY

```bash
# 1. Go to project root
cd "/Users/shaileshsingh/V1 draft"

# 2. Commit changes
git add -A
git commit -m "fix: Implement missing features"

# 3. Deploy to Railway
railway up

# 4. Check deployment
curl https://v1-draft-production.up.railway.app/health
```

---

## CHECKLIST FOR LLM

- [ ] TASK 1: Create `server/core/literature_clients.py`
- [ ] TASK 1: Update `server/app/api/literature.py` to use new clients
- [ ] TASK 1: Test literature search endpoint
- [ ] TASK 2: Create `server/pdf_processor/processor.py`
- [ ] TASK 2: Create `server/langchain_chains/rag_chain.py`
- [ ] TASK 2: Update `server/app/api/chat.py` imports
- [ ] TASK 2: Uncomment chat router in `main.py`
- [ ] TASK 2: Test chat with PDF endpoint
- [ ] TASK 3: Verify citation booster works (after Task 1)
- [ ] TASK 4: Update `server/app/api/data_extraction.py`
- [ ] TASK 4: Uncomment data_extraction router in `main.py`
- [ ] TASK 4: Test data extraction endpoint
- [ ] TASK 5: Uncomment ai_detector router in `main.py`
- [ ] FINAL: Run all tests
- [ ] FINAL: Deploy to Railway

---

## IMPORTANT RULES FOR ANY LLM

1. **DO NOT** modify working features (AI Writer, Deep Review, Paraphraser, etc.)
2. **DO NOT** change database schema unless absolutely necessary
3. **DO NOT** remove existing code - only add or fix
4. **DO** test each feature after implementing
5. **DO** use MIT/Apache licensed repos only
6. **DO** commit after each task is complete
7. **DO** deploy after all tasks pass tests

---

## ENVIRONMENT VARIABLES NEEDED

These are already set in Railway. For local development, copy to `.env`:
```
SUPABASE_URL=<already set>
SUPABASE_ANON_KEY=<already set>
SUPABASE_SERVICE_ROLE_KEY=<already set>
OPENAI_API_KEY=<already set>
```

---

**Document Version**: 1.0
**Last Updated**: 2026-01-21
**Status**: Ready for Implementation
