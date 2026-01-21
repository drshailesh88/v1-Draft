# ⚡ ULTIMATE BUILD DIRECTIVE - SCI-SPACE CLONE

**READ THIS FIRST ON EVERY NEW SESSION**
This file contains EVERYTHING we planned, how to build it, when to use parallel vs sequential agents, and all technical decisions.

---

## 🎯 PROJECT OVERVIEW

**What We're Building**: A subscription-based academic research platform (scispace.com clone) for global + Indian academics

**Target Users**: Academics, researchers, students

**Business Model**: Subscription tiers (Free: $0, Pro: $19/mo, Team: $49/mo/user)

**Custom UI**: Will NOT look like scispace.com, but same functionality

**Timeline**: 15 weeks (3.5 months) using parallel development strategy

**Founder Profile**: Non-technical, completely dependent on LLMs for debugging, needs easy setup

---

## 🏗️ TECH STACK (FINAL DECISIONS)

### Frontend
- **Next.js 14** (App Router) - 121k stars, MIT
- **shadcn/ui** - Beautiful, accessible components, 71k stars, MIT
- **Tailwind CSS** - Styling
- **TanStack Table** - Data tables for papers, 23k stars, MIT
- **agent-browser** - For automated E2E testing, 9k stars, Apache 2.0

### Backend
- **FastAPI** (Python) - Fast async, type-safe, 77k stars, MIT
- **LangChain** - AI orchestration, chains, agents, 125k stars, MIT
- **LlamaIndex** - Document indexing, retrieval, 37k stars, Apache 2.0
- **LangGraph** - Multi-agent workflows

### MCP Integrations (Critical)
- **paper-search-mcp** (550 stars, MIT) - 7+ academic databases in one interface
- **pubmed-mcp-server** (46 stars, Apache 2.0) - PubMed advanced features
- **claude-scientific-skills** (6.7k stars, MIT) - 140+ scientific skills

### Database + Auth + Storage
- **Supabase** (PostgreSQL + pgvector)
  - Built-in pgvector extension (no separate vector DB!)
  - Built-in Auth (no separate service!)
  - Built-in Storage (for PDFs)
  - Built-in Edge Functions
  - Real-time capabilities
  - Zero database administration
  - Auto-backups
  - Auto-scaling

### AI/ML
- **OpenAI GPT-4** - Main reasoning
- **Claude 3.5 Sonnet** - Alternative/better for some tasks
- May add more models later

### PDF Processing
- **Unstructured.io** - Document parsing, element extraction, 10k stars, Apache 2.0
- **PDFPlumber** - Table extraction with precise coordinates, 5.5k stars, MIT
- **Camelot** - Complex table extraction, 4.6k stars, MIT

### Payments (Hybrid Approach)
- **Paddle** (for global users)
  - USD/EUR/GBP pricing
  - Payouts to India automatically
  - Handles all tax compliance
  - No US entity needed
- **Razorpay** (for Indian users)
  - INR pricing
  - UPI support
  - 90%+ Indian payments
- **Currency detection**: Automatic routing to appropriate provider

### Deployment
- **Railway** (for frontend + backend)
  - Single platform for both
  - Easy deployment (git push)
  - Zero server management
  - Auto-deploys from GitHub
  - Built-in monitoring
  - Predictable pricing ($20/month for Pro 1 tier)
- **Supabase** (for database + auth + storage)
  - $0 → $25/month (Free tier: 500MB DB, 500MB storage)
  - Pro tier: 8GB DB, 100GB storage when needed

---

## 📋 11 CORE FEATURES (Build in This Order)

1. **Chat with PDF** - Upload PDFs, ask questions, get answers with page citations
2. **Literature Search** - Multi-source search (PubMed, Google Scholar, ArXiv, bioRxiv, medRxiv, Semantic Scholar, IACR)
3. **AI Writer** - Draft academic papers section-by-section (abstract, intro, methods, results, discussion, conclusion)
4. **Citation Generator** - Multiple styles (APA, MLA, Chicago, IEEE, Harvard, etc.)
5. **Paraphraser** - Academic paraphrasing with citation preservation
6. **Data Extraction** - Extract tables/figures from PDFs to CSV/Excel
7. **Find Topics** - Topic discovery, research gaps, trending topics
8. **Systematic Literature Review** - PRISMA methodology with flow diagram generator
9. **Deep Review** - Comprehensive paper analysis with critique
10. **Citation Booster** - Suggest relevant citations based on text
11. **AI Detector** - Detect AI-generated content

### Features to Exclude
- Chart/Data visualizations
- Poster generation
- Patent search
- Website/research site builder

---

## 🚀 DEVELOPMENT METHODOLOGY

