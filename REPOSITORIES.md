# PROVEN GITHUB REPOSITORIES FOR SCISPACE CLONE

## Development Methodology & Testing Tools (CRITICAL)

### 0. spec-kit - MIT License ✅
**URL**: https://github.com/github/spec-kit
**Stars**: 64k+
**Use**: Spec-driven development toolkit
**Key Features**:
- Intent-driven development (specifications define "what" before "how")
- Rich specification creation with guardrails
- Multi-step refinement (not one-shot code generation)
- Context preservation across sessions
- Reproducible development process
**Commands**:
```bash
specify init . --ai claude
/speckit.constitution  # Create project principles
/speckit.specify       # Define requirements
/speckit.plan           # Create technical plan
/speckit.tasks          # Generate tasks
/speckit.implement      # Execute implementation
```

### 1. agent-browser - Apache 2.0 License ✅
**URL**: https://github.com/vercel-labs/agent-browser
**Stars**: 9k+
**Use**: Browser automation CLI for E2E testing
**Key Features**:
- Fast Rust CLI with Node.js fallback
- Snapshot-based element selection (@e1, @e2 refs)
- Semantic locators (role, text, label)
- Support for forms, uploads, screenshots
- Perfect for simulating Dr. Chen's workflows
**Commands**:
```bash
agent-browser open http://localhost:3000
agent-browser snapshot -i --json
agent-browser click @e2
agent-browser fill @e3 "test@example.com"
agent-browser screenshot test.png
```

### 2. ralph-loop - Open Source ✅
**URL**: https://github.com/anthropics/claude-plugins-official/tree/main/plugins/ralph-loop
**Use**: Ralph Loop methodology plugin for Claude
**Key Features**:
- Test → Find Problem → Fix → Test Again → Exit When Complete
- Iterative refinement based on testing results
- Quality gates before moving forward
- Never abandon features, fix until they work

## MCP Servers (Model Context Protocol)

### 3. paper-search-mcp - MIT License ✅
**URL**: https://github.com/openags/paper-search-mcp
**Stars**: 550+
**Use**: Multi-source academic paper search
**Key Features**:
- **7+ Academic Databases**: arXiv, PubMed, bioRxiv, medRxiv, Google Scholar, IACR, Semantic Scholar
- Standardized output format via `Paper` class
- Asynchronous tools for efficient network requests
- MCP integration for seamless LLM context
- Extensible design for adding new platforms
**Tools**:
- `search_arxiv` - Search and download from arXiv
- `search_pubmed` - Search PubMed via NCBI
- `search_scholar` - Search Google Scholar
- `search_semantic_scholar` - Search Semantic Scholar
- `search_biorxiv` - Search bioRxiv preprints
- `search_medrxiv` - Search medRxiv preprints
- `search_iacr` - Search IACR ePrint Archive
**Why Use**: Already aggregates 7+ databases, saves 6+ months of integration work

### 4. pubmed-mcp-server - Apache 2.0 License ✅
**URL**: https://github.com/cyanheads/pubmed-mcp-server
**Stars**: 46+
**Use**: PubMed-specific advanced search and analysis
**Key Features**:
- Production-grade MCP server with robust NCBI E-utilities
- Advanced search capabilities (date ranges, publication types, MeSH terms, author filters)
- Full article metadata (abstracts, authors, affiliations, journal info, DOIs, citations)
- Citation network analysis (related articles, citing articles, references)
- Research planning and workflow generation
- Data visualization (PNG charts from publication data)
- Multiple output formats (JSON, MEDLINE, XML, RIS, BibTeX, APA, MLA)
- Batch processing with pagination support
**Tools**:
- `pubmed_search_articles` - Search with queries, filters, date ranges
- `pubmed_fetch_contents` - Fetch detailed article info (PMIDs, metadata, abstracts)
- `pubmed_article_connections` - Find related/citing papers, format citations
- `pubmed_research_agent` - Generate structured research plans
- `pubmed_generate_chart` - Create charts from publication data
**Why Use**: Production-grade implementation with advanced features beyond basic search

