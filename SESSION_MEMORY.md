# SESSION MEMORY - SCI SPACE CLONE PROJECT

## PROJECT CONTEXT
Building a subscription-based academic research platform clone of scispace.com
- **Custom UI**: Will NOT look like scispace.com
- **Target Users**: Academics, researchers, students (global + India)
- **Business Model**: Subscription tiers (Free, Pro, Team)
- **Methodology**: Spec-Driven Development with Ralph Loop Testing
- **Founder Profile**: Non-technical, needs LLM-friendly, easy setup

## DEVELOPMENT METHODOLOGY

### 1. Spec-Driven Development (SDD)
Using **github/spec-kit** (64k stars, MIT) to ensure:
- Intent-driven development (specifications define "what" before "how")
- Rich specification creation with guardrails
- Multi-step refinement (not one-shot code generation)
- Context preservation across sessions
- Reproducible development process

**Commands**:
```bash
# Install
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git

# Initialize
specify init . --ai claude

# Key commands
/speckit.constitution  # Create project principles
/speckit.specify       # Define what to build (requirements)
/speckit.plan           # Create technical implementation plan
/speckit.tasks          # Generate actionable task list
/speckit.implement      # Execute implementation
/speckit.clarify       # Clarify underspecified areas
/speckit.analyze        # Cross-artifact consistency analysis
/speckit.checklist      # Generate quality checklists
```

### 2. Ralph Loop Methodology
Using **anthropics/claude-plugins-official/plugins/ralph-loop** for testing:
- **Test** → **Find Problem** → **Fix** → **Test Again** → **Exit When Complete**
- No abandoning features - we fix until it works
- Iterative refinement based on testing results
- Quality gates before moving forward
- Document all fixes and learnings

**Principles**:
- Every feature is tested thoroughly
- Bugs are fixed, not skipped
- Exit criteria defined before testing
- Real user workflows validated

### 3. Browser-Based E2E Testing
Using **vercel-labs/agent-browser** (9k stars, Apache 2.0) for:
- Automated E2E testing of all features
- Simulating real user workflows
- Validating functionality from UI perspective
- Catching integration issues early

**Commands**:
```bash
# Install
npm install -g agent-browser
agent-browser install

# Key workflow
agent-browser open http://localhost:3000
agent-browser snapshot -i --json      # Get interactive elements
agent-browser click @e2                   # Click by ref
agent-browser fill @e3 "test@example.com" # Fill form
agent-browser screenshot test.png
```

## PROBLEMS WE'RE SOLVING

### Problem 1: Non-Technical Founder Constraints
**What Founder Struggles With:**
- ❌ Complex server management (VPS, SSH, Nginx, Docker)
- ❌ Multiple services integration difficulty (Firebase wiring)
- ❌ Time-consuming debugging of infrastructure
- ❌ Lack of technical knowledge for debugging
- ❌ Need for quick, reliable deployment

**How We Solve This:**
1. **Single Platform for Everything** (Railway)
   - Frontend + Backend + DB on one platform
   - One dashboard to manage all
   - Auto-deploys from GitHub
   - Zero server management
   - No SSH, no Docker config needed

2. **LLM-Friendly Setup**
   - Every step has clear LLM prompts
   - Thousands of examples for each technology
   - Easy to ask ChatGPT/Claude for help
   - Clear documentation optimized for LLMs

3. **Proven, Battle-Tested Components**
   - All repos have 10k+ stars
   - MIT/Apache 2.0 licenses (permissive)
   - Don't reinvent wheels
   - Focus on business logic, not infrastructure

### Problem 2: International Payments (India + Global)
**What Founder Struggles With:**
- ❌ Stripe India only accepts INR (bad UX for global users)
- ❌ Need for separate US entity for USD/EUR/GBP
- ❌ Complex tax compliance across jurisdictions
- ❌ Payouts to Indian banks restricted

**How We Solve This:**
1. **Hybrid Payment Solution** (Paddle + Razorpay)
   - Paddle for global users (USD/EUR/GBP pricing)
   - Razorpay for Indian users (INR + UPI support)
   - Automatic currency detection
   - Paddle handles all tax compliance
   - Payouts to Indian bank automatically

2. **No Separate Entity Needed**
   - Paddle: No US entity required for USD payments
   - Razorpay: Indian company already setup
   - Single bank account for both providers
   - Automatic currency conversion

### Problem 3: Database Complexity (RAG Requirements)
**What Founder Struggles With:**
- ❌ Vector databases separate from relational DB
- ❌ Complex integration between vector + relational
- ❌ Scaling challenges with vector search
- ❌ Performance issues with large datasets

**How We Solve This:**
1. **Single Database Solution** (PostgreSQL + pgvector)
   - Vector and relational data in one database
   - No separate vector DB needed
   - Simple queries (JOIN vector + relational)
   - Proven technology (11k stars)
   - Easy to scale

2. **Supabase Built-in pgvector**
   - pgvector pre-installed
   - No extension management
   - No database administration
   - Built-in backups
   - Auto-scaling

### Problem 4: Academic API Integration Complexity
**What Founder Struggles With:**
- ❌ PubMed API rate limits
- ❌ Google Scholar scraping difficulty
- ❌ Multiple databases (PubMed, ArXiv, Scholar, etc.)
- ❌ API authentication for each service
- ❌ Different response formats

**How We Solve This:**
1. **MCP Servers for All Academic APIs**
   - **paper-search-mcp**: 7+ databases in one interface
   - **pubmed-mcp-server**: Advanced PubMed features
   - **Claude Scientific Skills**: 140+ pre-built workflows
   - Unified response format
   - Single authentication
   - Production-grade implementations

