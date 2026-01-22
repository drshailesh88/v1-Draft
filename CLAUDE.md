# V1 DRAFT - PROJECT DIRECTIVES FOR CLAUDE

## CRITICAL: READ THIS FIRST

This is an **academic research platform** called "V1 Draft".
- **Live URL**: https://v1-draft-production.up.railway.app
- **GitHub**: https://github.com/drshailesh88/v1-Draft
- **Status**: 80% complete - 4 features need fixing

---

## PROJECT OVERVIEW

### What This Project Does
A SaaS platform for academic researchers to:
1. Search papers across arXiv, PubMed, Semantic Scholar
2. Chat with uploaded PDFs using AI (RAG)
3. Write research papers with AI assistance
4. Generate citations in APA/MLA/Chicago formats
5. Conduct systematic reviews with PRISMA diagrams
6. Detect AI-generated content
7. Find research topics
8. Paraphrase text while preserving citations
9. Boost citations with relevant paper suggestions
10. Deep review papers with multi-agent analysis
11. Handle payments (Paddle for USD, Razorpay for INR)

### Tech Stack
- **Frontend**: Next.js 16, React 19, Tailwind CSS, TypeScript
- **Backend**: FastAPI, Python 3.11, LangChain
- **Database**: Supabase (PostgreSQL + pgvector)
- **Deployment**: Railway
- **AI**: OpenAI GPT-4, text-embedding-3-small

---

## CURRENT STATUS

### WORKING FEATURES (8/12) - DO NOT MODIFY
| Feature | Backend File | Status |
|---------|-------------|--------|
| AI Writer | `server/app/api/ai_writer.py` | PRODUCTION READY |
| Deep Review | `server/app/api/deep_review.py` | PRODUCTION READY |
| Paraphraser | `server/app/api/paraphraser.py` | PRODUCTION READY |
| Systematic Review | `server/app/api/systematic_review.py` | PRODUCTION READY |
| AI Detector | `server/app/api/ai_detector.py` | PRODUCTION READY |
| Topic Discovery | `server/app/api/topics.py` | PRODUCTION READY |
| Payments | `server/app/api/payments.py` | PRODUCTION READY |
| Citations | `server/app/api/citations.py` | PRODUCTION READY |

### BROKEN FEATURES (4/12) - THESE NEED FIXING
| Feature | Problem | Priority | Solution |
|---------|---------|----------|----------|
| Literature Search | MCP integration broken | HIGH | Use direct Python libraries |
| Chat with PDF | Missing modules | HIGH | Create pdf_processor & langchain_chains |
| Citation Booster | Depends on Literature Search | MEDIUM | Fix Literature Search first |
| Data Extraction | Only placeholder code | LOW | Implement with pdfplumber |

---

## WHAT NEEDS TO BE DONE

### TASK 1: FIX LITERATURE SEARCH (HIGH PRIORITY)

**Problem**: The MCP (Model Context Protocol) integration doesn't work.

**Solution**: Replace MCP with direct Python library calls.

**Steps**:
1. Create file: `server/core/literature_clients.py`
2. Implement three classes:
   - `ArxivClient` using `arxiv` library
   - `PubMedClient` using `biopython` (Bio.Entrez)
   - `SemanticScholarClient` using `semanticscholar` library
3. Update `server/app/api/literature.py`:
   - Remove lines 60-120 (MCP code)
   - Import from `literature_clients.py`
   - Call each client based on requested sources

**Libraries** (already in requirements.txt):
```
arxiv>=2.1.0
biopython>=1.83
semanticscholar>=0.8.0
```

**Test Command**:
```bash
curl -X POST http://localhost:8000/api/literature/search \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning", "sources": ["arxiv", "pubmed"]}'
```

---

### TASK 2: FIX CHAT WITH PDF (HIGH PRIORITY)

