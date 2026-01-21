# Project Structure

```
/Users/shaileshsingh/V1 draft/
├── ULTIMATE_BUILD_DIRECTIVE.md    # Master directive
├── SESSION_MEMORY.md               # Context recovery
├── SPEC_DRIVEN_PLAN.md           # 15-week roadmap
├── client/                       # Next.js frontend
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── public/
├── server/                       # FastAPI backend
│   ├── app/
│   │   ├── api/                 # API endpoints
│   │   ├── core/                # Core functionality
│   │   ├── models/              # Pydantic models
│   │   └── services/            # Business logic
│   ├── pdf_processor/            # PDF processing
│   ├── vector_store/             # Vector search
│   ├── langchain_chains/         # AI chains
│   └── main.py                # FastAPI app
└── venv/                        # Python virtual environment
```

## Parallel Development Status

### Phase 1: Foundation (Week 2-3) - SEQUENTIAL ✅
- [x] Frontend scaffold created (Next.js)
- [x] Backend scaffold created (FastAPI)
- [ ] Supabase setup
- [ ] Railway deployment
- [ ] Payment integration (Paddle + Razorpay)
- [ ] Auth setup (Supabase Auth)

### Phase 2-6: PARALLEL SPRINT (Week 4-7) - 5 INDEPENDENT FEATURES

#### Agent A: Chat with PDF ⏳
- [ ] PDF upload endpoint
- [ ] PDF processing (Unstructured + PDFPlumber)
- [ ] Text chunking (500-1000 tokens)
- [ ] Embedding generation (OpenAI)
- [ ] Vector storage (Supabase pgvector)
- [ ] RAG chain (LangChain)
- [ ] Chat UI (real-time streaming)
- [ ] Source citation

#### Agent B: Literature Search ⏳
- [ ] paper-search-mcp integration (7 databases)
- [ ] pubmed-mcp-server integration (PubMed advanced)
- [ ] Multi-source aggregator
- [ ] Result deduplication
- [ ] Citation export (BibTeX, RIS, APA, MLA)
- [ ] Search history
- [ ] Save to library

#### Agent C: Citation Generator ⏳
- [ ] Citation input form (auto-fetch from DOI)
- [ ] 20+ citation styles (Citation Style Language)
- [ ] Batch citation generation
- [ ] Bibliography management
- [ ] Export to multiple formats

#### Agent D: Data Extraction ⏳
- [ ] Table extraction (PDFPlumber + Camelot)
- [ ] Figure detection
- [ ] Caption extraction
- [ ] CSV/Excel export
- [ ] Metadata preservation

#### Agent E: AI Detector ⏳
- [ ] Text input/upload
- [ ] AI probability score
- [ ] Highlighting (AI vs human sections)
- [ ] Document-level analysis
- [ ] Confidence metrics