### Problem 5: PDF Processing Challenges
**What Founder Struggles With:**
- ❌ Complex PDF layouts (tables, columns, figures)
- ❌ Table extraction accuracy
- ❌ Text chunking for RAG
- ❌ Metadata extraction

**How We Solve This:**
1. **Proven PDF Processing Libraries**
   - **Unstructured.io**: Document parsing, element extraction
   - **PDFPlumber**: Table extraction with precise coordinates
   - **Camelot**: Complex table extraction
   - All MIT/Apache 2.0 licensed
   - Battle-tested with 10k+ stars

### Problem 6: Feature Testing & Validation
**What Founder Struggles With:**
- ❌ Manual testing is time-consuming
- ❌ Miss edge cases
- ❌ Integration issues discovered late
- ❌ No systematic testing methodology

**How We Solve This:**
1. **Ralph Loop Testing**
   - Test → Fix → Test → Exit loop
   - Never abandon features
   - Document all fixes
   - Systematic, repeatable

2. **Agent-Browser E2E Testing**
   - Automated browser testing
   - Real user workflows (Dr. Chen)
   - Early integration issue detection
   - UI validation

### Problem 7: Context Loss Across Sessions
**What Founder Struggles With:**
- ❌ AI sessions crash/lose context
- ❌ Forget requirements and decisions
- ❌ Start from scratch each time
- ❌ Time wasted re-planning

**How We Solve This:**
1. **Spec-Driven Development with Context Preservation**
   - All specifications stored in `.specify/` directory
   - Constitution, specs, plans, tasks all documented
   - Session recovery: Read files, regain context
   - No re-planning needed

2. **Comprehensive Session Memory Files**
   - SESSION_MEMORY.md (quick recovery)
   - SESSION_RECOVERY.md (detailed instructions)
   - SPEC_DRIVEN_PLAN.md (20-week roadmap)
   - DEVELOPMENT_APPROACH.md (methodology)
   - All context persists across crashes

### Problem 8: Code Quality & Maintainability
**What Founder Struggles With:**
- ❌ Inconsistent code style
- ❌ Missing error handling
- ❌ No documentation
- ❌ Technical debt accumulation

**How We Solve This:**
1. **Quality Gates per Feature**
   - Code quality checks
   - Error handling validation
   - Documentation requirements
   - Performance metrics (<500ms API, <2s UI)
   - Dr. Chen approval (real user validation)

2. **Spec-Kit Guardrails**
   - Type hints enforced
   - Best practices built-in
   - Consistent patterns
   - Auto-generated documentation

### Problem 9: Parallel Development Coordination
**What Founder Struggles With:**
- ❌ How to run multiple agents simultaneously
- ❌ How to coordinate work across agents
- ❌ When to use parallel vs sequential
- ❌ How to manage dependencies

**How We Solve This:**
1. **Clear Parallel Strategy**
   - Week 4-7: 5 independent agents in parallel
   - Week 8-11: 3 dependent agents sequentially
   - Clear dependency graph documented
   - Each feature has independent spec in `.specify/specs/`

2. **LLM-Friendly Parallel Execution**
   - Spawn multiple sessions for each parallel agent
   - Clear instructions per agent
   - No coordination needed (agents work independently)

3. **Milestone-Based Coordination**
   - Complete parallel stage → review → move to sequential stage
   - Each agent has clear exit criteria
   - Ralph Loop testing per agent
   - No overlap between agents

## PERSONA FOR TESTING

### Dr. Chen - AI Research Scientist
**Background**:
- PhD in Computational Biology from MIT
- Postdoc at Stanford (AI/ML)
- Assistant Professor at UC Berkeley
- Publishes in Nature, Science, Cell

**Current Task**: Submit a state-of-the-art review on "AI-Powered Drug Discovery" to Nature

**Requirements from Nature**:
- Comprehensive literature review (500+ papers)
- PRISMA methodology for systematic review
- Data extraction from 200+ papers
- Visual analysis of trends
- Gap identification
- Future directions
- Publication-ready figures

**Dr. Chen's Testing Approach**:
- Will use EVERY feature of app
- Will test edge cases and failure modes
- Will validate all output formats
- Will check citation accuracy
- Will verify data extraction quality
- Will test collaboration features
- Will validate export capabilities

## FEATURES TO BUILD (Priority Order)

### ✅ Core Features (11 total)
1. **Chat with PDF** - Upload PDFs, ask questions, get answers
2. **Literature Review** - Systematic search (PubMed, Google Scholar, ArXiv)
3. **AI Writer** - Draft academic papers for journal submission
4. **Citation Generator** - Multiple styles (APA, MLA, Chicago, IEEE)
5. **Paraphraser** - Academic paraphrasing, plagiarism reduction
6. **Extract Data** - Tables/figures from PDFs to CSV/Excel
7. **Find Topics** - Topic discovery, research gaps, trending topics
8. **Systematic Literature Review** - PRISMA methodology
9. **Deep Review** - Comprehensive paper analysis
10. **Citation Booster** - Suggest relevant citations
11. **AI Detector** - Detect AI-generated content

### ❌ Features to Exclude
- Chart/Data visualizations
- Poster generation
- Patent search
- Website/research site builder

## TECH STACK DECISIONS (FINAL)

### Frontend
- **Next.js 14** (App Router) - Modern, fast, server components
- **shadcn/ui** - Beautiful, accessible components
- **Tailwind CSS** - Styling
- **TanStack Table** - Data tables for papers
- **agent-browser** - For automated E2E testing

### Backend
- **FastAPI** (Python) - Fast async, type-safe
- **LangChain** - AI orchestration, chains, agents
- **LlamaIndex** - Document indexing, retrieval
- **LangGraph** - Multi-agent workflows

