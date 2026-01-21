# DEVELOPMENT APPROACH SUMMARY
# SCI-SPACE CLONE PROJECT

## HOW WE WILL BUILD THIS

### 1. Spec-Driven Development (SDD)

**What it is**: A structured development methodology where specifications are **execuable** and define WHAT before HOW.

**What it is**: A structured development methodology where specifications are **execuable** and define WHAT before HOW.

**Why we use it**:
- **Context Preservation**: Survives crashes and context loss
- **Reprocible Process**: Same methodology every time
- **Intent-First**: Define requirements before choosing tech
- **Quality Gates**: Built-in checklists for completeness

**How it works**:
```
1. Constitution → 2. Specification → 3. Plan → 4. Tasks → 5. Implementation
                      ↓                ↓              ↓           ↓              ↓
                    Refine          Clarify       Execute     Code
                      ↓                ↓              ↓           ↓
                  Better Spec     Clear Tasks   Testing   Features
```

**Commands**:
```bash
# Install
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git

# Initialize in project
cd /Users/shaileshsingh/V1\ draft
specify init . --ai claude

# Key commands (available after init)
/speckit.constitution  # Create project principles
/speckit.specify       # Define what to build (user stories)
/speckit.plan           # Create technical implementation plan
/speckit.tasks          # Generate actionable task list
/speckit.clarify       # Clarify underspecified areas
/speckit.analyze        # Cross-artifact consistency analysis
/speckit.checklist      # Generate quality checklists
/speckit.implement      # Execute implementation
```

**Artifacts Generated**:
- `.specify/memory/constitution.md` - Project principles
- `.specify/specs/XXX-feature/spec.md` - User stories & requirements
- `.specify/specs/XXX-feature/plan.md` - Technical architecture
- `.specify/specs/XXX-feature/tasks.md` - Actionable task breakdown
- `.specify/specs/XXX-feature/data-model.md` - Database schemas
- `.specify/specs/XXX-feature/api-contracts/` - API specs

### 2. Ralph Loop Methodology

**What it is**: Test → Find Problem → Fix → Test Again → Exit When Complete

**Why we use it**:
- **Quality Focus**: Never abandon features, fix until they work
- **Learning**: Every bug fix is documented
- **Iterative**: Gradual improvement, not all-or-nothing
- **Exit Criteria**: Clear definition of "done" before testing

**How it works for each feature**:
```
1. Implement Feature (from /speckit.tasks)
2. Write E2E test (agent-browser scenario)
3. Run Test
4. Identify Problem
5. Fix Problem
6. Run Test Again
7. Repeat 3-6 until no problems
8. Exit: Feature complete
```

**Example: Chat with PDF**
```python
# 1. Implement
async def upload_pdf(file: UploadFile):
    text = await extract_text(file)
    chunks = await split_text(text)
    await store_embeddings(chunks)
    return {"status": "success"}

# 2. Write Test
# tests/scenarios/chat-with-pdf.workflow
agent-browser open http://localhost:3000
agent-browser click "#upload-pdf"
agent-browser upload "#file-input" "test_paper.pdf"
agent-browser wait --text "Processed"

# 3. Run Test
# EXECUTED: FAILS - "Chunking error"

# 4. Identify Problem
# Error: Text chunks too small (50 tokens), retrieval poor

# 5. Fix Problem
async def split_text(text: str):
    return split_into_chunks(text, min_tokens=500, max_tokens=1000)

# 6. Test Again
# EXECUTED: PASSES - Chunks correct size

# 7. Repeat until no problems
# No more problems found

# 8. Exit: Feature Complete
# Mark as completed in tasks.md
```

### 3. Agent-Based E2E Testing

**What it is**: Automated browser testing simulating real user workflows

**Why we use it**:
- **UI Validation**: Catch issues code reviews miss
- **Integration Testing**: Verify end-to-end flows work
- **Real User Scenarios**: Test as Dr. Chen would use the app
- **Reprocible**: Same test runs identically every time

**How it works**:
```bash
# Install
npm install -g agent-browser
agent-browser install

# Test Scenarios (automated scripts)
agent-browser open http://localhost:3000
agent-browser snapshot -i --json  # Get UI elements
agent-browser click @e2                # Interact using refs
agent-browser fill @e3 "input"        # Fill forms
agent-browser screenshot test.png          # Verify visual state
```

**Dr. Chen's Workflow Tests**:
1. **Literature Review Workflow** - Search, save, export
2. **Systematic Review Workflow** - PRISMA screening, data extraction
3. **AI Writer Workflow** - Generate sections, insert citations, export
4. **Full Nature Submission** - End-to-end from search to submission