### 5. claude-scientific-skills - MIT License ✅
**URL**: https://github.com/K-Dense-AI/claude-scientific-skills
**Stars**: 6.7k+
**Use**: 140+ ready-to-use scientific skills
**Key Features**:
- **28+ Scientific Databases**: OpenAlex, PubMed, bioRxiv, ChEMBL, UniProt, COSMIC, ClinicalTrials.gov
- **55+ Python Packages**: RDKit, Scanpy, PyTorch Lightning, scikit-learn, BioPython, BioServices, PennyLane, Qiskit
- **15+ Scientific Integrations**: Benchling, DNAnexus, LatchBio, OMERO, Protocols.io
- **30+ Analysis & Communication Tools**: Literature review, scientific writing, peer review, document processing
- **10+ Research & Clinical Tools**: Hypothesis generation, grant writing, clinical decision support
- Installation via Claude Code plugin or MCP server
- Comprehensive documentation with examples
**Categories**:
- Bioinformatics & Genomics (16+ skills)
- Cheminformatics & Drug Discovery (11+ skills)
- Proteomics & Mass Spectrometry (2 skills)
- Clinical Research & Precision Medicine (12+ skills)
- Machine Learning & AI (15+ skills)
- Scientific Databases (28+ skills)
- Scientific Communication (20+ skills)
**Why Use**: Pre-built, tested scientific workflows accelerates development significantly

## PDF Processing & RAG (Chat with PDF)

### 1. LangChain - MIT License ✅
**URL**: https://github.com/langchain-ai/langchain
**Stars**: 125k+
**Use**: PDF loading, document processing, RAG chains, embeddings
**Key Features**:
- PDF document loaders (PyPDF, PDFMiner)
- Vector store integrations (Pinecone, Weaviate, Chroma)
- RAG chains for document Q&A
- Text splitters for chunking

### 2. LlamaIndex - Apache 2.0 License ✅
**URL**: https://github.com/run-llama/llama_index
**Stars**: 37k+
**Use**: Document indexing, retrieval, query engine
**Key Features**:
- Vector database integration
- Hybrid search (semantic + keyword)
- Document storage and retrieval
- Query optimization

### 3. PDFPlumber - MIT License ✅
**URL**: https://github.com/jsvine/pdfplumber
**Stars**: 5.5k+
**Use**: Extract text, tables, figures from PDFs
**Key Features**:
- Table extraction with precise coordinates
- Visual debugging
- Support for complex layouts
- Export to CSV/JSON

### 4. PyMuPDF - AGPL-3.0 License (Free for non-commercial) ⚠️
**URL**: https://github.com/pymupdf/python-fitz
**Stars**: 4.8k+
**Use**: Fast PDF parsing, text extraction
**Note**: Consider commercial license if selling

### 5. Unstructured.io - Apache 2.0 License ✅
**URL**: https://github.com/Unstructured-IO/unstructured
**Stars**: 10k+
**Use**: Parse documents from multiple formats
**Key Features**:
- Support for PDF, DOCX, HTML, TXT
- Extract elements (tables, headers, lists)
- Table extraction
- Clean structured output

## Literature Search APIs

### 6. Entrez Direct (EDirect) - Public Domain ✅
**URL**: https://github.com/ncbi/edirect
**Stars**: 1.8k+
**Use**: PubMed API integration
**Key Features**:
- Direct access to PubMed database
- Search and retrieve papers
- Citation metadata
- Full-text access (where available)

### 7. Scholarly - MIT License ✅
**URL**: https://github.com/scholarly-python-package/scholarly
**Stars**: 3.5k+
**Use**: Google Scholar scraping
**Key Features**:
- Search papers by author, title, keyword
- Extract citation metrics
- Publication details
- Author profiles

### 8. arxiv.py - MIT License ✅
**URL**: https://github.com/lukasschwab/arxiv.py
**Stars**: 2.1k+
**Use**: ArXiv API wrapper
**Key Features**:
- Query ArXiv database
- Download papers
- Metadata extraction
- Search by category, author, keywords

### 9. Semantic Scholar API - MIT License ✅
**URL**: https://github.com/allenai/semanticscholar
**Stars**: 1.2k+
**Use**: Academic paper search
**Key Features**:
- Access 200M+ papers
- Citation graphs
- Influence measures
- Related papers

## Citation Management

### 10. Citation Style Language (CSL) - CC-BY-SA 4.0 ✅
**URL**: https://github.com/citation-style-language/styles
**Stars**: 4.1k+
**Use**: Citation style definitions
**Key Features**:
- 9000+ citation styles
- APA, MLA, Chicago, IEEE, Harvard
- Standardized format
- Widely used in academia