### 1. Spec-Driven Development (SDD)
Using **github/spec-kit** (64k stars, MIT) to ensure:
- Intent-driven development (define "what" before "how")
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
```

### 2. Ralph Loop Testing
Using **anthropics/claude-plugins-official/plugins/ralph-loop**

**For EACH Feature**:
```
Test → Find Problem → Fix → Test Again → Exit When Complete
```

**Principles**:
- Never abandon features - we fix until it works
- Iterative refinement based on testing results
- Quality gates before moving forward
- Document all fixes and learnings
- Define exit criteria before testing

### 3. Browser-Based E2E Testing
Using **vercel-labs/agent-browser** (9k stars, Apache 2.0)

**Purpose**:
- Automated E2E testing of all features
- Simulating real user workflows (Dr. Chen)
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

---

## 🎭 TESTING PERSONA: DR. CHEN

### Background
- **PhD**: Computational Biology, MIT
- **Postdoc**: Stanford (AI/ML)
- **Current**: Assistant Professor, UC Berkeley
- **Publications**: Nature, Science, Cell

### Current Task
Submit a **state-of-the-art review on "AI-Powered Drug Discovery"** to **Nature**

### Requirements from Nature
- Comprehensive literature review (500+ papers)
- PRISMA methodology for systematic review
- Data extraction from 200+ papers
- Visual analysis of trends
- Gap identification
- Future directions
- Publication-ready figures

### Dr. Chen's Testing Approach
- Will use EVERY feature of app
- Will test edge cases and failure modes
- Will validate all output formats
- Will check citation accuracy
- Will verify data extraction quality
- Will test collaboration features
- Will validate export capabilities
- Will simulate full Nature submission workflow

---

## ⚡ PARALLEL DEVELOPMENT STRATEGY (CRITICAL!)

### Why Parallel?

**Problem with Sequential (Original Plan)**:
- 20 weeks to build all 11 features
- No way to speed up
- Founder waits for each feature sequentially

**Solution: Parallel Agents (New Plan)**:
- 15 weeks total (saves 5 weeks = 30% faster)
- 5 independent features built simultaneously (Week 4-7)
- 3 dependent features built sequentially (Week 8-11)

### Timeline Overview

```
Week 1:    Phase 0: Spec-Driven Setup
Week 2-3:  Phase 1: Foundation (Sequential - BLOCKS everything)
Week 4-7:  Phase 2-6: PARALLEL SPRINT (5 independent features)
             ├─ Agent A: Chat with PDF
             ├─ Agent B: Literature Search
             ├─ Agent C: Citation Generator
             ├─ Agent D: Data Extraction
             └─ Agent E: AI Detector
Week 8-11:  Phase 7-11: SEQUENTIAL SPRINT (3 dependent features)
             ├─ Agent F: AI Writer (depends on Literature Search)
             ├─ Agent G: Systematic Review (depends on Literature Search)
             └─ Agent H: Citation Booster (depends on Literature Search)
Week 12:    Phase 12: Paraphraser (Sequential or parallel)
Week 13:    Phase 13: Deep Review (Depends on EVERYTHING - must be last)
Week 14:    Phase 14: E2E Testing (Agent-browser validates all)
Week 15:    Phase 15: Polish & Launch

Total: 15 weeks (3.5 months)
Savings: 5 weeks (30% faster)
```

---

## 🔍 PARALLEL VS SEQUENTIAL - WHEN TO USE WHICH

### PARALLEL - Week 4-7 (5 Agents Simultaneously)

**Use When**: Features are INDEPENDENT
- No shared dependencies
- No shared database tables (initially)
- Can work in separate code areas
- Can be developed in separate sessions

**5 Independent Features**:

1. **Agent A: Chat with PDF** (INDEPENDENT)
   - Uses: Unstructured, LangChain, OpenAI, Supabase pgvector
   - Debugging: 2-4 hours (LOW risk)
   - No dependencies on other features

2. **Agent B: Literature Search** (INDEPENDENT)
   - Uses: paper-search-mcp, pubmed-mcp-server, Supabase
   - Debugging: 4-6 hours (LOW-MED risk)
   - No dependencies on other features
   - **CRITICAL**: AI Writer, Systematic Review, Citation Booster DEPEND on this

3. **Agent C: Citation Generator** (INDEPENDENT)
   - Uses: Citation Style Language, pubmed-mcp, Supabase
   - Debugging: 1-2 hours (LOW risk)
   - No dependencies on other features

4. **Agent D: Data Extraction** (INDEPENDENT)
   - Uses: PDFPlumber, Camelot, Unstructured, Supabase
   - Debugging: 4-6 hours (LOW-MED risk)
   - No dependencies on other features

5. **Agent E: AI Detector** (INDEPENDENT)
   - Uses: HuggingFace Transformers, OpenAI, Supabase
   - Debugging: 2-4 hours (LOW risk)
   - No dependencies on other features

### How Parallel Execution Works

**Founder's Approach**:
```python
# Week 4: Start all 5 agents in separate sessions
Session 1: "Agent A, build Chat with PDF feature."
Session 2: "Agent B, build Literature Search feature."
Session 3: "Agent C, build Citation Generator feature."
Session 4: "Agent D, build Data Extraction feature."
Session 5: "Agent E, build AI Detector feature."