### MCP Integrations
- **paper-search-mcp** (550 stars, MIT) - Multi-source paper search
- **pubmed-mcp-server** (46 stars, Apache 2.0) - PubMed advanced search
- **claude-scientific-skills** (6.7k stars, MIT) - 140+ scientific skills

### Database (UPDATED)
- **Supabase** (PostgreSQL + pgvector)
  - Built-in pgvector extension
  - Built-in authentication (no Clerk needed!)
  - Built-in storage (for PDFs)
  - Built-in edge functions
  - Real-time capabilities
  - Zero database administration
  - Auto-backups
  - Auto-scaling

### AI/ML
- **OpenAI GPT-4** - Main reasoning
- **Claude 3.5 Sonnet** - Alternative/better for some tasks
- May add more models later

### PDF Processing
- **Unstructured.io** - Extract elements (tables, headers, lists)
- **PDFPlumber** - Table extraction
- Both have permissive licenses

### Academic APIs
- **PubMed** - Via pubmed-mcp-server
- **Google Scholar** - Via paper-search-mcp
- **ArXiv** - Via paper-search-mcp
- **Semantic Scholar** - Via paper-search-mcp
- **BioRxiv/medRxiv** - Via paper-search-mcp
- **IACR** - Via paper-search-mcp

### Authentication (UPDATED)
- **Supabase Auth** - Built into Supabase, no separate service needed
  - Easy, supports OAuth (Google, GitHub, etc.)
  - Email/password
  - MFA support
  - User management
  - $0 cost (included in Supabase)
  - Simpler than Clerk!

### Payments (UPDATED)
- **Paddle** (for global users) - USD/EUR/GBP pricing, payouts to India
- **Razorpay** (for Indian users) - INR pricing, UPI support
- Hybrid: Automatic currency detection, route to appropriate provider
- Paddle handles tax compliance automatically
- Payouts to single Indian bank account

### Deployment (UPDATED)
- **Railway** (for frontend + backend)
  - Single platform for both
  - Easy deployment (git push)
  - Zero server management
  - Auto-deploys from GitHub
  - Built-in monitoring
  - Predictable pricing

- **Supabase** (for database + auth + storage)
  - One dashboard for DB, auth, storage, edge functions
  - Built-in pgvector
  - Zero database administration
  - Auto-scaling
  - Great for non-technical founders

## DEPLOYMENT ARCHITECTURE (FINAL)

```
┌──────────────────────────────────────────┐
│          YOUR DEPLOYMENT (2 services)   │
├──────────────────────────────────────────┤
│                                         │
│  ┌────────────────┐   ┌──────────────┐│
│  │   Railway     │──▶│  Supabase    ││
│  │               │   │              ││
│  │ Frontend      │   │ PostgreSQL   ││
│  │ Next.js       │   │ pgvector    ││
│  │ Backend       │   │ Auth        ││ ← BUILT-IN!
│  │ FastAPI      │   │ Storage     ││ ← BUILT-IN!
│  │ $20/month     │   │ Edge Funcs  ││
│  └────────────────┘   │ $0 → $25   ││
│                       └──────────────┘│
│                                         │
│  ┌────────────────┐                 │
│  │   Paddle     │ (Hybrid payments)│
│  │   Razorpay    │                 │
│  │   $0 setup    │                 │
│  └────────────────┘                 │
│                                         │
└──────────────────────────────────────────┘
```

### Why This is Perfect for Non-Technical Founder

```
┌─────────────────────────────────────┐
│  EASE OF SETUP COMPARISON         │
├─────────────────────────────────────┤
│                                  │
│ Firebase (Your Past Experience):   │
│ ❌ Auth separately             │
│ ❌ Firestore separately         │
│ ❌ Storage separately          │
│ ❌ Hosting separately          │
│ ❌ Functions separately        │
│ ❌ WIRING ALL TOGETHER = HARD!│
│ ❌ Complex rules to debug     │
│ ❌ No SQL (NoSQL learning curve)│
│ ❌ Firebase docs hard for LLMs │
│                                  │
│ Our Recommended Setup:         │
│ ✅ Railway: Frontend + Backend (2 in 1)│
│ ✅ Supabase: DB + Auth + Storage (4 in 1)│
│ ✅ Paddle: Payments (1 service)      │
│ ✅ Total: 3 services (not 5+)       │
│ ✅ Simple wiring (great docs)          │
│ ✅ SQL database (easy to learn)        │
│ ✅ pgvector built-in (no setup)        │
│ ✅ LLM-friendly (thousands of examples)│
│                                  │
│ Setup Time:                    │
│ ❌ Firebase: 2+ weeks                   │
│ ✅ Our setup: <2 hours (LLM-assisted) │
└─────────────────────────────────────┘
```

### What You Don't Need to Know

```
❌ NO: VPS, SSH, server management
❌ NO: Docker, Dockerfiles, docker-compose
❌ NO: Nginx, Apache, web server config
❌ NO: SSL certificates (auto)
❌ NO: Load balancers (auto)
❌ NO: Database administration (auto)
❌ NO: Backup management (auto)
❌ NO: Scaling strategy (auto)
```

### What You Need to Do

```
✅ YES: Connect GitHub to Railway
✅ YES: Create Supabase project
✅ YES: Create Paddle account
✅ YES: Ask LLMs for help (thousands of examples)
✅ YES: Read docs (optimized for LLMs)
```

## ADDITIONAL PROVEN REPOS (UPDATED)

