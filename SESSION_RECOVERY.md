# SESSION RECOVERY & QUICK START GUIDE
# SCI-SPACE CLONE PROJECT

## 🎯 PROJECT STATUS

**Current Phase**: Planning Complete ✅
**Next Action**: Initialize spec-kit and begin Phase 0
**Total Duration**: 20 weeks (5 months)
**Features**: 11 core features for academics

## 📚 DOCUMENTATION INDEX

### Essential Files (Read in this order on session crash)

#### 1. SESSION_MEMORY.md (27KB) ⚡ QUICK START
**Read First**: Quick context recovery
**Contains**:
- Project context
- Features to build (11 items)
- Tech stack decisions (Railway + Supabase + Paddle)
- Repository list (24+ repos)
- Development phases summary
- Problems we're solving + how
- Next actions
**Purpose**: Fast context recovery, 5-minute read time

#### 2. SPEC_DRIVEN_PLAN.md (27KB) 📅 DETAILED PLAN
**Read Second**: Implementation roadmap
**Contains**:
- 20-week phased plan
- Detailed user stories per feature
- Integration points for new repos
- Testing scenarios (Dr. Chen)
- Success metrics per phase
- Contingency plans
**Purpose**: Complete roadmap, day-by-day tasks

#### 3. SESSION_RECOVERY.md (THIS FILE) 🆕 RECOVERY GUIDE
**Read Third**: Recovery instructions
**Contains**:
- Immediate recovery steps
- What to tell LLM to start building
- Problem-solving methodology
- Deployment setup instructions
- Cost breakdown
**Purpose**: Get unblocked fast, resume work

#### 4. REPOSITORIES.md (15KB) 🔧 REPO LIST
**Read Fourth**: All proven repos
**Contains**:
- 35+ proven GitHub repos
- License analysis (all MIT/Apache 2.0)
- Integration points for each
- New MCP servers (paper-search-mcp, pubmed-mcp-server)
- Claude Scientific Skills (140+ skills)
**Purpose**: Tech stack reference, ensure permissive licenses

#### 5. DEVELOPMENT_APPROACH.md (17KB) 📋 METHODOLOGY
**Optional**: Methodology explained
**Contains**:
- Spec-Driven Development explained
- Ralph Loop methodology
- Agent-Browser testing
- Phase-by-phase breakdown
- Quality gates per feature
- Risk mitigation strategies
**Purpose**: How we work, quality standards

#### 6. QUICK_START.md (8.7KB) 🚀 COMMANDS
**Optional**: Quick commands reference
**Contains**:
- Installation commands
- Database schema
- Core algorithms
- Troubleshooting guide
- Quick examples
**Purpose**: Copy-paste commands, get unblocked

#### 7. PROJECT_PLAN.md (4.0KB) 📋 OVERVIEW
**Optional**: High-level overview
**Contains**:
- Feature list
- Tech stack
- High-level phases
- Subscription tiers
**Purpose**: Big picture, executive summary

#### 8. IMPLEMENTATION_ROADMAP.md (23KB) 💻 CODE EXAMPLES
**Optional**: Detailed code examples
**Contains**:
- Step-by-step implementation
- Code snippets for each feature
- Database schemas
- API endpoints
**Purpose**: Deep dive, when coding specific features

## 🎭 TESTING PERSONA: DR. CHEN

### Background
- **PhD**: Computational Biology, MIT
- **Postdoc**: Stanford (AI/ML)
- **Current**: Assistant Professor, UC Berkeley
- **Publications**: Nature, Science, Cell

### Current Task
Submit a **state-of-the-art review on "AI-Powered Drug Discovery"** to **Nature**

### Dr. Chen's Requirements from Nature
- Comprehensive literature review (500+ papers)
- PRISMA methodology
- Data extraction from 200+ papers
- Visual analysis of trends
- Gap identification
- Future directions
- Publication-ready figures

### How Dr. Chen Will Test
1. ✅ Use EVERY feature of app
2. ✅ Test edge cases and failure modes
3. ✅ Validate all output formats
4. ✅ Check citation accuracy
5. ✅ Verify data extraction quality
6. ✅ Test collaboration features
7. ✅ Validate export capabilities
8. ✅ Simulate Nature submission workflow

## 🛠️ NEW REPOS INTEGRATED