**Problem**: `server/app/api/chat.py` imports modules that don't exist:
- `from pdf_processor import process_pdf` (file doesn't exist)
- `from langchain_chains import rag_chain` (file doesn't exist)

**Solution**: Create these modules.

**Steps**:
1. Create file: `server/pdf_processor/processor.py`
   - Function `extract_text_from_pdf(file_path)` using pdfplumber
   - Function `chunk_text(text, chunk_size=1000, overlap=200)`
   - Function `process_pdf(file_path)` that combines both

2. Create file: `server/langchain_chains/rag_chain.py`
   - Function `get_embeddings(texts)` using OpenAI
   - Function `find_similar_chunks(query, chunks, embeddings)`
   - Function `answer_question(question, context_chunks)` using GPT-4

3. Update `server/app/api/chat.py` imports

4. Uncomment router in `server/main.py` line 65

**Libraries**: Already installed (pdfplumber, openai)

**Test Command**:
```bash
# Upload PDF
curl -X POST http://localhost:8000/api/chat/upload -F "file=@paper.pdf"

# Chat with it
curl -X POST http://localhost:8000/api/chat/chat \
  -H "Content-Type: application/json" \
  -d '{"document_id": "xxx", "question": "What is the main finding?"}'
```

---

### TASK 3: VERIFY CITATION BOOSTER (MEDIUM PRIORITY)

**Problem**: Depends on Literature Search working.

**Solution**: Once Task 1 is done, Citation Booster should work automatically.

**Steps**:
1. Complete Task 1 first
2. Test Citation Booster endpoint

**Test Command**:
```bash
curl -X POST http://localhost:8000/api/citation-booster/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Machine learning has revolutionized healthcare..."}'
```

---

### TASK 4: IMPLEMENT DATA EXTRACTION (LOW PRIORITY)

**Problem**: `server/app/api/data_extraction.py` has only placeholder code.

**Solution**: Implement real table extraction using pdfplumber.

**Steps**:
1. Update `server/app/api/data_extraction.py`:
   - Implement `extract_tables()` using pdfplumber
   - Implement `export_csv()` using pandas
   - Implement `export_excel()` using openpyxl

2. Uncomment router in `server/main.py` line 79

**Libraries**: Already installed (pdfplumber, pandas, openpyxl)

---

### TASK 5: ENABLE REMAINING ROUTERS

After Tasks 1-4, update `server/main.py`:

```python
# Uncomment these lines:
from app.api import chat
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])

from app.api import data_extraction
app.include_router(data_extraction.router, prefix="/api/data-extraction", tags=["data-extraction"])
```

---

## FILE STRUCTURE

```
V1 draft/
├── server/                          # FastAPI Backend
│   ├── main.py                      # Entry point - routers registered here
│   ├── requirements.txt             # Python dependencies
│   ├── app/api/                     # All API endpoints
│   │   ├── literature.py            # TASK 1: Fix this
│   │   ├── chat.py                  # TASK 2: Fix imports
│   │   ├── citation_booster.py      # TASK 3: Verify after Task 1
│   │   ├── data_extraction.py       # TASK 4: Implement this
│   │   ├── ai_writer.py             # WORKING
│   │   ├── deep_review.py           # WORKING
│   │   ├── paraphraser.py           # WORKING
│   │   ├── systematic_review.py     # WORKING
│   │   ├── ai_detector.py           # WORKING
│   │   ├── topics.py                # WORKING
│   │   ├── payments.py              # WORKING
│   │   └── citations.py             # WORKING
│   ├── core/
│   │   ├── database.py              # Supabase client (WORKING)
│   │   ├── openai_client.py         # OpenAI client (WORKING)
│   │   └── literature_clients.py    # TASK 1: CREATE THIS
│   ├── pdf_processor/
│   │   └── processor.py             # TASK 2: CREATE THIS
│   └── langchain_chains/
│       └── rag_chain.py             # TASK 2: CREATE THIS
│
├── client/                          # Next.js Frontend
│   └── src/app/                     # All pages exist and are connected
│
├── MASTER_BUILD_PLAN.md             # Detailed implementation guide
├── .specify/specs/                  # Speckit specifications
└── .env                             # Environment variables (DO NOT COMMIT)
```

---

## HOW TO DEVELOP

### Local Development
```bash
# Backend
cd server
source ../venv/bin/activate
pip install -r requirements.txt
python main.py
# Runs on http://localhost:8000

# Frontend
cd client
npm install
npm run dev
# Runs on http://localhost:3000
```

### Deploy to Railway
```bash
cd "/Users/shaileshsingh/V1 draft"
git add -A
git commit -m "fix: Description of changes"
railway up
```

---

## ENVIRONMENT VARIABLES

Already configured in Railway. For local development:
```
SUPABASE_URL=https://qmtilfljwlixgcucwprs.supabase.co
SUPABASE_ANON_KEY=<set in Railway>
SUPABASE_SERVICE_ROLE_KEY=<set in Railway>
OPENAI_API_KEY=<set in Railway>
```

---

## IMPORTANT RULES

1. **DO NOT** modify working features unless explicitly broken
2. **DO NOT** change database schema without migration
3. **DO** test each feature after implementing
4. **DO** commit after each task
5. **DO** use MIT/Apache licensed libraries only
6. **DO** read MASTER_BUILD_PLAN.md for detailed code examples

---

## IMPLEMENTATION CHECKLIST

- [ ] TASK 1: Create `server/core/literature_clients.py`
- [ ] TASK 1: Update `server/app/api/literature.py`
- [ ] TASK 1: Test literature search
- [ ] TASK 2: Create `server/pdf_processor/processor.py`
- [ ] TASK 2: Create `server/langchain_chains/rag_chain.py`
- [ ] TASK 2: Enable chat router in main.py
- [ ] TASK 2: Test chat with PDF
- [ ] TASK 3: Verify citation booster works
- [ ] TASK 4: Implement data extraction
- [ ] TASK 4: Enable data_extraction router
- [ ] TASK 5: Deploy to Railway
- [ ] TASK 5: Verify all endpoints work in production

---

## QUICK REFERENCE

### API Endpoints (Production)
- Health: https://v1-draft-production.up.railway.app/health
- Docs: https://v1-draft-production.up.railway.app/docs

### GitHub Repository
https://github.com/drshailesh88/v1-Draft

### Railway Dashboard
https://railway.com/project/88e553b1-36e3-461a-8ec0-6c9cda9efb73

---

## SPECKIT WORKFLOW

This project uses **Spec-Driven Development** with Speckit.

### Available Commands
```
/speckit.specify    - Define feature requirements
/speckit.plan       - Create technical implementation plan
/speckit.tasks      - Generate task list from plan
/speckit.implement  - Execute the implementation
/speckit.analyze    - Verify cross-artifact consistency
/speckit.checklist  - Generate testing checklist
```

### Project Files
```
.specify/
├── memory/
│   └── constitution.md     # Project principles and rules
├── specs/
│   └── implementation-plan.md  # Current feature specs
└── templates/              # Speckit templates
```

### Workflow for New Features
1. Run `/speckit.specify` to define requirements
2. Run `/speckit.plan` to create technical plan
3. Run `/speckit.tasks` to generate task list
4. Implement each task following MASTER_BUILD_PLAN.md
5. Run `/speckit.analyze` to verify consistency
6. Deploy with `railway up`

### Current Spec Status
- **implementation-plan.md**: Defines 4 features to fix
- **constitution.md**: Project principles established

---

## KEY DOCUMENTS (READ IN ORDER)

1. **CLAUDE.md** (this file) - Project directives
2. **STATUS.md** - Quick status overview
3. **MASTER_BUILD_PLAN.md** - Detailed implementation with code
4. **.specify/specs/implementation-plan.md** - Speckit format specs
5. **.specify/memory/constitution.md** - Project principles

---

**Last Updated**: 2026-01-22
**Status**: 4 tasks remaining to complete
**Next Action**: Start with TASK 1 (Literature Search)
**Development Mode**: Spec-Driven with Speckit