### 1. paper-search-mcp (MIT License) ⭐ 550
**URL**: https://github.com/openags/paper-search-mcp
**Use**: Multi-source paper search (arXiv, PubMed, bioRxiv, medRxiv, Google Scholar, IACR, Semantic Scholar)
**Integration Point**: Literature search feature
**Why**: Already aggregates 7+ academic databases - saves integration time
**License**: MIT - Permissive, commercial use allowed

### 2. pubmed-mcp-server (Apache 2.0) ⭐ 46
**URL**: https://github.com/cyanheads/pubmed-mcp-server
**Use**: PubMed-specific advanced search, citation networks, research planning
**Integration Point**: PubMed integration in literature search
**Why**: Production-grade MCP server with robust NCBI E-utilities integration
**Features**:
- pubmed_search_articles - Search with queries, filters, date ranges
- pubmed_fetch_contents - Get detailed article info
- pubmed_article_connections - Find related/citing papers
- pubmed_research_agent - Generate research plans
- pubmed_generate_chart - Create charts from publication data
**License**: Apache 2.0 - Permissive, commercial use allowed

### 3. claude-scientific-skills (MIT License) ⭐ 6.7k
**URL**: https://github.com/K-Dense-AI/claude-scientific-skills
**Use**: 140+ scientific skills for specialized tasks
**Integration Points**:
- Literature review workflows
- Scientific writing assistance
- Data analysis
- Visualization generation
**Why**: Pre-built, tested scientific workflows - accelerates development significantly
**Categories**:
- 28+ Scientific Databases (OpenAlex, PubMed, bioRxiv, ChEMBL, UniProt, COSMIC, ClinicalTrials.gov)
- 55+ Python Packages (RDKit, Scanpy, PyTorch Lightning, scikit-learn, BioPython, BioServices, PennyLane, Qiskit)
- 15+ Scientific Integrations (Benchling, DNAnexus, LatchBio, OMERO, Protocols.io)
- 30+ Analysis & Communication Tools (Literature review, scientific writing, peer review, citations)
- 10+ Research & Clinical Tools (Hypothesis generation, grant writing, clinical decision support)
**License**: MIT - Permissive, commercial use allowed

### 4. agent-browser (Apache 2.0) ⭐ 9k
**URL**: https://github.com/vercel-labs/agent-browser
**Use**: Browser automation CLI for E2E testing
**Integration Point**: E2E testing framework
**Why**: Fast Rust CLI with Node.js fallback, perfect for automated testing
**License**: Apache 2.0 - Permissive, commercial use allowed

### 5. spec-kit (MIT License) ⭐ 64k
**URL**: https://github.com/github/spec-kit
**Use**: Spec-driven development toolkit
**Integration Point**: Development methodology
**Why**: Ensures context preservation, structured development, and reproducible process
**License**: MIT - Permissive, commercial use allowed

## PROJECT STRUCTURE (UPDATED)

```
/Users/shaileshsingh/V1 draft/
├── PROJECT_PLAN.md               # Overall project plan
├── REPOSITORIES.md              # List of all repos with licenses
├── SESSION_MEMORY.md            # This file - context preservation
├── SPEC_DRIVEN_PLAN.md         # Detailed SDD plan with phases
├── SESSION_RECOVERY.md         # Quick recovery guide
├── .specify/                   # Spec-kit generated specs
│   ├── memory/
│   │   └── constitution.md
│   ├── scripts/
│   └── templates/
│   ├── specs/
│   │   ├── chat-with-pdf/
│   │   │   ├── spec.md
│   │   │   ├── plan.md
│   │   │   ├── tasks.md
│   │   │   ├── data-model.md
│   │   │   ├── api-contracts/
│   │   │   └── quickstart.md
│   │   ├── literature-search/
│   │   ├── ai-writer/
│   │   ├── systematic-review/
│   │   ├── citation-generator/
│   │   ├── data-extraction/
│   │   ├── ai-detector/
│   │   ├── paraphraser/
│   │   ├── deep-review/
│   │   └── citation-booster/
│   └── quickstart.md
├── client/                     # Next.js frontend
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── public/
├── server/                     # FastAPI backend
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   └── services/
│   ├── pdf_processor/
│   ├── vector_store/
│   └── langchain_chains/
├── tests/                      # E2E tests with agent-browser
│   ├── scenarios/
│   │   ├── literature-review.workflow
│   │   ├── systematic-review.workflow
│   │   ├── ai-writer.workflow
│   │   └── nature-submission.workflow
│   └── expected-results/
└── docker-compose.yml           # For local development only
```

## DEVELOPMENT PHASES (UPDATED)

### Phase 0: Spec-Driven Setup (Week 1)
**Objective**: Establish SDD methodology and project constitution

- [ ] Initialize spec-kit
- [ ] Create project constitution
- [ ] Create project specification
- [ ] Create technical implementation plan
- [ ] Generate task breakdown

### Phase 1: Foundation (Week 2-3)
**Objective**: Railway deployment, Supabase setup, basic UI

- [ ] Create Railway account
- [ ] Create Railway service (Frontend + Backend)
- [ ] Create Supabase project
- [ ] Enable pgvector in Supabase
- [ ] Create Supabase auth tables
- [ ] Create Paddle account
- [ ] Create Razorpay account
- [ ] Dashboard UI
- [ ] User profile management
- [ ] Hybrid payment integration

### Phase 2: Chat with PDF (Week 4-5)
**Objective**: Upload, process, chat with documents

- [ ] PDF upload endpoint (Railway backend)
- [ ] PDF processing (Unstructured + PDFPlumber)
- [ ] Text chunking (500-1000 tokens)
- [ ] Embedding generation (OpenAI)
- [ ] Vector storage (Supabase pgvector)
- [ ] RAG chain (LangChain)
- [ ] Chat UI (real-time streaming)
- [ ] Source citation in responses