### MCP Servers (Critical Integration)
1. **paper-search-mcp** ⭐ 550 (MIT) - 7+ academic databases
2. **pubmed-mcp-server** ⭐ 46 (Apache 2.0) - PubMed advanced features
3. **claude-scientific-skills** ⭐ 6.7k (MIT) - 140+ scientific skills

### Testing & Dev Tools
4. **agent-browser** ⭐ 9k (Apache 2.0) - Browser automation
5. **spec-kit** ⭐ 64k (MIT) - Spec-driven development

## 🎯 FINAL TECH STACK (DECIDED)

### Frontend
```
Next.js 14        (121k stars, MIT)  - App Router, Server Components
shadcn/ui         (71k stars, MIT)   - Beautiful, accessible components
Tailwind CSS        -                 - Styling
TanStack Table      (23k stars, MIT)   - Data tables for papers
agent-browser       (9k stars, Apache)  - E2E testing
```

### Backend
```
FastAPI            (77k stars, MIT)   - Python async, type-safe
LangChain            (125k stars, MIT)  - AI orchestration
LlamaIndex          (37k stars, Apache) - Document indexing
LangGraph            -                  - Multi-agent workflows
```

### MCP Servers
```
paper-search-mcp       (550 stars, MIT)      - 7+ academic databases
pubmed-mcp-server      (46 stars, Apache 2.0) - PubMed advanced features
claude-scientific-skills (6.7k stars, MIT) - 140+ scientific skills
```

### Database (CHOSEN)
```
Supabase (PostgreSQL + pgvector)
✅ Built-in pgvector extension
✅ Built-in Auth (no separate service!)
✅ Built-in Storage (for PDFs)
✅ Built-in Edge Functions
✅ Real-time capabilities
✅ Zero database administration
✅ Auto-backups
✅ Auto-scaling
```

### Authentication (CHOSEN)
```
Supabase Auth (built-in)
✅ No separate service needed
✅ Easy OAuth (Google, GitHub, etc.)
✅ Email/password
✅ MFA support
✅ $0 cost (included in Supabase)
✅ Simpler than Clerk!
```

### Payments (CHOSEN)
```
Paddle (for global users)
✅ USD/EUR/GBP pricing (native UX)
✅ Payouts to India
✅ No tax compliance needed
✅ Built for SaaS

Razorpay (for Indian users - optional)
✅ INR pricing
✅ UPI support
✅ 90%+ Indian payments

Hybrid approach:
✅ Automatic currency detection
✅ Route to appropriate provider
✅ Payouts to single Indian bank
```

### Deployment (CHOSEN)
```
Railway (Frontend + Backend)
✅ Single platform for both
✅ Easy deployment (git push)
✅ Zero server management
✅ Built-in monitoring
✅ Predictable pricing

Supabase (Database + Auth + Storage)
✅ All-in-one dashboard
✅ Built-in pgvector
✅ No database administration
✅ Real-time capabilities
```

### AI/ML
```
OpenAI GPT-4        - Main reasoning
Claude 3.5 Sonnet     - Alternative/better
HuggingFace Transformers (134k stars, Apache) - AI detector model
```

### PDF Processing
```
Unstructured.io (10k stars, Apache) - Document parsing
PDFPlumber       (5.5k stars, MIT)   - Table extraction
Camelot          (4.6k stars, MIT)   - Complex tables
```

### Academic APIs
```
PubMed           - Via pubmed-mcp-server
Google Scholar     - Via paper-search-mcp
ArXiv             - Via paper-search-mcp
Semantic Scholar   - Via paper-search-mcp
bioRxiv/medRxiv   - Via paper-search-mcp
IACR              - Via paper-search-mcp
BioPython         - PubMed via EDirect
```

## 📋 PROBLEMS WE'RE SOLVING

### Problem 1: Non-Technical Founder Constraints
**What Founder Struggles With:**
- ❌ Complex server management (VPS, SSH, Nginx, Docker)
- ❌ Multiple services integration difficulty (Firebase wiring)
- ❌ Time-consuming debugging of infrastructure
- ❌ Lack of technical knowledge for debugging
- ❌ Need for quick, reliable deployment

**How We Solve This:**
1. **Single Platform for Everything** (Railway)
   - Frontend + Backend on one platform
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

## 🎯 PARALLEL DEVELOPMENT STRATEGY (NEW)

### Stage 2: Parallel Execution (Week 4-7) - 5 Agents