# All 5 work SIMULTANEOUSLY!
# Founder switches between sessions to monitor progress
# Each agent follows Ralph Loop independently
```

**Agent Behavior**:
- Each agent works in separate conversation/session
- No coordination needed between agents (features are independent)
- Each agent has separate spec in `.specify/specs/`
- Each agent has separate agent-browser test scenarios
- Each agent provides weekly progress update
- Founder monitors all 5 agents concurrently

**Each Agent Follows Ralph Loop Independently**:
1. Implement feature
2. Write E2E test scenario (agent-browser)
3. Test feature
4. Find problem
5. Fix problem
6. Test again
7. Repeat until complete
8. Exit when tests pass

---

### SEQUENTIAL - Week 8-11 (3 Agents One After Another)

**Use When**: Features are DEPENDENT
- Need data from another feature
- Use APIs from another feature
- Share complex business logic
- Must wait for prerequisite to complete

**3 Dependent Features**:

1. **Agent F: AI Writer** - DEPENDS on Literature Search (Agent B)
   - Uses: Literature search results for citation insertion
   - Debugging: 8-12 hours (MEDIUM risk)
   - Must wait for Literature Search to complete

2. **Agent G: Systematic Review** - DEPENDS on Literature Search (Agent B)
   - Uses: Literature search APIs for multi-source search
   - Debugging: 12-18 hours (MED-HIGH risk)
   - Must wait for Literature Search to complete

3. **Agent H: Citation Booster** - DEPENDS on Literature Search (Agent B)
   - Uses: Literature search for citation suggestions
   - Debugging: 6-8 hours (LOW-MED risk)
   - Must wait for Literature Search to complete

### How Sequential Execution Works

**Founder's Approach**:
```python
# Week 4-7: Literature Search completes (Agent B)
# Week 8: Check if Literature Search is complete
if literature_search_complete:
    # Start dependent features sequentially
    Session 1: "Agent F, build AI Writer feature."
    # Wait for AI Writer to complete

    Session 2: "Agent G, build Systematic Review feature."
    # Wait for Systematic Review to complete

    Session 3: "Agent H, build Citation Booster feature."
    # Wait for Citation Booster to complete