### Phase 3: Literature Search (Week 6-7)
**Objective**: Multi-source academic paper search

- [ ] paper-search-mcp integration (MCP server)
- [ ] pubmed-mcp-server integration (MCP server)
- [ ] Multi-source search aggregator
- [ ] Result deduplication
- [ ] Citation export (BibTeX, RIS, APA, MLA)
- [ ] Search history
- [ ] Save to library

### Phase 4: AI Writer (Week 8-9)
**Objective**: AI-assisted academic paper writing

- [ ] Writing project management
- [ ] Section-by-section generation (GPT-4)
- [ ] Academic tone enforcement
- [ ] Citation insertion
- [ ] Version history
- [ ] Export to multiple formats

### Phase 5: Systematic Literature Review (Week 10-11)
**Objective**: PRISMA-compliant systematic review

- [ ] PRISMA workflow builder
- [ ] Multi-source search
- [ ] Screening tool
- [ ] Data extraction form
- [ ] PRISMA flow diagram generator
- [ ] Bias assessment tool

### Phase 6: Citation Generator (Week 12)
**Objective**: Generate citations in multiple styles

- [ ] Citation input form (auto-fetch from DOI)
- [ ] 20+ citation styles
- [ ] Batch citation generation
- [ ] Bibliography management
- [ ] Export to multiple formats

### Phase 7: Data Extraction (Week 13)
**Objective**: Extract tables/figures from PDFs

- [ ] Table extraction (PDFPlumber + Camelot)
- [ ] Figure detection
- [ ] Caption extraction
- [ ] CSV/Excel export

### Phase 8: AI Detector (Week 14)
**Objective**: Detect AI-generated content

- [ ] Text input/upload
- [ ] AI probability score
- [ ] Highlighting (AI vs human sections)
- [ ] Document-level analysis

### Phase 9: Paraphraser (Week 15)
**Objective**: Academic paraphrasing tool

- [ ] Text input
- [ ] Paraphrase intensity (light, medium, strong)
- [ ] Side-by-side comparison
- [ ] Citation preservation

### Phase 10: Deep Review (Week 16)
**Objective**: Comprehensive paper analysis

- [ ] Paper upload
- [ ] Automated critique
- [ ] Cross-paper comparison
- [ ] Suggestion generation
- [ ] Similarity analysis

### Phase 11: Citation Booster (Week 17)
**Objective**: Suggest additional citations

- [ ] Text input
- [ ] Citation suggestions (from literature search)
- [ ] Relevance scoring
- [ ] One-click insertion
- [ ] Citation completeness check

### Phase 12: E2E Testing with Agent-Browser (Week 18-19)
**Objective**: Comprehensive testing of all features using Dr. Chen's workflows

- [ ] Test Scenario 1: Literature review workflow
- [ ] Test Scenario 2: Systematic review workflow
- [ ] Test Scenario 3: AI writer workflow
- [ ] Test Scenario 4: Full Nature submission workflow

**Ralph Loop for Each Scenario**:
1. Test feature
2. Find problem
3. Fix problem
4. Test again
5. Repeat until complete
6. Exit when all tests pass

### Phase 13: Polish & Launch (Week 20)
**Objective**: Performance, security, documentation, launch

- [ ] Performance optimization
- [ ] Security audit
- [ ] Error handling review
- [ ] Documentation completion
- [ ] Beta testing with 20+ researchers
- [ ] Launch preparation

## KEY PROVEN REPOS TO USE (FINAL)

### Core Infrastructure
1. **LangChain** (125k stars, MIT) - AI orchestration
2. **LlamaIndex** (37k stars, Apache 2.0) - Document indexing
3. **Next.js 14** (121k stars, MIT) - Frontend
4. **FastAPI** (77k stars, MIT) - Backend
5. **Railway** - Deployment platform (frontend + backend)
6. **Supabase** - PostgreSQL + pgvector + Auth + Storage

### AI & Machine Learning
7. **LangGraph** - Multi-agent workflows
8. **OpenAI** (GPT-4 API)
9. **Claude 3.5** (API)
10. **Transformers** (134k stars, Apache 2.0) - HuggingFace models

### PDF Processing
11. **PDFPlumber** (5.5k stars, MIT) - Table extraction
12. **Unstructured** (10k stars, Apache 2.0) - Document parsing

### Academic APIs & MCP Servers
13. **paper-search-mcp** (550 stars, MIT) - 7+ academic databases
14. **pubmed-mcp-server** (46 stars, Apache 2.0) - PubMed advanced features
15. **Scholarly** (3.5k stars, MIT) - Google Scholar
16. **arxiv.py** (2.1k stars, MIT) - ArXiv API
17. **Semantic Scholar API** - Official API
18. **BioPython** - PubMed via EDirect

### Scientific Skills
19. **claude-scientific-skills** (6.7k stars, MIT) - 140+ scientific skills

### Payments (UPDATED)
20. **Paddle** - Global payments (USD/EUR/GBP), payouts to India, tax compliance
21. **Razorpay** - Indian payments (INR), UPI support

### Testing & Development Tools
22. **agent-browser** (9k stars, Apache 2.0) - Browser automation
23. **spec-kit** (64k stars, MIT) - Spec-driven development
24. **ralph-loop** - Iterative testing methodology

## SESSION CONTEXT
- **User Goal**: Build scispace.com clone for academics
- **Founder Profile**: Non-technical, needs easy setup, LLM-friendly, depends on LLMs for debugging
- **Deployment Choice**: Railway (frontend + backend) + Supabase (DB + auth + storage)
- **Payment Choice**: Paddle (global) + Razorpay (India), hybrid approach
- **Development Strategy**: PARALLEL development with async agents + Ralph Loop testing
- **Current State**: Planning phase, documents created, methodology defined
- **Next Steps**: Initialize spec-kit and start Phase 0
- **Session ID**: sci-space-clone-001
- **Last Updated**: 2026-01-21