**5 Independent Features Built Simultaneously:**
```
┌──────────────────────────────────────────┐
│  WEEK 4-7: PARALLEL SPRINT          │
├──────────────────────────────────────────┤
│                                       │
│  🤖 Agent A: Chat with PDF             │
│  🤖 Agent B: Literature Search          │
│  🤖 Agent C: Citation Generator        │
│  🤖 Agent D: Data Extraction           │
│  🤖 Agent E: AI Detector             │
│                                       │
│  All 5 work INDEPENDENTLY at once!   │
│  Each follows Ralph Loop independently   │
│  Each has separate spec in .specify/   │
│  Each has separate agent-browser tests   │
│                                       │
└──────────────────────────────────────────┘
```

**How Founder Coordinates This:**
```python
# In Session 1:
"Agent A, build Chat with PDF feature."

# In Session 2 (while Agent A is working):
"Agent B, build Literature Search feature."

# In Session 3 (while Agents A+B are working):
"Agent C, build Citation Generator feature."

# In Session 4 (while Agents A+B+C are working):
"Agent D, build Data Extraction feature."

# In Session 5 (while Agents A+B+C+D are working):
"Agent E, build AI Detector feature."
```

**All 5 features develop in parallel!** No waiting for sequential completion.

### Stage 3: Sequential Execution (Week 8-11) - 3 Agents

**3 Features That Depend on Literature Search:**
```
┌──────────────────────────────────────────┐
│  WEEK 8-11: SEQUENTIAL SPRINT        │
├──────────────────────────────────────────┤
│                                       │
│  Wait for Literature Search (Agent B)   │
│         ↓                           │
│  🤖 Agent F: AI Writer               │
│  🤖 Agent G: Systematic Review        │
│  🤖 Agent H: Citation Booster        │
│                                       │
│  All 3 depend on Literature Search    │
│                                       │
└──────────────────────────────────────────┘
```

**Each follows Ralph Loop**: Test → Fix → Test → Exit

### Stage 4: Final Stages (Week 12-14)

- Week 12: Paraphraser (Can be independent, sequential for simplicity)
- Week 13: Deep Review (Depends on EVERYTHING - must be last)
- Week 14: E2E Testing (Agent-browser validates all features)
- Week 15: Polish & Launch

### Timeline Comparison

| Approach | Duration | Saved |
|----------|----------|-------|
| Sequential (Original) | 20 weeks | - |
| Parallel (New) | 15 weeks | 5 weeks (25% faster) |

### When to Use Each Approach

**Parallel** - When features are INDEPENDENT:
- No shared dependencies
- No shared database tables (initially)
- Can work in separate code areas

**Sequential** - When features are DEPENDENT:
- Need data from another feature
- Use APIs from another feature
- Share complex business logic

## 📋 TIMELINE COMPARISON

### Original Plan (Sequential - 20 weeks)

```
Week 1:    Spec-Driven Setup
Week 2-3:  Foundation
Week 4-5:  Chat with PDF
Week 6-7:  Literature Search
Week 8-9:  AI Writer
Week 10-11:  Systematic Review
Week 12:    Citation Generator
Week 13:    Data Extraction
Week 14:    AI Detector
Week 15:    Paraphraser
Week 16:    Deep Review
Week 17:    Citation Booster
Week 18-19:  E2E Testing
Week 20:    Polish & Launch
```

### Updated Plan (Parallel - 15 weeks)

```
Week 1:    Spec-Driven Setup
Week 2-3:  Foundation (Sequential, all features depend on this)
Week 4-7:  PARALLEL SPRINT (5 independent features)
            ├─ Agent A: Chat with PDF
            ├─ Agent B: Literature Search
            ├─ Agent C: Citation Generator
            ├─ Agent D: Data Extraction
            └─ Agent E: AI Detector
Week 8-11:  SEQUENTIAL SPRINT (3 dependent features)
            ├─ Agent F: AI Writer (depends on Lit Search)
            ├─ Agent G: Systematic Review (depends on Lit Search)
            └─ Agent H: Citation Booster (depends on Lit Search)
Week 12:    Paraphraser (Sequential for simplicity)
Week 13:    Deep Review (Depends on EVERYTHING - must be last)
Week 14:    E2E Testing (Agent-browser validates everything)
Week 15:    Polish & Launch

Total: 15 weeks (3.5 months)
Savings: 5 weeks (30% faster)
```

