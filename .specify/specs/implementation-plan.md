# V1 Draft - Implementation Specification

## Overview
Complete the remaining 4 broken/incomplete features of the V1 Draft academic research platform.

## Features to Implement

### Feature 1: Literature Search Fix
**Priority**: HIGH
**Status**: PARTIAL - MCP integration broken

#### Requirements
- Search academic papers from multiple sources
- Sources: arXiv, PubMed, Semantic Scholar
- Return unified paper format with: title, authors, abstract, url, source
- Deduplicate results by DOI/title

#### Technical Approach
- Remove broken MCP code
- Use direct Python libraries:
  - `arxiv` for arXiv
  - `biopython` (Bio.Entrez) for PubMed
  - `semanticscholar` for Semantic Scholar
- Create unified client interface

#### Files to Create/Modify
- CREATE: `server/core/literature_clients.py`
- MODIFY: `server/app/api/literature.py`

#### Dependencies
```
arxiv>=2.0.0
biopython>=1.80
semanticscholar>=0.8.0
```

#### Acceptance Criteria
- [ ] ArXiv search returns papers
- [ ] PubMed search returns papers
- [ ] Semantic Scholar search returns papers
- [ ] Results are deduplicated
- [ ] API endpoint responds in <5 seconds

---

### Feature 2: Chat with PDF Fix
**Priority**: HIGH
**Status**: BROKEN - Missing modules

#### Requirements
- Upload PDF files
- Extract text from PDFs
- Chunk text for vector search
- Answer questions using RAG

#### Technical Approach
- Use `pdfplumber` for PDF text extraction
- Chunk text with overlap (1000 chars, 200 overlap)
- Store embeddings in Supabase pgvector
- Use OpenAI for embeddings and chat

#### Files to Create/Modify
- CREATE: `server/pdf_processor/processor.py`
- CREATE: `server/langchain_chains/rag_chain.py`
- MODIFY: `server/app/api/chat.py` (update imports)
- MODIFY: `server/main.py` (enable router)

#### Dependencies
Already installed: `pdfplumber`, `openai`

#### Acceptance Criteria
- [ ] PDF upload works
- [ ] Text extraction succeeds
- [ ] Questions are answered with context
- [ ] Sources are cited in responses

---

### Feature 3: Citation Booster Verification
**Priority**: MEDIUM
**Status**: PARTIAL - Depends on Feature 1

#### Requirements
- Analyze text for citation gaps
- Suggest relevant papers
- Rank papers by relevance

#### Technical Approach
- Fix depends on Feature 1 (Literature Search)
- No code changes needed if Feature 1 works

#### Acceptance Criteria
- [ ] Gap analysis identifies missing citations
- [ ] Paper suggestions are relevant
- [ ] Relevance scores are accurate

---

### Feature 4: Data Extraction Implementation
**Priority**: LOW
**Status**: STUB - Placeholder only

#### Requirements
- Extract tables from PDFs
- Export to CSV/Excel formats
- Handle multi-page tables

#### Technical Approach
- Use `pdfplumber` for table extraction
- Use `pandas` for data manipulation
- Use `openpyxl` for Excel export

#### Files to Modify
- MODIFY: `server/app/api/data_extraction.py`
- MODIFY: `server/main.py` (enable router)

#### Dependencies
Already installed: `pdfplumber`, `pandas`, `openpyxl`

#### Acceptance Criteria
- [ ] Tables extracted from PDF
- [ ] CSV export works
- [ ] Excel export works

---

## Implementation Order

```
1. Feature 1: Literature Search (unblocks Feature 3)
   └── Create literature_clients.py
   └── Update literature.py
   └── Test

2. Feature 2: Chat with PDF (independent)
   └── Create pdf_processor/processor.py
   └── Create langchain_chains/rag_chain.py
   └── Update chat.py imports
   └── Enable router
   └── Test

3. Feature 3: Citation Booster (after Feature 1)
   └── Test only (no code changes)

4. Feature 4: Data Extraction (independent)
   └── Implement extraction logic
   └── Enable router
   └── Test

5. Enable remaining routers
   └── chat router
   └── data_extraction router
   └── ai_detector router

6. Deploy
   └── git commit
   └── railway up
```

## Do Not Modify
These features are WORKING. Do not change unless explicitly broken:
- ai_writer.py
- deep_review.py
- paraphraser.py
- systematic_review.py
- ai_detector.py
- topics.py
- payments.py
- citations.py

## Testing Commands

```bash
# Literature Search
curl -X POST http://localhost:8000/api/literature/search \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning healthcare", "sources": ["arxiv", "pubmed"]}'

# Chat with PDF (upload first, then chat)
curl -X POST http://localhost:8000/api/chat/upload \
  -F "file=@test.pdf"

curl -X POST http://localhost:8000/api/chat/chat \
  -H "Content-Type: application/json" \
  -d '{"document_id": "xxx", "question": "What is the main finding?"}'

# Data Extraction
curl -X POST http://localhost:8000/api/data-extraction/extract-tables \
  -F "file=@test.pdf"
```