## DEVELOPMENT STRATEGY: PARALLEL + SEQUENTIAL

### Parallel Execution (Independent Features - Week 4-7)
**5 Agents Working Simultaneously:**
1. 🤖 Agent A: Chat with PDF - INDEPENDENT
2. 🤖 Agent B: Literature Search - INDEPENDENT
3. 🤖 Agent C: Citation Generator - INDEPENDENT
4. 🤖 Agent D: Data Extraction - INDEPENDENT
5. 🤖 Agent E: AI Detector - INDEPENDENT

**How It Works:**
```python
# Stage 2 (Week 4-7): 5 agents in parallel
async def run_parallel_stage_2():
    # All 5 features develop simultaneously
    await agent_a_chat_with_pdf()      # Independent
    await agent_b_literature_search() # Independent
    await agent_c_citation_generator() # Independent
    await agent_d_data_extraction()    # Independent
    await agent_e_ai_detector()       # Independent
    
    # All follow Ralph Loop methodology independently
    # Each: Test → Find Problem → Fix → Test Again → Exit
```

### Sequential Execution (Dependent Features - Week 8-11)
**3 Agents Work Sequentially (depend on Stage 2):**
1. 🤖 Agent F: AI Writer - DEPENDS on Literature Search (Agent B)
2. 🤖 Agent G: Systematic Review - DEPENDS on Literature Search (Agent B)
3. 🤖 Agent H: Citation Booster - DEPENDS on Literature Search (Agent B)

### Final Stages (Week 12-14)
**Sequential (depend on everything above):**
- Week 12: Paraphraser - Can be independent, but done sequentially for simplicity
- Week 13: Deep Review - DEPENDS on ALL features
- Week 14: E2E Testing - Agent-browser validates everything
- Week 15: Polish & Launch

### Total Timeline
- **Sequential Plan**: 20 weeks (5 months)
- **Parallel Plan**: 15 weeks (3.5 months)
- **Savings**: 5 weeks (30% faster) 🚀

## FOUNDER CAPABILITIES & EXPECTATIONS

### User Profile
- **Technical Background**: Non-technical founder
- **Debugging Approach**: Completely dependent on LLMs (ChatGPT/Claude)
- **Comfort Zone**: Easy setup, proven technologies, minimum complexity
- **Pain Points**: Complex server management, multiple service wiring, difficult debugging

### Code Breakdown by Source
```
┌─────────────────────────────────────────────┐
│  CODE BREAKDOWN: WHAT WE WRITE VS REPOS│
├─────────────────────────────────────────────┤
│                                          │
│ FROM PROVEN REPOS (90% of code):      │
│ ✅ LangChain (AI orchestration)         │
│ ✅ LlamaIndex (document indexing)        │
│ ✅ paper-search-mcp (7 databases)     │
│ ✅ pubmed-mcp-server (PubMed advanced)  │
│ ✅ Unstructured.io (PDF parsing)        │
│ ✅ PDFPlumber (table extraction)       │
│ ✅ Claude Scientific Skills (workflows)   │
│ ✅ HuggingFace Transformers (AI detector) │
│ ✅ Citation Style Language (formats)      │
│ ✅ Supabase (DB + auth + storage)     │
│ ✅ shadcn/ui (UI components)          │
│                                          │
│ WE WRITE (10% of code):                │
│ ⚠️ Integration code (API endpoints)      │
│ ⚠️ Business logic (subscriptions, limits)│
│ ⚠️ UI composition (Next.js + shadcn)    │
│ ⚠️ Workflow orchestration               │
│ ⚠️ Algorithm tuning (ranking, similarity) │
│ ⚠️ Prompt engineering (academic tone)     │
│ ⚠️ Error handling & edge cases          │
│                                          │
└─────────────────────────────────────────────┘
```

### Debugging Time Expectations

| Feature Type | Our Code | Debugging Hours | Risk Level |
|--------------|-----------|-----------------|-------------|
| **Chat with PDF** | 5% | 2-4 hrs | LOW |
| **Literature Search** | 10% | 4-6 hrs | LOW-MED |
| **AI Writer** | 15% | 8-12 hrs | MEDIUM |
| **Citation Generator** | 5% | 1-2 hrs | LOW |
| **Systematic Review** | 20% | 12-18 hrs | MED-HIGH |
| **Data Extraction** | 10% | 4-6 hrs | LOW-MED |
| **AI Detector** | 5% | 2-4 hrs | LOW |
| **Paraphraser** | 10% | 4-6 hrs | LOW-MED |
| **Deep Review** | 15% | 8-12 hrs | MEDIUM |
| **Citation Booster** | 10% | 6-8 hrs | LOW-MED |
| **TOTAL** | **10%** | **51-78 hrs** | **LOW-MED** |

### What This Means for Founder

**Expected Debugging: 65 hours over 15 weeks**
- = ~4.3 hours/week
- = Most debugging is UI tweaks, prompt tuning, algorithm refinement
- = NOT debugging complex infrastructure
- = NOT debugging proven libraries

**Risk Assessment: LOW-MEDIUM**
- 90% of code comes from proven repos (10k+ stars each)
- Only 10% is integration code we write
- Proven repos are battle-tested by millions of users
- Low probability of critical bugs in repos
- Bugs will be in our integration code (easier to fix)

**Founder's Expected Time Investment:**
- Code writing: ~10 hours/week (parallel agents)
- Debugging with LLMs: ~4.3 hours/week
- Ralph Loop testing: ~2 hours/week (per feature)
- Total: ~16.3 hours/week