### Week 1: Spec-Driven Setup
- [ ] Initialize spec-kit
- [ ] Create constitution
- [ ] Write specification (11 features)
- [ ] Generate technical plan
- [ ] Create task breakdown

### Week 2-3: Foundation (Railway + Supabase + Paddle)
- [ ] Create Railway account
- [ ] Create Railway service (Frontend + Backend)
- [ ] Create Supabase project
- [ ] Enable pgvector in Supabase
- [ ] Create Supabase auth tables
- [ ] Create Paddle account
- [ ] Create Razorpay account (if needed for India)
- [ ] Dashboard UI
- [ ] User profile management
- [ ] Hybrid payment integration

### Week 4-5: Chat with PDF
- [ ] PDF upload endpoint (Railway backend)
- [ ] PDF processing (Unstructured + PDFPlumber)
- [ ] Text chunking (500-1000 tokens)
- [ ] Embedding generation (OpenAI)
- [ ] Vector storage (Supabase pgvector)
- [ ] RAG chain (LangChain)
- [ ] Chat UI with streaming
- [ ] Source citation

### Week 6-7: Literature Search
- [ ] paper-search-mcp integration (MCP server)
- [ ] pubmed-mcp-server integration (MCP server)
- [ ] Multi-source aggregator
- [ ] Result deduplication
- [ ] Citation export (BibTeX, RIS, APA, MLA)
- [ ] Search history
- [ ] Save to library

### Week 8-9: AI Writer
- [ ] Writing project management
- [ ] Section-by-section generation
- [ ] Academic tone enforcement
- [ ] Citation insertion
- [ ] Version history
- [ ] Export to LaTeX/Word

### Week 10-11: Systematic Review
- [ ] PRISMA workflow builder
- [ ] Multi-source search
- [ ] Screening tool
- [ ] Data extraction form
- [ ] PRISMA flow diagram
- [ ] Bias assessment (Cochrane ROB2)

### Week 12: Citation Generator
- [ ] Citation input form (DOI fetch)
- [ ] 20+ styles
- [ ] Batch generation
- [ ] Bibliography management
- [ ] Export to multiple formats

### Week 13: Data Extraction
- [ ] PDFPlumber + Camelot integration
- [ ] Table extraction
- [ ] Figure detection
- [ ] Caption extraction
- [ ] CSV/Excel export

### Week 14: AI Detector
- [ ] HuggingFace model integration
- [ ] Text input/upload
- [ ] AI probability score
- [ ] Highlighting (AI vs human)

### Week 15: Paraphraser
- [ ] Text input
- [ ] Paraphrase intensity
- [ ] Side-by-side comparison
- [ ] Citation preservation

### Week 16: Deep Review
- [ ] Paper upload
- [ ] Automated critique
- [ ] Cross-paper comparison
- [ ] Similarity analysis

### Week 17: Citation Booster
- [ ] Text input
- [ ] Literature search integration
- [ ] Relevance scoring
- [ ] One-click insertion