```

**Agent Behavior**:
- Each agent works sequentially (one after another)
- Each agent follows Ralph Loop independently
- Founder only works with one agent at a time
- Founder monitors progress and approves before moving to next agent

---

### FINAL STAGES - Week 12-15

**Week 12: Paraphraser**
- Can be independent, but done sequentially for simplicity
- Debugging: 4-6 hours (LOW-MED risk)

**Week 13: Deep Review**
- DEPENDS ON EVERYTHING - must be last
- Integrates all features
- Debugging: 8-12 hours (MEDIUM risk)

**Week 14: E2E Testing**
- Agent-browser validates ALL features
- Test Dr. Chen's complete Nature submission workflow
- All 4 test scenarios must pass

**Week 15: Polish & Launch**
- Performance optimization
- Security audit
- Documentation completion
- Beta testing with 20+ researchers
- Launch preparation

---

## 📊 CODE BREAKDOWN: PROVEN REPOS vs OUR CODE

### What Comes From Proven Repos (90% of code)

```
┌──────────────────────────────────────────┐
│  FROM PROVEN REPOS (BATTLE-TESTED)    │
├──────────────────────────────────────────┤
│ ✅ LangChain (125k stars, MIT)         │
│    - AI orchestration, chains, agents  │
│ ✅ LlamaIndex (37k stars, Apache)      │
│    - Document indexing, retrieval        │
│ ✅ paper-search-mcp (550 stars, MIT)  │
│    - 7 academic databases integrated   │
│ ✅ pubmed-mcp-server (46 stars, Apache)│
│    - PubMed advanced features           │
│ ✅ Unstructured.io (10k stars, Apache) │
│    - PDF parsing, element extraction    │
│ ✅ PDFPlumber (5.5k stars, MIT)       │
│    - Table extraction                   │
│ ✅ Camelot (4.6k stars, MIT)          │
│    - Complex table extraction           │
│ ✅ Claude Scientific Skills (6.7k)    │
│    - 140+ scientific workflows          │
│ ✅ HuggingFace Transformers (134k)     │
│    - AI detector models                │
│ ✅ Citation Style Language             │
│    - 20+ citation style formats        │
│ ✅ Supabase (DB + auth + storage)     │
│    - Database, auth, storage built-in  │
│ ✅ shadcn/ui (71k stars, MIT)         │
│    - Beautiful UI components           │
└──────────────────────────────────────────┘
```

### What We Write (10% of code)

```
┌──────────────────────────────────────────┐
│  WE WRITE (INTEGRATION CODE)           │
├──────────────────────────────────────────┤
│ ⚠️ API endpoints (Railway backend)     │
│ ⚠️ Business logic (subscriptions, limits)│
│ ⚠️ UI composition (Next.js + shadcn)   │
│ ⚠️ Workflow orchestration              │
│ ⚠️ Algorithm tuning (ranking, similarity)│
│ ⚠️ Prompt engineering (academic tone)    │
│ ⚠️ Error handling & edge cases         │
└──────────────────────────────────────────┘
```

---

## 🔧 FOUNDER CAPABILITIES & EXPECTATIONS

### Technical Level
**Non-technical founder**
- Completely dependent on LLMs (ChatGPT, Claude) for debugging and implementation
- Needs easy setup, proven technologies
- Struggles with:
  - ❌ Complex server management (VPS, SSH, Nginx, Docker)
  - ❌ Multiple services integration difficulty (Firebase wiring)
  - ❌ Time-consuming debugging of infrastructure
  - ❌ Lack of technical knowledge for debugging
  - ❌ Need for quick, reliable deployment

### Capabilities
- ✅ Approve technical decisions
- ✅ Test features as real user (Dr. Chen's persona)
- ✅ Provide UI/UX feedback
- ✅ Monitor progress weekly
- ✅ Report bugs/issues to LLM
- ❌ SSH into servers
- ❌ Configure Docker, Nginx, SSL
- ❌ Manage database administration
- ❌ Debug complex infrastructure

---

## ⏱️ DEBUGGING TIME EXPECTATIONS

### By Feature

| Feature | Our Code | Debugging Hours | Risk Level |
|---------|-----------|-----------------|-------------|
| Chat with PDF | 5% | 2-4 hrs | LOW |
| Literature Search | 10% | 4-6 hrs | LOW-MED |
| AI Writer | 15% | 8-12 hrs | MEDIUM |
| Citation Generator | 5% | 1-2 hrs | LOW |
| Systematic Review | 20% | 12-18 hrs | MED-HIGH |
| Data Extraction | 10% | 4-6 hrs | LOW-MED |
| AI Detector | 5% | 2-4 hrs | LOW |
| Paraphraser | 10% | 4-6 hrs | LOW-MED |
| Deep Review | 15% | 8-12 hrs | MEDIUM |
| Citation Booster | 10% | 6-8 hrs | LOW-MED |
| **TOTAL** | **10%** | **51-78 hrs** | **LOW-MED** |

### What This Means

**Expected Debugging: 65 hours over 15 weeks**
- ~4.3 hours/week
- Most debugging is: UI tweaks, prompt tuning, algorithm refinement
- **NOT debugging complex infrastructure**
- **NOT debugging proven libraries**

**Success Probability: 90-95%**
- 90% of code comes from proven repos (10k+ stars each)
- Only 10% is integration code we write
- Proven repos are battle-tested by millions of users
- Low probability of critical bugs in repos
- Bugs will be in our integration code (easier to fix)

### Founder's Expected Time Investment

- Code writing: ~10 hours/week (parallel agents)
- Debugging with LLMs: ~4.3 hours/week
- Ralph Loop testing: ~2 hours/week (per feature)
- **Total: ~16.3 hours/week**

### How to Debug with LLMs

**For each bug, tell LLM**:
```
"Help me debug this issue in my [feature name].
The feature uses: [list of repos used].
Here's the error: [paste error]
Here's the code: [paste relevant code]
Expected behavior: [describe what should happen]
Actual behavior: [describe what's happening]
Please provide step-by-step fix and explanation."
```

### What Founder WILL Deal With vs WON'T

**WILL Deal With (10% of code, 65 hrs debugging)**:
- ✅ API endpoint integration (Railway → Supabase)
- ✅ UI component composition (Next.js + shadcn)
- ✅ Business logic (subscription limits, permissions)
- ✅ Workflow orchestration (connecting features)
- ✅ Algorithm tuning (result ranking, similarity thresholds)
- ✅ Prompt engineering (getting GPT-4 to write in academic tone)
- ✅ UI tweaks (streaming formatting, loading states)
- ✅ Citation formatting adjustments
- ✅ Edge cases (unusual PDFs, special characters)

**WON'T Deal With (90% of code, minimal debugging)**:
- ❌ PDF parsing (Unstructured handles it)
- ❌ Table extraction (PDFPlumber + Camelot handle it)
- ❌ Vector search (pgvector + LangChain handle it)
- ❌ RAG chains (LangChain handles it)
- ❌ Authentication (Supabase Auth handles it)
- ❌ Database operations (Supabase handles it)
- ❌ Academic API integration (MCP servers handle it)
- ❌ Citation style formatting (CSL library handles it)
- ❌ AI detection (HuggingFace models handle it)

---

## 🏢 DEPLOYMENT ARCHITECTURE

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

---

## 💰 COST ESTIMATION

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

---

## 📅 PHASE-BY-PHASE BREAKDOWN

### Phase 0: Spec-Driven Setup (Week 1)

**Objective**: Establish SDD methodology and project constitution

**Tasks**:
- [ ] Install spec-kit: `uv tool install specify-cli --from git+https://github.com/github/spec-kit.git`
- [ ] Initialize: `specify init . --ai claude`
- [ ] Create project constitution: `/speckit.constitution`
- [ ] Create project specification: `/speckit.specify` (all 11 features)
- [ ] Create technical implementation plan: `/speckit.plan`
- [ ] Generate task breakdown: `/speckit.tasks`

**Exit Criteria**: Constitution, specs, plans, tasks all created and approved

---

### Phase 1: Foundation (Week 2-3) - SEQUENTIAL (BLOCKS EVERYTHING!)

**Objective**: Railway deployment, Supabase setup, basic UI

**IMPORTANT**: This phase MUST be complete before any parallel agents start - all features depend on this.

**Tasks**:
- [ ] Create Railway account
- [ ] Create Railway service (Frontend + Backend)
- [ ] Create Supabase project
- [ ] Enable pgvector in Supabase
- [ ] Create Supabase auth tables
- [ ] Create Paddle account
- [ ] Create Razorpay account (if needed for India)
- [ ] Dashboard UI
- [ ] User profile management
- [ ] Hybrid payment integration (Paddle for global, Razorpay for India)

**Exit Criteria**: All auth, database, payments working. Railway + Supabase + Paddle/Razorpay operational.

---

### PARALLEL SPRINT - Week 4-7 (5 Agents Simultaneously)

#### Agent A: Chat with PDF (Week 4-7) - INDEPENDENT

**User Stories**:
- US2.1: As a researcher, I can upload a PDF paper
- US2.2: As a researcher, I can see processing status
- US2.3: As a researcher, I can ask questions about PDF
- US2.4: As a researcher, I get answers with page references

**Features**:
- [ ] PDF upload endpoint (multipart/form-data)
- [ ] PDF processing (Unstructured + PDFPlumber)
- [ ] Text chunking (500-1000 tokens)
- [ ] Embedding generation (OpenAI text-embedding-3-small)
- [ ] Vector storage (Supabase pgvector)
- [ ] RAG chain (LangChain)
- [ ] Chat UI (real-time streaming)
- [ ] Source citation in responses

**Integration Points**:
- Use Unstructured.io for document parsing
- Use PDFPlumber for table extraction
- Use LangChain for RAG pipeline
- Use pgvector for vector search

**Testing (Ralph Loop)**:
1. Upload Dr. Chen's Nature review PDF
2. Test: "What are the main findings?"
3. Find problem: No page references
4. Fix: Add page number tracking in chunks
5. Test again: Success with page refs
6. Test: Extract data from Table 3
7. Find problem: Table structure lost
8. Fix: Use PDFPlumber for tables
9. Test again: Table extracted correctly
10. Exit: All tests pass

**Debugging Time**: 2-4 hours (LOW risk)

---

#### Agent B: Literature Search (Week 4-7) - INDEPENDENT

**User Stories**:
- US3.1: As a researcher, I can search PubMed
- US3.2: As a researcher, I can search arXiv
- US3.3: As a researcher, I can search Google Scholar
- US3.4: As a researcher, I can see aggregated results
- US3.5: As a researcher, I can export citations

**Features**:
- [ ] **paper-search-mcp integration** (MCP server) - 7 databases
- [ ] **pubmed-mcp-server integration** (MCP server) - PubMed advanced
- [ ] Multi-source search aggregator
- [ ] Result deduplication
- [ ] Citation export (BibTeX, RIS, APA, MLA)
- [ ] Search history
- [ ] Save to library

**Integration Points**:
- **paper-search-mcp**: arXiv, bioRxiv, medRxiv, Google Scholar, IACR, Semantic Scholar
- **pubmed-mcp-server**: PubMed with advanced features (citation networks, research planning)
- **Claude Scientific Skills**: Literature review workflows

**Testing (Ralph Loop)**:
1. Test: Search "AI drug discovery" across all sources
2. Find problem: Duplicates in results
3. Fix: Implement deduplication logic (DOI + title matching)
4. Test again: Results deduplicated
5. Test: Export 10 results to BibTeX
6. Find problem: Missing DOIs
7. Fix: Add DOI fetch from all sources
8. Test again: BibTeX complete
9. Test: Search PubMed for Dr. Chen's papers
10. Find problem: Rate limited
11. Fix: Implement caching + rate limiting
12. Test again: Success
13. Exit: All tests pass

**Debugging Time**: 4-6 hours (LOW-MED risk)

**CRITICAL**: AI Writer, Systematic Review, Citation Booster depend on this feature!

---

#### Agent C: Citation Generator (Week 4-7) - INDEPENDENT

**User Stories**:
- US6.1: As a researcher, I can enter paper metadata
- US6.2: As a researcher, I can generate APA citation
- US6.3: As a researcher, I can generate MLA citation
- US6.4: As a researcher, I can generate BibTeX
- US6.5: As a researcher, I can batch generate citations

**Features**:
- [ ] Citation input form (auto-fetch from DOI)
- [ ] 20+ citation styles (Citation Style Language)
- [ ] Batch citation generation
- [ ] Bibliography management
- [ ] Export to multiple formats

**Integration Points**:
- **citation-style-language**: Style definitions
- **PubMed/MCP**: Auto-fetch metadata

**Testing (Ralph Loop)**:
1. Test: Generate APA citation from DOI
2. Find problem: DOI fetch fails
3. Fix: Use PubMed MCP for lookup
4. Test again: Citation generated
5. Test: Batch generate 50 citations
6. Find problem: Timeout after 10
7. Fix: Implement async processing
8. Test again: All 50 generated
9. Exit: All tests pass

**Debugging Time**: 1-2 hours (LOW risk)

---

#### Agent D: Data Extraction (Week 4-7) - INDEPENDENT

**User Stories**:
- US7.1: As a researcher, I can extract tables
- US7.2: As a researcher, I can extract figure captions
- US7.3: As a researcher, I can export to CSV
- US7.4: As a researcher, I can download original figures

**Features**:
- [ ] Table extraction (PDFPlumber + Camelot)
- [ ] Figure detection
- [ ] Caption extraction
- [ ] CSV/Excel export
- [ ] Metadata preservation (page, title)

**Integration Points**:
- **PDFPlumber**: Table extraction
- **Camelot**: Complex table extraction
- **Unstructured**: Figure detection

**Testing (Ralph Loop)**:
1. Test: Extract tables from Dr. Chen's review
2. Find problem: Multi-page tables broken
3. Fix: Implement multi-page table detection
4. Test again: Tables complete
5. Test: Export to CSV
6. Find problem: Column headers lost
7. Fix: Add header detection
8. Test again: Headers preserved
9. Exit: All tests pass

**Debugging Time**: 4-6 hours (LOW-MED risk)

---

#### Agent E: AI Detector (Week 4-7) - INDEPENDENT

**User Stories**:
- US8.1: As a researcher, I can paste text
- US8.2: As a researcher, I can see AI probability
- US8.3: As a researcher, I can upload a document
- US8.4: As a researcher, I can see document-level analysis

**Features**:
- [ ] Text input/upload
- [ ] AI probability score
- [ ] Highlighting (AI vs human sections)
- [ ] Document-level analysis
- [ ] Confidence metrics

**Integration Points**:
- **HuggingFace Transformers**: Pre-trained AI detector model
- **Claude Scientific Skills**: Text analysis workflows

**Testing (Ralph Loop)**:
1. Test: Detect AI in GPT-4 text
2. Find problem: Low confidence
3. Fix: Use ensemble of models
4. Test again: High confidence
5. Test: Analyze full paper (Dr. Chen's review)
6. Find problem: Timeout on 20 pages
7. Fix: Implement chunked analysis
8. Test again: Analyzes full paper
9. Exit: All tests pass

**Debugging Time**: 2-4 hours (LOW risk)

---

### SEQUENTIAL SPRINT - Week 8-11 (3 Agents One After Another)

#### Agent F: AI Writer (Week 8-9) - DEPENDS ON LITERATURE SEARCH

**User Stories**:
- US4.1: As a researcher, I can start a writing project
- US4.2: As a researcher, I can generate sections (abstract, intro, etc.)
- US4.3: As a researcher, I can edit AI-generated content
- US4.4: As a researcher, I can track word count
- US4.5: As a researcher, I can export to LaTeX/Word

**Features**:
- [ ] Writing project management
- [ ] Section-by-section generation (GPT-4)
- [ ] Academic tone enforcement
- [ ] Citation insertion (uses Literature Search)
- [ ] Version history
- [ ] Collaborative editing (Team tier)
- [ ] Export to multiple formats

**Integration Points**:
- **LangChain**: Writing chains with academic prompts
- **Claude Scientific Skills**: Scientific writing best practices
- **Citation generator**: Auto-insert citations
- **Literature Search**: Find and insert citations

**Testing (Ralph Loop)**:
1. Test: Generate abstract for Dr. Chen's review
2. Find problem: Too informal tone
3. Fix: Add academic tone prompt engineering
4. Test again: Tone appropriate
5. Test: Insert citations in text
6. Find problem: Citations not formatted
7. Fix: Integrate citation generator
8. Test again: Citations formatted
9. Test: Export to LaTeX
10. Find problem: Table of contents missing
11. Fix: Add TOC generation
12. Test again: TOC present
13. Exit: All tests pass

**Debugging Time**: 8-12 hours (MEDIUM risk)

---

#### Agent G: Systematic Literature Review (Week 10-11) - DEPENDS ON LITERATURE SEARCH

**User Stories**:
- US5.1: As a researcher, I can define research question
- US5.2: As a researcher, I can set inclusion/exclusion criteria
- US5.3: As a researcher, I can run PRISMA screening
- US5.4: As a researcher, I can get PRISMA flow diagram
- US5.5: As a researcher, I can export study data

**Features**:
- [ ] PRISMA workflow builder
- [ ] Multi-source search (integrate Literature Search)
- [ ] Screening tool (title/abstract/full-text)
- [ ] Data extraction form
- [ ] PRISMA flow diagram generator
- [ ] Bias assessment tool (Cochrane ROB2)
- [ ] Study management

**Integration Points**:
- **paper-search-mcp**: Multi-source search
- **pubmed-mcp-server**: PubMed advanced search
- **Claude Scientific Skills**: PRISMA workflows
- **Literature Search**: Access to search APIs

**Testing (Ralph Loop)**:
1. Test: Create PRISMA review for Dr. Chen
2. Find problem: No inclusion/exclusion UI
3. Fix: Add criteria builder
4. Test again: UI works
5. Test: Run screening phase
6. Find problem: Can't bulk screen
7. Fix: Add bulk actions
8. Test again: Bulk screening works
9. Test: Generate PRISMA diagram
10. Find problem: Counts don't match
11. Fix: Fix counting logic
12. Test again: Diagram correct
13. Exit: All tests pass

**Debugging Time**: 12-18 hours (MED-HIGH risk)

---

#### Agent H: Citation Booster (Week 11) - DEPENDS ON LITERATURE SEARCH

**User Stories**:
- US11.1: As a researcher, I can paste a paragraph
- US11.2: As a researcher, I can see citation suggestions
- US11.3: As a researcher, I can insert citations
- US11.4: As a researcher, I can see relevance scores

**Features**:
- [ ] Text input/upload
- [ ] Citation suggestions (from Literature Search)
- [ ] Relevance scoring
- [ ] One-click insertion
- [ ] Citation completeness check

**Integration Points**:
- **paper-search-mcp**: Find relevant papers
- **OpenAI Embeddings**: Similarity scoring
- **Literature Search**: Access to search APIs

**Testing (Ralph Loop)**:
1. Test: Suggest citations for intro
2. Find problem: Suggestions irrelevant
3. Fix: Improve embedding similarity threshold
4. Test again: Relevant suggestions
5. Test: Insert citation
6. Find problem: Wrong format
7. Fix: Match document style
8. Test again: Format correct
9. Exit: All tests pass

**Debugging Time**: 6-8 hours (LOW-MED risk)

---

### Phase 12: Paraphraser (Week 12) - CAN BE PARALLEL

**User Stories**:
- US9.1: As a researcher, I can paste text
- US9.2: As a researcher, I can select paraphrase intensity
- US9.3: As a researcher, I can compare original vs paraphrase
- US9.4: As a researcher, I can preserve citations

**Features**:
- [ ] Text input (paste/upload)
- [ ] Paraphrase intensity (light, medium, strong)
- [ ] Side-by-side comparison
- [ ] Citation preservation
- [ ] Academic vocabulary enrichment

**Integration Points**:
- **OpenAI GPT-4**: Paraphrasing
- **Claude Scientific Skills**: Paraphrasing workflows

**Testing (Ralph Loop)**:
1. Test: Paraphrase abstract
2. Find problem: Meaning changed
3. Fix: Add meaning preservation constraint
4. Test again: Meaning preserved
5. Test: Paraphrase with citations
6. Find problem: Citations lost
7. Fix: Detect and preserve citations
8. Test again: Citations preserved
9. Exit: All tests pass

**Debugging Time**: 4-6 hours (LOW-MED risk)

---

### Phase 13: Deep Review (Week 13) - DEPENDS ON EVERYTHING

**User Stories**:
- US10.1: As a researcher, I can upload a paper
- US10.2: As a researcher, I can see strengths/weaknesses
- US10.3: As a researcher, I can get improvement suggestions
- US10.4: As a researcher, I can compare to similar papers

**Features**:
- [ ] Paper upload
- [ ] Automated critique (methods, results, discussion)
- [ ] Cross-paper comparison
- [ ] Suggestion generation
- [ ] Similarity analysis

**Integration Points**:
- **LangGraph**: Multi-agent analysis
- **Semantic Scholar API**: Similar paper lookup

**Testing (Ralph Loop)**:
1. Test: Analyze Dr. Chen's draft
2. Find problem: Methods section not analyzed
3. Fix: Add methods-specific prompts
4. Test again: All sections analyzed
5. Test: Find similar papers
6. Find problem: Only finds recent papers
7. Fix: Remove date filter
8. Test again: Historical papers found
9. Exit: All tests pass

**Debugging Time**: 8-12 hours (MEDIUM risk)

---

### Phase 14: E2E Testing with Agent-Browser (Week 14)

**Objective**: Comprehensive testing of all features using Dr. Chen's workflows

**Test Scenarios**:

##### Scenario 1: Literature Review Workflow
```bash
agent-browser open http://localhost:3000
# 1. Sign in as Dr. Chen
# 2. Search for "AI drug discovery"
# 3. Select top 10 papers
# 4. Export to BibTeX
# 5. Upload papers to Chat with PDF
# 6. Ask questions
# 7. Extract data
# 8. Verify outputs
```

**Ralph Loop**: Test → Find problem → Fix → Test again → Exit

##### Scenario 2: Systematic Review Workflow
```bash
agent-browser open http://localhost:3000/literature/new-review
# 1. Define research question
# 2. Set inclusion/exclusion criteria
# 3. Run PRISMA screening
# 4. Screen 20 papers
# 5. Generate PRISMA diagram
```

**Ralph Loop**: Test → Find problem → Fix → Test again → Exit

##### Scenario 3: AI Writer Workflow
```bash
agent-browser open http://localhost:3000/writing/new
# 1. Create project
# 2. Generate abstract
# 3. Check academic tone
# 4. Add citations
# 5. Export to LaTeX
```

**Ralph Loop**: Test → Find problem → Fix → Test again → Exit

##### Scenario 4: Full Nature Review Workflow (Dr. Chen's Goal)
```bash
# Step 1: Literature search (500+ papers)
# Step 2: Systematic screening
# Step 3: Data extraction (200 papers)
# Step 4: AI Writer (all sections)
# Step 5: Citation management
# Step 6: Export for Nature
```

**Ralph Loop**: Test → Find problem → Fix → Test again → Exit

**Exit Criteria**: All 4 test scenarios pass

---

### Phase 15: Polish & Launch (Week 15)

**Tasks**:
- [ ] Performance optimization
- [ ] Security audit
- [ ] Error handling review
- [ ] Documentation completion
- [ ] Beta testing with 20+ researchers
- [ ] Launch preparation

**Exit Criteria**: Ready for launch

---

## ✅ SUCCESS METRICS

### By Feature Completion
- [ ] All user stories pass Ralph Loop testing
- [ ] Agent-browser scenarios pass
- [ ] Dr. Chen approves functionality
- [ ] Documentation complete
- [ ] Code quality checks pass
- [ ] Performance metrics met (<500ms API, <2s UI)

### By Project Launch
- [ ] 11/11 features implemented
- [ ] 200+ test scenarios passing
- [ ] Dr. Chen successfully submits Nature review
- [ ] 20+ beta testers happy
- [ ] 100+ paying users (Month 1)
- [ ] $1,000+ MRR (Month 1)
- [ ] Ready for launch

---

## 🔄 HOW TO RECOVER FROM SESSION CRASH

### Step 1: Read ULTIMATE_BUILD_DIRECTIVE.md (This File) - 5 minutes

### Step 2: Read SESSION_MEMORY.md - 3 minutes

### Step 3: Read SPEC_DRIVEN_PLAN.md - 5 minutes

### Step 4: Continue from Last Completed Phase

### Step 5: Do NOT Restart from Beginning

---

## 🎯 WHAT TO TELL ME WHEN STARTING A NEW SESSION

### Template to Use

```
"I'm ready to start building my Sci-Space clone for academics.

Please read ULTIMATE_BUILD_DIRECTIVE.md to regain full context.

Important things to remember:
- I'm a non-technical founder
- I'm using Railway (frontend + backend) + Supabase (DB + auth + storage)
- I'm using Paddle (global) + Razorpay (India) for payments
- I'm using parallel development strategy with async agents
- Week 4-7: 5 independent features in parallel (Chat with PDF, Literature Search, Citation Generator, Data Extraction, AI Detector)
- Week 8-11: 3 dependent features sequentially (AI Writer, Systematic Review, Citation Booster)
- Week 12-14: Paraphraser, Deep Review, E2E Testing
- Week 15: Polish & Launch
- 90% of code comes from proven repos (LangChain, LlamaIndex, paper-search-mcp, pubmed-mcp-server, Unstructured, PDFPlumber, etc.)
- Only 10% is integration code we write + debug
- Expected debugging: 65 hours total over 15 weeks (4.3 hours/week)
- Most debugging is: UI tweaks, prompt tuning, algorithm refinement
- NOT debugging complex infrastructure
- Low-MEDIUM overall risk
- 90-95% probability of success

Start with [specify which phase, e.g., 'Phase 0: Spec-Driven Setup']"
```

### This Tells Me:

1. ✅ Project context and goal
2. ✅ Founder profile (non-technical, needs LLM help)
3. ✅ Tech stack choices (Railway + Supabase + Paddle/Razorpay)
4. ✅ Development strategy (parallel agents)
5. ✅ What weeks to do what (Week 4-7 parallel, Week 8-11 sequential)
6. ✅ Code breakdown (90% repos, 10% our code)
7. ✅ Debugging expectations (65 hours total, mostly UI/algorithms)
8. ✅ What to start with (specify phase)

---

## 🎯 I WILL NOT FORGET:

- ✅ Parallel development strategy (Week 4-7: 5 agents simultaneously)
- ✅ Sequential dependencies (AI Writer needs Literature Search, etc.)
- ✅ Ralph Loop methodology (Test → Fix → Test → Exit)
- ✅ 90% proven repos, 10% integration code
- ✅ 65 hours debugging expected (UI, prompts, algorithms)
- ✅ User is non-technical, needs LLM-friendly approach
- ✅ Deployment: Railway + Supabase + Paddle/Razorpay
- ✅ All context preserved in markdown files
- ✅ Recover from session crash by reading ULTIMATE_BUILD_DIRECTIVE.md
- ✅ When to use parallel (independent features, Week 4-7)
- ✅ When to use sequential (dependent features, Week 8-11)
- ✅ Dr. Chen's persona for testing
- ✅ All 11 features and their dependencies
- ✅ Spec-Driven Development methodology
- ✅ Agent-Browser E2E testing
- ✅ Quality gates per feature
- ✅ Success metrics

---

## 🚀 READY TO BEGIN?

When you're ready, simply say:

**"Start Phase 0"**

I will:
1. Install spec-kit
2. Initialize SDD project
3. Create project constitution
4. Write specification for all 11 features
5. Generate technical plan
6. Create task breakdown
7. Begin Phase 1 (Foundation)

**Estimated time for Phase 0**: 2-3 days

---

**Last Updated**: 2026-01-21
**Session ID**: sci-space-clone-001
**Project**: Sci-Space Clone for Academics