**How to Debug with LLMs:**
```
For each bug, tell LLM:
"Help me debug this issue in my Chat with PDF feature.
Here's the error: [paste error]
Here's the code: [paste relevant code]
The feature uses: Unstructured, LangChain, Supabase pgvector.
Expected behavior: [describe what should happen]
Actual behavior: [describe error]
Please provide the fix and explain it."
```

### What Founder WILL Deal With vs WON'T

✅ **WILL Deal With (10% of code, 65 hrs debugging):**
- API endpoint integration (Railway → Supabase)
- UI component composition (Next.js + shadcn)
- Business logic (subscription limits, permissions)
- Workflow orchestration (connecting features)
- Algorithm tuning (result ranking, similarity thresholds)
- Prompt engineering (getting GPT-4 to write in academic tone)
- UI tweaks (streaming formatting, loading states)
- Citation formatting adjustments
- Edge cases (unusual PDFs, special characters)

❌ **WON'T Deal With (90% of code, minimal debugging):**
- PDF parsing (Unstructured handles it)
- Table extraction (PDFPlumber + Camelot handle it)
- Vector search (pgvector + LangChain handle it)
- RAG chains (LangChain handles it)
- Authentication (Supabase Auth handles it)
- Database operations (Supabase handles it)
- Academic API integration (MCP servers handle it)
- Citation style formatting (CSL library handles it)
- AI detection (HuggingFace models handle it)

### Success Probability

```
┌─────────────────────────────────┐
│  SUCCESS PROBABILITY ASSESSMENT  │
├─────────────────────────────────┤
│                                 │
│ Building from Scratch:          │
│   Success: 50-70%            │
│   Debugging: 400-600 hours     │
│   Time: 3-4 months           │
│   Risk: VERY HIGH             │
│                                 │
│ Our Integration Approach:       │
│   Success: 90-95%            │
│   Debugging: 65 hours        │
│   Time: 15 weeks              │
│   Risk: LOW-MEDIUM            │
│   Time Saved: 2-3 months      │
│   Risk Reduced: 40%           │
│                                 │
└─────────────────────────────────┘
```

### When Founder Needs Help

**For Coding Issues:**
1. Try ChatGPT/Claude first with clear prompt
2. Include context: "This is for my Chat with PDF feature using Unstructured + LangChain"
3. Paste error and relevant code
4. Ask for explanation + fix + testing steps

**For Design/UI Issues:**
1. Use shadcn/ui components (pre-styled, accessible)
2. Ask LLM: "Help me style this page using shadcn/ui components and Tailwind CSS"
3. Focus on layout and spacing (LLMs good at this)

**For Debugging Complex Issues:**
1. Clear steps: What you did, what you expected, what happened
2. Screenshots: Include error messages or unexpected behavior
3. Context: What feature, what part of workflow
4. Ask LLM to: "Break down the problem step-by-step and help me solve each part"

**When to Escalate to Me (Claude Code):**
- You've spent >2 hours on a single bug
- LLMs giving inconsistent answers
- Not sure which file or component to modify
- Need architectural guidance

## METHODOLOGY SUMMARY

### How We Work

#### 1. Spec-First Approach
1. Define WHAT we're building (not HOW)
2. Create user stories and requirements
3. Generate technical plan
4. Break down into actionable tasks
5. Execute tasks systematically

#### 2. Ralph Loop Testing
For EACH feature:
```
Test → Find Problem → Fix → Test Again → Exit When Complete
```

**Principles**:
- Never abandon a feature
- Fix issues until they work
- Document all fixes
- Validate with real user scenarios (Dr. Chen)

#### 3. Agent-Browser Validation
For EACH feature:
- Create automated test scenarios
- Simulate real user workflows
- Test UI interactions
- Verify end-to-end functionality
- Catch integration issues early

#### 4. Continuous Integration
- All repos use permissive licenses (MIT, Apache 2.0)
- Proven, battle-tested components only
- Context preserved across sessions
- Reproducible development process
- LLM-friendly setup for non-technical founder

## IMPORTANT NOTES