### Week 18-19: E2E Testing (Agent-Browser)
- [ ] Scenario 1: Literature review workflow
- [ ] Scenario 2: Systematic review workflow
- [ ] Scenario 3: AI writer workflow
- [ ] Scenario 4: Full Nature submission (Dr. Chen's goal)

**Ralph Loop for Each Scenario**: Test → Fix → Test → Exit

### Week 20: Polish & Launch
- [ ] Performance optimization
- [ ] Security audit
- [ ] Documentation completion
- [ ] Beta testing (20+ researchers)
- [ ] Launch preparation

## 🔄 RALPH LOOP PROCESS

### For EACH Feature

```python
ralph_loop(feature):
    while not feature_complete:
        result = test_feature(feature)
        if result.success:
            feature_complete = True
            log("✅ Feature complete!")
        else:
            problem = identify_problem(result)
            log(f"❌ Problem: {problem}")
            fix = create_fix(problem)
            apply_fix(fix)
            log("🔧 Fix applied, testing again...")
```

### Exit Criteria (Before Moving Forward)
- [ ] All user stories pass
- [ ] Agent-browser tests pass
- [ ] Dr. Chen approves functionality
- [ ] No critical bugs
- [ ] Performance metrics met (<500ms API, <2s UI)
- [ ] Security review passed
- [ ] Documentation complete

## 📊 SUCCESS METRICS

### By Phase Completion
- [ ] All user stories work
- [ ] Ralph loop passed (Test → Fix → Test → Exit)
- [ ] Dr. Chen validated
- [ ] Documented

### By Project Launch
- [ ] 11/11 features complete
- [ ] 200+ test scenarios pass
- [ ] Dr. Chen submits Nature review
- [ ] 20+ beta testers happy
- [ ] 100+ paying users (Month 1)
- [ ] $1,000+ MRR (Month 1)

## 💰 COST TRACKING

### Monthly Operating Costs (Expected)
- Railway (Frontend + Backend): $20/month
- Supabase (DB + Auth + Storage): $0 → $25/month
- AI APIs (OpenAI + Claude): $50-130/month
- Paddle: $0/month + variable fees
- Razorpay: $0/month + variable fees (India)
- **Total: $70-175/month** (startup phase)

### Revenue (Month 1 Goal)
- 100 users @ $19/mo (Pro): $1,900
- 20 users @ $49/mo (Team): $980
- **Total: $2,880/month**

### Net (Month 1 Goal)
$2,880 - $175 = **$2,705/month**

## 🎯 NEXT ACTIONS (IMMEDIATE)

### Right Now (Today)
1. ✅ Read SESSION_RECOVERY.md (you're here!)
2. Review SESSION_MEMORY.md
3. Review SPEC_DRIVEN_PLAN.md
4. ✅ Approved tech stack (Railway + Supabase + Paddle)
5. **Wait for user to start**

### When Ready to Begin
```bash
# 1. Navigate to project
cd /Users/shaileshsingh/V1\ draft

# 2. Install spec-kit
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git

# 3. Initialize spec-kit project
specify init . --ai claude

# 4. Create constitution
/speckit.constitution

# 5. Create specification
/speckit.specify

# 6. Create technical plan
/speckit.plan

# 7. Generate tasks
/speckit.tasks

# 8. Start implementation
/speckit.implement
```

## ⚠️ IMPORTANT REMINDERS

### Before Starting
1. **Approved Plan**: Read all documents, agreed on approach
2. **Install Dependencies**: spec-kit, agent-browser, uv
3. **Set Up Environment**: Create Railway account, Supabase project, Paddle account
4. **Configure Services**: Get API keys (OpenAI, Paddle, Razorpay)

### During Development
1. **Follow Ralph Loop**: Test → Fix → Test → Exit (never abandon)
2. **Use Dr. Chen's Workflow**: Test as if submitting to Nature
3. **Update SESSION_MEMORY.md**: After each major milestone
4. **Commit Frequently**: Small commits with clear messages
5. **Run Ralph Loop After Each Feature**: Before marking complete

### If Session Crashes
1. **Read SESSION_MEMORY.md** first (5 minutes)
2. **Read SESSION_RECOVERY.md** second (5 minutes)
3. **Read SPEC_DRIVEN_PLAN.md** third (15 minutes)
4. **Continue** from last completed phase
5. **Do NOT Restart** from beginning

### Quality Gates
- **Never Skip Ralph Loop Testing**
- **Never Mark Feature Complete Without Tests Passing**
- **Never Abandon Features - Fix Until They Work**
- **Always Get Dr. Chen's Approval Before Moving On**
- **Always Document Problems and Fixes**

## 💡 WHAT TO TELL LLM WHEN STARTING

### When you start a new session and want me to build:

```
"I'm ready to start building the Sci-Space clone.
Please read SESSION_MEMORY.md to regain context.
We're using Railway (frontend + backend) + Supabase (DB + auth + storage) + Paddle/Razorpay (payments).
Start with Phase 0: Spec-Driven Setup."
```

This tells me:
1. ✅ What project we're building
2. ✅ What tech stack to use
3. ✅ Where to recover context
4. ✅ What phase to start
5. ✅ What methodology to follow

---

## 🚀 READY TO BEGIN?

When you're ready, say:
**"Start Phase 0"** and I will:
1. Initialize spec-kit
2. Create project constitution
3. Write specification
4. Generate technical plan
5. Create task breakdown

**Estimated time for Phase 0**: 2-3 days

---

**Last Updated**: 2026-01-21
**Session ID**: sci-space-clone-001
**Project**: Sci-Space Clone for Academics