### 11. pandoc - GPL-2.0+ License ✅
**URL**: https://github.com/jgm/pandoc
**Stars**: 32k+
**Use**: Document conversion and citation processing
**Key Features**:
- Convert between formats (Markdown, LaTeX, Word)
- Process citations with pandoc-citeproc
- Bibliography generation

### 12. biblatex-parser - MIT License ✅
**URL**: https://github.com/sciunto-org/python-bibtexparser
**Stars**: 1.2k+
**Use**: BibTeX file parsing
**Key Features**:
- Parse BibTeX files
- Write BibTeX
- Validate citations
- Format conversion

## AI Writing & Content Generation

### 13. LangChain (Reuse from #1)
**Use**: Writing chains, content generation chains
**Templates**:
- Academic paper writing chains
- Section-by-section generation
- Paraphrasing chains
- Style adaptation

### 14. AutoGen - MIT License ✅
**URL**: https://github.com/microsoft/autogen
**Stars**: 32k+
**Use**: Multi-agent writing assistance
**Key Features**:
- Multiple agents collaborate
- Human-in-the-loop
- Drafting and editing workflow
- Academic writing templates

### 15. Guidance - Apache 2.0 License ✅
**URL**: https://github.com/guidance-ai/guidance
**Stars**: 18k+
**Use**: Controlled text generation
**Key Features**:
- Structure-aware generation
- Academic templates
- Citation injection
- Format constraints

## Data Extraction & Analysis

### 16. Tabula - MIT License ✅
**URL**: https://github.com/tabulapdf/tabula
**Stars**: 14k+
**Use**: Extract tables from PDFs
**Key Features**:
- GUI and CLI
- Batch extraction
- CSV/JSON export
- Automatic table detection

### 17. Camelot - MIT License ✅
**URL**: https://github.com/socialcopsdev/camelot
**Stars**: 4.6k+
**Use**: Complex table extraction from PDFs
**Key Features**:
- Stream and Lattice extraction
- Export to CSV, Excel, JSON
- Table quality scores
- Visual debugging