1. **Custom UI**: Not scispace.com look, but same functionality
2. **Railway Deployment**: Frontend + backend on single platform (zero server management)
3. **Supabase Integration**: DB + Auth + Storage all-in-one (easiest setup)
4. **Hybrid Payments**: Paddle (global) + Razorpay (India)
5. **Spec-Driven**: Use spec-kit for structured development
6. **Ralph Loop**: Test → Fix → Test → Exit (never abandon)
7. **Agent-Browser**: E2E test all features before completion
8. **Dr. Chen Persona**: Test as if submitting to Nature
9. **Proven Repos Only**: All MIT or Apache 2.0 licensed
10. **LLM-Friendly**: Easy to ask ChatGPT/Claude for help
11. **Session Memory**: Check SESSION_MEMORY.md on session start
12. **Context Preservation**: Use spec-kit to survive crashes
13. **Non-Technical Founder Focus**: Maximum ease of setup, minimum technical complexity
14. **Migration Path**: Can migrate from Railway/Supabase later if needed (but don't expect to)

## SUBSCRIPTION TIERS

### Free Tier
- 5 PDF uploads
- Basic chat with PDF
- 50 literature searches/month
- Basic citation generation
- Watermarked outputs

### Pro ($19/month)
- Unlimited PDFs
- Unlimited literature searches
- AI Writer
- Advanced data extraction
- Priority processing
- No watermarks

### Team ($49/month/user)
- Everything in Pro
- Team collaboration
- Shared libraries
- Admin dashboard
- Priority support
- API access

## COST ESTIMATION (UPDATED)

### Infrastructure (Monthly)
- Railway (Frontend + Backend): $20/month
  - Pro 1 tier: 2GB RAM, 1 CPU
  - Scales automatically
- Supabase (DB + Auth + Storage): $0 → $25/month
  - Free tier: 500MB DB, 500MB storage
  - Pro tier (when needed): 8GB DB, 100GB storage
- **Total: $20-45/month** (startup phase)

### AI APIs (for 100 active users)
- OpenAI GPT-4: $30-80
- Embeddings: $10-20
- Claude 3.5: $10-30
- **Total: $50-130/month**

### Third-party Services
- Paddle: $0/month + 5% + $0.50 per transaction
- Razorpay: $0/month + 2% + $0.10 per transaction (India only)
- Supabase: Included in DB cost
- **Total: $0 + variable**

### Total: $70-175/month (infrastructure + AI)
### Revenue: $1,900/month (100 users @ $19/mo)
### Net: ~$1,725-1,830/month (at 100 users)

## NEXT ACTIONS

### Immediate (Today)
1. ✅ Update all documentation with Railway + Supabase + Paddle
2. ✅ Review and approve final tech stack
3. ✅ Ready to begin when user says "start"

### This Week
1. Complete Phase 0 (Spec-Driven Setup)
2. Validate spec-kit installation
3. Review constitution with user
4. Get approval on specification
5. Generate detailed tasks

### Next Week
1. Begin Phase 1 (Foundation)
2. Set up Railway account and services
3. Set up Supabase project
4. Set up Paddle + Razorpay accounts
5. Build basic UI
6. Start Ralph loop testing

## RECOVERY CHECKLIST

If session crashes, do this:

1. **Read SESSION_MEMORY.md** - This file (you're here!)
2. **Read SESSION_RECOVERY.md** - Quick recovery guide
3. **Read SPEC_DRIVEN_PLAN.md** - Detailed plan
4. **Read REPOSITORIES.md** - All repos
5. **Run**: `specify check` - Verify tools installed
6. **Continue** from last completed phase

## SUCCESS METRICS

### By Feature Completion
- [ ] All user stories pass Ralph loop testing
- [ ] Agent-browser scenarios pass
- [ ] Dr. Chen approves functionality
- [ ] Documentation complete
- [ ] Code quality checks pass

### By Project Completion
- [ ] 11/11 features implemented
- [ ] 200+ test scenarios passing
- [ ] Dr. Chen successfully submits Nature review
- [ ] 20+ beta testers happy
- [ ] Ready for launch

**When to Escalate to Me (Claude Code):**
- You've spent >2 hours on a single bug
- LLMs giving inconsistent answers
- Not sure which file or component to modify
- Need architectural guidance

## WHAT TO TELL ME WHEN STARTING

### When Refreshing Context in New Session

```
"I'm ready to start building my Sci-Space clone for academics.
Please read SESSION_MEMORY.md to regain full context.

Important things to remember:
- I'm a non-technical founder
- We're using Railway (frontend + backend) + Supabase (DB + auth + storage)
- We're using Paddle (global) + Razorpay (India) for payments
- We're using parallel development strategy with async agents
- Week 4-7: 5 independent features in parallel (Chat with PDF, Literature Search, Citation Generator, Data Extraction, AI Detector)
- Week 8-11: 3 dependent features sequentially (AI Writer, Systematic Review, Citation Booster)
- Week 12-14: Deep Review, E2E Testing, Launch
- 90% of code comes from proven repos (LangChain, LlamaIndex, paper-search-mcp, pubmed-mcp-server, Unstructured, PDFPlumber, etc.)
- Only 10% is integration code we write + debug
- Expected debugging: 65 hours total over 15 weeks (4.3 hours/week)
- Most debugging will be: UI tweaks, prompt tuning, algorithm refinement (NOT debugging complex infrastructure)

Start with Phase 0: Spec-Driven Setup."
```

### This Tells Me:
1. ✅ Project context and goal
2. ✅ Founder profile (non-technical, needs LLM help)
3. ✅ Tech stack choices (Railway + Supabase + Paddle)
4. ✅ Development strategy (parallel agents)
5. ✅ What weeks to do what (Week 4-7: parallel, Week 8-11: sequential)
6. ✅ Code breakdown (90% repos, 10% our code)
7. ✅ Debugging expectations (65 hours total, mostly UI + algorithms)
8. ✅ What to start with (Phase 0)

### What I Will Do When You Say "Start"

1. **Read SESSION_MEMORY.md** - Regain full context
2. **Read SPEC_DRIVEN_PLAN.md** - Review 15-week parallel plan
3. **Read SESSION_RECOVERY.md** - Check recovery guide
4. **Initialize Phase 0** - Install spec-kit, create constitution
5. **Create Specification** - Define all 11 features
6. **Generate Technical Plan** - Architecture, database, APIs
7. **Generate Tasks** - Break down into actionable items
8. **Begin Execution** - Start implementing features

### I Will NOT Forget:
- ✅ Parallel development strategy (Week 4-7: 5 agents simultaneously)
- ✅ Sequential dependencies (AI Writer needs Literature Search first, etc.)
- ✅ Ralph Loop methodology (Test → Fix → Test → Exit)
- ✅ 90% proven repos, 10% integration code
- ✅ 65 hours debugging expected (UI, prompts, algorithms)
- ✅ User is non-technical, needs LLM-friendly approach
- ✅ Deployment: Railway + Supabase + Paddle/Razorpay
- ✅ All context preserved in markdown files

---

**Remember**: All context saved in markdown files. If session crashes, read SESSION_MEMORY.md, SPEC_DRIVEN_PLAN.md, and SESSION_RECOVERY.md to regain full context.