## OUR TECH STACK (FINAL)

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

### MCP Servers (NEW - CRITICAL)
```
paper-search-mcp       (550 stars, MIT)      - 7+ academic databases
pubmed-mcp-server      (46 stars, Apache 2.0) - PubMed advanced features
claude-scientific-skills (6.7k stars, MIT) - 140+ scientific skills
```

### Database
```
PostgreSQL + pgvector - Combined relational + vector search
- Avoids separate vector DB
- ACID compliance
- Easy scaling
```

### AI/ML
```
OpenAI GPT-4        - Main reasoning
Claude 3.5 Sonnet     - Alternative/better
HuggingFace Transformers (134k stars, Apache) - AI detector model
```

### Authentication & Payments
```
Clerk  (8.4k stars, MIT) - Auth (OAuth, MFA, user management)
Stripe (5.7k stars, MIT) - Subscriptions, invoicing
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

## DEVELOPMENT PHASES (20 Weeks Total)

### Phase 0: Spec-Driven Setup (Week 1)
**Objective**: Establish methodology and constitution
**Deliverables**:
- [ ] spec-kit initialized
- [ ] Constitution created (principles, quality gates)
- [ ] Specification created (11 features with user stories)
- [ ] Technical plan created (architecture, API contracts)
- [ ] Tasks generated (breakdown by user story)

**Ralph Loop Exit Criteria**: All deliverables complete, user approved

### Phase 1: Foundation (Week 2-3)
**Objective**: Auth, database, basic UI
**Deliverables**:
- [ ] Clerk authentication (Google, GitHub, Email/Password)
- [ ] Stripe subscriptions (Free, Pro, Team)
- [ ] PostgreSQL + pgvector setup
- [ ] Dashboard UI
- [ ] User profile management

**Ralph Loop Exit Criteria**: Dr. Chen can sign up, upgrade, access dashboard

### Phase 2: Chat with PDF (Week 4-5)
**Objective**: Upload, process, chat with documents
**Deliverables**:
- [ ] PDF upload endpoint
- [ ] PDF processing (Unstructured + PDFPlumber)
- [ ] Text chunking (500-1000 tokens)
- [ ] Embedding generation
- [ ] Vector storage (pgvector)
- [ ] RAG chain (LangChain)
- [ ] Chat UI (real-time streaming)
- [ ] Source citation in responses

**Ralph Loop Exit Criteria**: Dr. Chen uploads PDF, asks question, gets answer with page refs

### Phase 3: Literature Search (Week 6-7)
**Objective**: Multi-source academic paper search
**Deliverables**:
- [ ] paper-search-mcp integration (MCP server)
- [ ] pubmed-mcp-server integration (MCP server)
- [ ] Multi-source search aggregator
- [ ] Result deduplication
- [ ] Citation export (BibTeX, RIS, APA, MLA)
- [ ] Search history
- [ ] Save to library

**Ralph Loop Exit Criteria**: Dr. Chen searches 7+ databases, exports citations, saves to library

### Phase 4: AI Writer (Week 8-9)
**Objective**: AI-assisted academic paper writing
**Deliverables**:
- [ ] Writing project management
- [ ] Section-by-section generation (GPT-4)
- [ ] Academic tone enforcement
- [ ] Citation insertion
- [ ] Version history
- [ ] Export to multiple formats

**Ralph Loop Exit Criteria**: Dr. Chen generates abstract/intro/methods, inserts citations, exports LaTeX

### Phase 5: Systematic Review (Week 10-11)
**Objective**: PRISMA-compliant systematic review
**Deliverables**:
- [ ] PRISMA workflow builder
- [ ] Multi-source search
- [ ] Screening tool
- [ ] Data extraction form
- [ ] PRISMA flow diagram generator
- [ ] Bias assessment tool

**Ralph Loop Exit Criteria**: Dr. Chen completes full PRISMA review, generates diagram

### Phase 6: Citation Generator (Week 12)
**Objective**: Generate citations in multiple styles
**Deliverables**:
- [ ] Citation input form (auto-fetch from DOI)
- [ ] 20+ citation styles
- [ ] Batch generation
- [ ] Bibliography management
- [ ] Export to multiple formats

**Ralph Loop Exit Criteria**: Dr. Chen generates 50+ citations in APA, MLA, BibTeX

### Phase 7: Data Extraction (Week 13)
**Objective**: Extract tables/figures from PDFs
**Deliverables**:
- [ ] Table extraction (PDFPlumber + Camelot)
- [ ] Figure detection
- [ ] Caption extraction
- [ ] CSV/Excel export

**Ralph Loop Exit Criteria**: Dr. Chen extracts tables from 10+ papers, exports to CSV

### Phase 8: AI Detector (Week 14)
**Objective**: Detect AI-generated content
**Deliverables**:
- [ ] Text input/upload
- [ ] AI probability score
- [ ] Highlighting (AI vs human)
- [ ] Document-level analysis

**Ralph Loop Exit Criteria**: Dr. Chen analyzes paper, gets accurate AI probability

### Phase 9: Paraphraser (Week 15)
**Objective**: Academic paraphrasing tool
**Deliverables**:
- [ ] Text input
- [ ] Paraphrase intensity (light, medium, strong)
- [ ] Side-by-side comparison
- [ ] Citation preservation

**Ralph Loop Exit Criteria**: Dr. Chen paraphrases abstract, preserves meaning and citations

### Phase 10: Deep Review (Week 16)
**Objective**: Comprehensive paper analysis
**Deliverables**:
- [ ] Paper upload
- [ ] Automated critique
- [ ] Cross-paper comparison
- [ ] Suggestion generation
- [ ] Similarity analysis

**Ralph Loop Exit Criteria**: Dr. Chen uploads draft, gets comprehensive review

### Phase 11: Citation Booster (Week 17)
**Objective**: Suggest additional citations
**Deliverables**:
- [ ] Text input
- [ ] Citation suggestions
- [ ] Relevance scoring
- [ ] One-click insertion

**Ralph Loop Exit Criteria**: Dr. Chen pastes paragraph, gets 10+ relevant citations

### Phase 12: E2E Testing (Week 18-19)
**Objective**: Comprehensive testing with agent-browser
**Deliverables**:
- [ ] Scenario 1: Literature review workflow
- [ ] Scenario 2: Systematic review workflow
- [ ] Scenario 3: AI writer workflow
- [ ] Scenario 4: Full Nature submission

**Ralph Loop for Each Scenario**: Test → Find Problem → Fix → Test → Exit
**Exit Criteria**: All 4 scenarios pass, Dr. Chen approves

### Phase 13: Polish & Launch (Week 20)
**Objective**: Performance, security, documentation, launch
**Deliverables**:
- [ ] Performance optimization (<2s page load, <500ms API)
- [ ] Security audit (no secrets, input validation, rate limiting)
- [ ] Documentation (dev, API, user)
- [ ] Beta testing (20+ researchers)
- [ ] Launch preparation

**Ralph Loop Exit Criteria**: All quality gates pass, ready for launch

## QUALITY GATES

### Per-Feature Quality Gates
Before marking feature complete:
1. ✅ All user stories work as specified
2. ✅ Agent-browser tests pass (all scenarios)
3. ✅ Error handling (graceful messages, no crashes)
4. ✅ Performance (<2s page load, <500ms API)
5. ✅ Accessibility (WCAG 2.1 AA compliant)
6. ✅ Mobile responsive
7. ✅ Code quality (type hints, no console errors)
8. ✅ API docs updated
9. ✅ **Dr. Chen Approval** - Real researcher validates functionality

### Project-Wide Quality Gates
Before launch:
1. ✅ All 11 features implemented
2. ✅ Integration tests pass (all features work together)
3. ✅ Security audit complete
4. ✅ Performance metrics met (p95 targets)
5. ✅ Uptime 99.9%
6. ✅ Backup strategy in place
7. ✅ Monitoring configured
8. ✅ Documentation complete (dev, API, user)
9. ✅ Beta test results (20+ researchers, 80%+ satisfaction)
10. ✅ **Dr. Chen successfully submits Nature review** - Ultimate validation

## RISK MITIGATION

### Integration Complexity
**Risk**: 3 MCP servers + multiple APIs = complex
**Mitigation**:
- Start with paper-search-mcp (aggregates 7 databases)
- Add pubmed-mcp-server for PubMed advanced features
- Use claude-scientific-skills as fallback/reference
- Document all MCP interaction patterns

### AI Model Costs
**Risk**: OpenAI costs spiral with 100+ beta testers
**Mitigation**:
- Use GPT-4o-mini for simple tasks
- Cache frequent queries (literature searches)
- Rate limit per user tier
- Monitor costs daily, alert at $50/day
- Implement usage quotas

### Performance with Large PDFs
**Risk**: 50+ page PDFs timeout or crash
**Mitigation**:
- Streaming processing (show progress)
- Async workers for heavy tasks
- 5-minute timeout per PDF
- Queue system for concurrent uploads
- Clear error messages with retry options

### API Rate Limits
**Risk**: PubMed/Scholar block users
**Mitigation**:
- Multi-layer caching (Redis + database)
- Multiple API keys if needed
- Queue system with rate limit awareness
- Show status to users ("3 searches left this hour")

### Dr. Chen's Review Rejected
**Risk**: Nature rejects AI-generated review
**Mitigation**:
- Use claude-scientific-skills for Nature-specific guidance
- Get peer review from another academic (beta tester)
- Validate against Nature template exactly
- Test multiple drafts, pick best
- Human-in-the-loop editing before submission

## SUCCESS METRICS

### Feature Completion
- **11/11 features** implemented
- **50+ user stories** completed
- **200+ test scenarios** passing
- **Dr. Chen's Nature review** submitted

### Quality Metrics
- **95%+** test coverage
- **<500ms** API response (p95)
- **<2s** page load (p95)
- **0** critical bugs
- **<5** minor bugs

### User Success (Beta)
- **20+** beta testers
- **80%+** feature usage
- **4.5+** average rating
- **<5%** feature abandonment

### Business Metrics (Launch)
- **100+** paying users (Month 1)
- **500+** total users (Month 1)
- **<5%** churn (Month 1)
- **$1,000+** MRR (Month 1)

## NEXT ACTIONS (RIGHT NOW)

### Today
1. ✅ Read this summary
2. ✅ Review methodology with user
3. ✅ Get approval to proceed
4. Install spec-kit
5. Initialize spec-kit project

### This Week
1. Complete Phase 0 (Spec-Driven Setup)
2. Create constitution with user input
3. Write specification for all 11 features
4. Generate technical plan
5. Create task breakdown

### Next Week
1. Begin Phase 1 (Foundation)
2. Implement authentication
3. Set up database
4. Build basic UI
5. First Ralph loop tests

## DOCUMENTATION STRUCTURE

All context is preserved in these files:

```
/Users/shaileshsingh/V1 draft/
├── DEVELOPMENT_APPROACH.md    # THIS FILE - Methodology summary
├── SPEC_DRIVEN_PLAN.md        # Detailed 20-week plan
├── SESSION_MEMORY.md           # Session context & quick reference
├── REPOSITORIES.md            # All repos with licenses
├── PROJECT_PLAN.md             # Original high-level plan
├── QUICK_START.md             # Quick reference guide
├── .specify/                 # Spec-kit artifacts (after init)
│   ├── memory/
│   │   └── constitution.md
│   ├── specs/
│   │   ├── XXX-feature/
│   │   │   ├── spec.md
│   │   │   ├── plan.md
│   │   │   ├── tasks.md
│   │   │   ├── data-model.md
│   │   │   └── api-contracts/
│   └── templates/
├── client/                    # Next.js frontend (after start)
├── server/                    # FastAPI backend (after start)
└── tests/                     # Agent-browser scenarios (after start)
```

## RECOVERY PROCEDURE

If session crashes:

1. **Read SESSION_MEMORY.md** - Quick context recovery
2. **Read SPEC_DRIVEN_PLAN.md** - Detailed plan
3. **Read DEVELOPMENT_APPROACH.md** - Methodology
4. **Read REPOSITORIES.md** - All repos
5. **Run** `specify check` - Verify tools
6. **Continue** from last completed phase

## FINAL NOTES

### What Makes This Approach Unique

1. **Spec-First**: Define WHAT before HOW, ensure we build the right thing
2. **Never Abandon**: Ralph loop means we fix until features work
3. **Context Preservation**: spec-kit survives crashes and context loss
4. **Real Validation**: Dr. Chen's actual Nature review workflow
5. **Proven Tech Stack**: All repos battle-tested, permissive licenses
6. **Comprehensive Testing**: Agent-browser validates real user flows

### Expected Outcome

- **20 weeks** to fully functional product
- **11 features** that actually work (tested thoroughly)
- **Dr. Chen can submit** her Nature review
- **Launch-ready** with documentation and monitoring
- **100+ paying users** by Month 1

### Why This Will Succeed

1. **Structure**: Spec-kit provides methodology, not just coding
2. **Quality**: Ralph loop ensures features work, not abandoned
3. **Validation**: Agent-browser tests real workflows, not unit tests
4. **Speed**: Proven repos = 6+ months saved
5. **Focus**: Dr. Chen's persona = real user needs
6. **Resilience**: Context preserved across crashes

---

**Ready to begin?** Run `specify init . --ai claude` to start Phase 0!