### 18. PyMuPDF Tables - AGPL-3.0 ⚠️
**URL**: Part of PyMuPDF (#4 above)
**Use**: High-performance table extraction

## Content Analysis & AI Detection

### 19. OpenAI Cookbooks - MIT License ✅
**URL**: https://github.com/openai/openai-cookbook
**Stars**: 53k+
**Use**: Content analysis examples
**Key Features**:
- Text classification
- Sentiment analysis
- Similarity scoring
- Plagiarism detection patterns

### 20. Transformers - Apache 2.0 License ✅
**URL**: https://github.com/huggingface/transformers
**Stars**: 134k+
**Use**: Pre-trained models for analysis
**Key Features**:
- BERT/RoBERTa for text analysis
- Classification models
- Named entity recognition
- Zero-shot classification

### 21. GPTZero Open - Custom (Free tier) ✅
**URL**: https://github.com/GPTZero-Official/gptzero-detection-api
**Use**: AI content detection API
**Note**: Free tier available, paid for commercial use

## Vector Databases (Essential for RAG)

### 22. Pinecone - Commercial with Free Tier ✅
**URL**: https://github.com/pinecone-io/pinecone-ts-client
**Use**: Vector search
**Free Tier**: 1 index, 1M vectors
**Production**: Scales easily

### 23. Weaviate - BSD-3-Clause License ✅
**URL**: https://github.com/weaviate/weaviate
**Stars**: 10k+
**Use**: Open-source vector database
**Key Features**:
- Self-hosted option
- GraphQL and REST API
- Hybrid search
- Multi-modal support

### 24. ChromaDB - Apache 2.0 License ✅
**URL**: https://github.com/chroma-core/chroma
**Stars**: 12k+
**Use**: Lightweight vector database
**Key Features**:
- Easy to set up
- Python/JS clients
- Persistent storage
- Good for MVP

## Frontend Framework

### 25. Next.js 14 - MIT License ✅
**URL**: https://github.com/vercel/next.js
**Stars**: 121k+
**Use**: React framework for frontend
**Key Features**:
- App Router
- Server Components
- API Routes
- Built-in optimization

### 26. shadcn/ui - MIT License ✅
**URL**: https://github.com/shadcn-ui/ui
**Stars**: 71k+
**Use**: UI component library
**Key Features**:
- Beautiful components
- Tailwind CSS based
- Accessible
- Customizable

### 27. TanStack Table - MIT License ✅
**URL**: https://github.com/TanStack/table
**Stars**: 23k+
**Use**: Data tables for paper listings
**Key Features**:
- Virtual scrolling
- Sorting, filtering
- Pagination
- Server-side support

## Backend & APIs

### 28. FastAPI - MIT License ✅
**URL**: https://github.com/tiangolo/fastapi
**Stars**: 77k+
**Use**: Python backend framework
**Key Features**:
- Fast async
- Automatic docs (Swagger)
- Type hints
- Easy deployment

### 29. pgvector - PostgreSQL Extension - PostgreSQL License ✅
**URL**: https://github.com/pgvector/pgvector
**Stars**: 11k+
**Use**: Vector similarity search in Postgres
**Key Features**:
- Native Postgres integration
- No separate vector DB needed
- ACID compliance
- Easy scaling

### 30. Stripe SDK - MIT License ✅
**URL**: https://github.com/stripe/stripe-python
**Stars**: 5.7k+
**Use**: Payment processing
**Key Features**:
- Subscriptions
- Invoicing
- Webhooks
- Tax handling

## Authentication & User Management

### 31. Clerk - MIT License ✅
**URL**: https://github.com/clerk/javascript
**Stars**: 8.4k+
**Use**: Authentication
**Key Features**:
- OAuth (Google, GitHub, etc.)
- Email/password
- MFA support
- User management

### 32. Supabase - Apache 2.0 License ✅
**URL**: https://github.com/supabase/supabase
**Stars**: 69k+
**Use**: Firebase alternative with Postgres
**Key Features**:
- Auth included
- Real-time database
- Storage
- Edge functions

## Monitoring & Analytics

### 33. LangSmith - Commercial with Free Tier ✅
**URL**: https://github.com/langchain-ai/langsmith-sdk
**Use**: LLM app monitoring and debugging
**Free Tier**: 1,000 traces/month
**Key Features**:
- Track LLM calls
- Debug chains
- Evaluate performance
- A/B testing

### 34. Vercel Analytics - Commercial ✅
**URL**: https://github.com/vercel/analytics
**Use**: Web analytics
**Key Features**:
- Real-time insights
- Performance monitoring
- User behavior
- Conversion tracking

## Deployment

### 35. Docker - Apache 2.0 License ✅
**URL**: https://github.com/docker
**Stars**: N/A (Docker Hub)
**Use**: Containerization

### 36. Railway - Commercial ✅
**URL**: https://github.com/railwayapp
**Use**: Easy deployment platform
**Free Tier**: $5/month credit
**Key Features**:
- One-click deploy
- Built-in Postgres
- Preview environments
- Git integration

## SUMMARY OF LICENSES

### ✅ Fully Free & Permissive (MIT, Apache 2.0, BSD)
- LangChain, LlamaIndex, PDFPlumber, Scholarly, arxiv.py
- Next.js, FastAPI, shadcn/ui, TanStack Table
- ChromaDB, Weaviate, pgvector
- Clerk, Supabase
- AutoGen, Guidance, Transformers

### ⚠️ Commercial/Free Tier Only
- Pinecone (SaaS with free tier)
- LangSmith (SaaS with free tier)
- Stripe (SaaS with transaction fees)
- GPTZero (SaaS with free tier)

### ❌ Avoid for Commercial Use
- PyMuPDF (AGPL requires source disclosure)

## RECOMMENDED STACK FOR MVP

### Frontend
- Next.js 14 (App Router)
- shadcn/ui (components)
- Tailwind CSS
- TanStack Table (data tables)

### Backend
- FastAPI (Python)
- LangChain (AI orchestration)
- LlamaIndex (document indexing)

### Database
- PostgreSQL + pgvector (vector search)

### AI/ML
- OpenAI GPT-4 / Claude 3.5 Sonnet
- LangChain chains
- Document loaders (PDFPlumber, Unstructured)

### APIs Integration
- PubMed (EDirect)
- Google Scholar (Scholarly)
- ArXiv (arxiv.py)

### Authentication
- Clerk or Supabase Auth

### Payments
- Stripe

### Deployment
- Docker + Railway/Vercel
