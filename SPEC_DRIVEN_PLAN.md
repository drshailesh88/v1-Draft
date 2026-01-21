# SPEC-DRIVEN DEVELOPMENT PLAN
# SCI-SPACE CLONE FOR ACADEMICS

## DEVELOPMENT METHODOLOGY

### Spec-Driven Development (SDD)
Using **github/spec-kit** to ensure:
- Intent-driven development (specifications define "what" before "how")
- Rich specification creation with guardrails
- Multi-step refinement (not one-shot code generation)
- Context preservation across sessions
- Reproducible development process

### Ralph Loop Methodology
Using **anthropics/claude-plugins-official/plugins/ralph-loop** for:
- Test → Find problem → Fix → Test again → Exit when complete
- No abandoning features - we fix until it works
- Iterative refinement based on testing results
- Quality gates before moving forward

### Browser-Based Testing
Using **vercel-labs/agent-browser** for:
- Automated E2E testing of all features
- Simulating real user workflows
- Validating functionality from UI perspective
- Catching integration issues early

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
- Will use EVERY feature of the app
- Will test edge cases and failure modes
- Will validate all output formats
- Will check citation accuracy
- Will verify data extraction quality
- Will test collaboration features
- Will validate export capabilities

## ADDITIONAL REPOS TO INTEGRATE

### 1. paper-search-mcp (MIT License) ⭐ 550
**URL**: https://github.com/openags/paper-search-mcp
**Use**: Multi-source paper search (arXiv, PubMed, bioRxiv, medRxiv, Google Scholar, IACR, Semantic Scholar)
**Integration Point**: Literature search feature
**Why**: Already aggregates 7+ academic databases - saves integration time

### 2. pubmed-mcp-server (Apache 2.0) ⭐ 46
**URL**: https://github.com/cyanheads/pubmed-mcp-server
**Use**: PubMed-specific advanced search, citation networks, research planning
**Integration Point**: PubMed integration in literature search
**Why**: Production-grade MCP server with robust NCBI E-utilities integration

### 3. claude-scientific-skills (MIT License) ⭐ 6.7k
**URL**: https://github.com/K-Dense-AI/claude-scientific-skills
**Use**: 140+ scientific skills for specialized tasks
**Integration Points**:
- Literature review workflows
- Scientific writing assistance
- Data analysis
- Visualization generation
**Why**: Pre-built, tested scientific workflows - accelerates development

## REVISED TECH STACK

### Enhanced Stack with New Integrations

#### Frontend
- **Next.js 14** (App Router)
- **shadcn/ui** (UI components)
- **Tailwind CSS**
- **TanStack Table** (Data tables)
- **agent-browser** (for automated testing)

#### Backend
- **FastAPI** (Python)
- **LangChain** (AI orchestration)
- **LlamaIndex** (Document indexing)
- **paper-search-mcp** (MCP server for multi-source search)
- **pubmed-mcp-server** (MCP server for PubMed)
- **Claude Scientific Skills** (as MCP integration)

#### AI/ML
- **OpenAI GPT-4** (Main reasoning)
- **Claude 3.5 Sonnet** (Alternative/better tasks)
- **LangGraph** (Multi-agent workflows from LangChain)

#### Databases
- **PostgreSQL + pgvector** (Combined relational + vector search)

#### Infrastructure
- **spec-kit** (Spec-driven development)
- **Docker** (Containerization)
- **Railway/Vercel** (Deployment)

## DEVELOPMENT PHASES (UPDATED)

### Phase 0: Spec-Driven Setup (Week 1)
**Objective**: Establish SDD methodology and project constitution

#### Step 0.1: Initialize Spec-Kit
```bash
cd /Users/shaileshsingh/V1\ draft
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
specify init . --ai claude
```

#### Step 0.2: Create Project Constitution
Run `/speckit.constitution` to establish:
- Code quality principles (TypeScript strict, Python type hints)
- Testing standards (80%+ coverage, E2E tests)
- UX consistency principles (accessibility, responsive design)
- Performance requirements (<2s page load, <500ms API response)
- Security standards (no secrets in code, input validation)

#### Step 0.3: Create Specification
Run `/speckit.specify` to define:
- All 11 features with user stories
- Dr. Chen's persona requirements
- Integration points for new repos
- Non-functional requirements (scalability, reliability)

#### Step 0.4: Create Technical Plan
Run `/speckit.plan` with tech stack:
- Detailed architecture
- API contracts
- Database schemas
- Integration patterns

#### Step 0.5: Generate Tasks
Run `/speckit.tasks` to break down:
- Feature by feature
- User story by user story
- Dependency mapping
- Parallel execution markers

### Phase 1: Foundation (Week 2-3)
**Objective**: Auth, database, basic UI
**IMPORTANT**: This phase MUST be complete before any parallel agents start - all features depend on this.

- [ ] Create Railway account and project
- [ ] Create Supabase project
- [ ] Enable pgvector in Supabase
- [ ] Create Supabase auth tables (users, profiles)
- [ ] Create Paddle account and products (Free, Pro, Team)
- [ ] Create Razorpay account (if needed for Indian users)
- [ ] Hybrid payment integration (Paddle for global, Razorpay for India)
- [ ] Dashboard UI
- [ ] User profile management

**Exit Criteria**: All auth, database, payments working. Railway + Supabase + Paddle/Razorpay operational.

### PARALLEL DEVELOPMENT STRATEGY (NEW)

**Overview**: Week 4-7 will run 5 independent features in parallel using async agents

**What Can Be Parallel (Week 4-7)**:
- ✅ Agent A: Chat with PDF (INDEPENDENT)
- ✅ Agent B: Literature Search (INDEPENDENT)
- ✅ Agent C: Citation Generator (INDEPENDENT)
- ✅ Agent D: Data Extraction (INDEPENDENT)
- ✅ Agent E: AI Detector (INDEPENDENT)

**How It Works**:
```python
# Stage 2 (Week 4-7): 5 agents in parallel
async def run_parallel_agents():
    # All 5 features develop simultaneously
    await agent_a_chat_with_pdf()       # Independent
    await agent_b_literature_search()  # Independent
    await agent_c_citation_generator() # Independent
    await agent_d_data_extraction()    # Independent
    await agent_e_ai_detector()       # Independent
    
    # All follow Ralph Loop methodology independently
    # Each: Test → Find Problem → Fix → Test Again → Exit
```

**Each Agent Follows Ralph Loop**:
1. Implement feature
2. Write E2E test scenario (agent-browser)
3. Test feature
4. Find problem
5. Fix problem
6. Test again
7. Repeat until complete
8. Exit when tests pass

**Communication Between Sessions**:
- Each agent works in separate conversation/session
- No coordination needed (features are independent)
- Founder switches between agents to monitor progress
- Each agent provides weekly progress update

**Stage 3 (Week 8-11): Sequential (3 agents)**
These features DEPEND on Literature Search (Agent B) from Stage 2:
- ✅ Agent F: AI Writer - DEPENDS on Literature Search
- ✅ Agent G: Systematic Review - DEPENDS on Literature Search
- ✅ Agent H: Citation Booster - DEPENDS on Literature Search

**How It Works**:
```python
# Stage 3 (Week 8-11): 3 agents sequentially
async def run_sequential_agents():
    # Wait for Stage 2 Literature Search to complete
    literature_search_complete = await check_agent_b_status()
    
    if literature_search_complete:
        # Now start dependent features
        await agent_f_ai_writer()           # Depends on Literature Search
        await agent_g_systematic_review()      # Depends on Literature Search
        await agent_h_citation_booster()     # Depends on Literature Search
    
    # Each follows Ralph Loop methodology
```

**Stage 4 (Week 12-14): Final stages**
- Week 12: Paraphraser (Can be independent, but sequential for simplicity)
- Week 13: Deep Review (Depends on EVERY feature)
- Week 14: E2E Testing (Agent-browser validates everything)
- Week 15: Polish & Launch

### Phase 2: Chat with PDF (Week 4-7 - PARALLEL)
**Objective**: Auth, database, basic UI

#### User Stories (US)
- **US1.1**: As a researcher, I can sign up with Google/Orcid ID
- **US1.2**: As a researcher, I can upgrade to Pro tier
- **US1.3**: As a researcher, I can manage my subscription
- **US1.4**: As a researcher, I can access my dashboard

#### Features
- [ ] Clerk authentication (Google, GitHub, Email/Password)
- [ ] Stripe subscriptions (Free, Pro, Team)
- [ ] PostgreSQL + pgvector setup
- [ ] Dashboard UI
- [ ] User profile management

**Testing (Ralph Loop)**:
1. Test sign-up flow with agent-browser
2. Find problem: Rate limit on Clerk
3. Fix: Implement retry logic
4. Test again: Success
5. Exit: Move to next feature

### Phase 2: Chat with PDF (Week 4-5)
**Objective**: Upload, process, chat with documents

#### User Stories
- **US2.1**: As a researcher, I can upload a PDF paper
- **US2.2**: As a researcher, I can see processing status
- **US2.3**: As a researcher, I can ask questions about the PDF
- **US2.4**: As a researcher, I get answers with page references

#### Features
- [ ] PDF upload endpoint (multipart/form-data)
- [ ] PDF processing (Unstructured + PDFPlumber)
- [ ] Text chunking (500-1000 tokens)
- [ ] Embedding generation (OpenAI text-embedding-3-small)
- [ ] Vector storage (pgvector)
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

### Phase 3: Literature Search (Week 6-7)
**Objective**: Multi-source academic paper search

#### User Stories
- **US3.1**: As a researcher, I can search PubMed
- **US3.2**: As a researcher, I can search arXiv
- **US3.3**: As a researcher, I can search Google Scholar
- **US3.4**: As a researcher, I can see aggregated results
- **US3.5**: As a researcher, I can export citations

#### Features
- [ ] **paper-search-mcp integration** (MCP server)
- [ ] **pubmed-mcp-server integration** (MCP server)
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

### Phase 4: AI Writer (Week 8-9)
**Objective**: AI-assisted academic paper writing

#### User Stories
- **US4.1**: As a researcher, I can start a writing project
- **US4.2**: As a researcher, I can generate sections (abstract, intro, etc.)
- **US4.3**: As a researcher, I can edit AI-generated content
- **US4.4**: As a researcher, I can track word count
- **US4.5**: As a researcher, I can export to LaTeX/Word

#### Features
- [ ] Writing project management
- [ ] Section-by-section generation (GPT-4)
- [ ] Academic tone enforcement
- [ ] Citation insertion
- [ ] Version history
- [ ] Collaborative editing (Team tier)
- [ ] Export to multiple formats

**Integration Points**:
- **LangChain**: Writing chains with academic prompts
- **Claude Scientific Skills**: Scientific writing best practices
- **Citation generator**: Auto-insert citations

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

### Phase 5: Systematic Literature Review (Week 10-11)
**Objective**: PRISMA-compliant systematic review

#### User Stories
- **US5.1**: As a researcher, I can define research question
- **US5.2**: As a researcher, I can set inclusion/exclusion criteria
- **US5.3**: As a researcher, I can run PRISMA screening
- **US5.4**: As a researcher, I can get PRISMA flow diagram
- **US5.5**: As a researcher, I can export study data

#### Features
- [ ] PRISMA workflow builder
- [ ] Multi-source search (integrate Phase 3)
- [ ] Screening tool (title/abstract/full-text)
- [ ] Data extraction form
- [ ] PRISMA flow diagram generator
- [ ] Bias assessment tool (Cochrane ROB2)
- [ ] Study management

**Integration Points**:
- **paper-search-mcp**: Multi-source search
- **pubmed-mcp-server**: PubMed advanced search
- **Claude Scientific Skills**: PRISMA workflows

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

### Phase 6: Citation Generator (Week 12)
**Objective**: Generate citations in multiple styles

#### User Stories
- **US6.1**: As a researcher, I can enter paper metadata
- **US6.2**: As a researcher, I can generate APA citation
- **US6.3**: As a researcher, I can generate MLA citation
- **US6.4**: As a researcher, I can generate BibTeX
- **US6.5**: As a researcher, I can batch generate citations

#### Features
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

### Phase 7: Data Extraction (Week 13)
**Objective**: Extract tables/figures from PDFs

#### User Stories
- **US7.1**: As a researcher, I can extract tables
- **US7.2**: As a researcher, I can extract figure captions
- **US7.3**: As a researcher, I can export to CSV
- **US7.4**: As a researcher, I can download original figures

#### Features
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

### Phase 8: AI Detector (Week 14)
**Objective**: Detect AI-generated content

#### User Stories
- **US8.1**: As a researcher, I can paste text
- **US8.2**: As a researcher, I can see AI probability
- **US8.3**: As a researcher, I can upload a document
- **US8.4**: As a researcher, I can see document-level analysis

#### Features
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

### Phase 9: Paraphraser (Week 15)
**Objective**: Academic paraphrasing tool

#### User Stories
- **US9.1**: As a researcher, I can paste text
- **US9.2**: As a researcher, I can select paraphrase intensity
- **US9.3**: As a researcher, I can compare original vs paraphrase
- **US9.4**: As a researcher, I can preserve citations

#### Features
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

### Phase 10: Deep Review (Week 16)
**Objective**: Comprehensive paper analysis

#### User Stories
- **US10.1**: As a researcher, I can upload a paper
- **US10.2**: As a researcher, I can see strengths/weaknesses
- **US10.3**: As a researcher, I can get improvement suggestions
- **US10.4**: As a researcher, I can compare to similar papers

#### Features
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

### Phase 11: Citation Booster (Week 17)
**Objective**: Suggest additional citations

#### User Stories
- **US11.1**: As a researcher, I can paste a paragraph
- **US11.2**: As a researcher, I can see citation suggestions
- **US11.3**: As a researcher, I can insert citations
- **US11.4**: As a researcher, I can see relevance scores

#### Features
- [ ] Text input/upload
- [ ] Citation suggestions (from literature search)
- [ ] Relevance scoring
- [ ] One-click insertion
- [ ] Citation completeness check

**Integration Points**:
- **paper-search-mcp**: Find relevant papers
- **OpenAI Embeddings**: Similarity scoring

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

## TESTING STRATEGY

### Agent-Based Testing (Phase 12-18)
**Objective**: Comprehensive E2E testing with agent-browser

#### Test Scenarios (Dr. Chen's Workflows)

##### Scenario 1: Literature Review Workflow
```bash
# Start browser automation
agent-browser open http://localhost:3000
agent-browser snapshot --json
# 1. Sign in as Dr. Chen
agent-browser find role button click --name "Sign In"
agent-browser find label "Email" fill "dr.chen@berkeley.edu"
agent-browser find label "Password" fill "password123"
agent-browser find role button click --name "Sign In"
# 2. Search for "AI drug discovery"
agent-browser find label "Search" fill "AI drug discovery"
agent-browser press Enter
# 3. Select top 10 papers
agent-browser find checkbox "Select all" check
# 4. Export to BibTeX
agent-browser find role button click --name "Export"
agent-browser find text "BibTeX" click
# 5. Upload papers to Chat with PDF
agent-browser click "@new-chat"
agent-browser upload "#pdf-upload" ["paper1.pdf", "paper2.pdf"]
# 6. Ask questions
agent-browser find textarea "message" fill "Summarize the main findings"
agent-browser find role button click --name "Send"
# 7. Extract data
agent-browser click "#data-extraction"
agent-browser find role button click --name "Extract Tables"
# 8. Verify outputs
agent-browser screenshot workflow-test-1.png
agent-browser get text "#results"
```

**Ralph Loop**:
- Test workflow end-to-end
- Find problem: Export format wrong
- Fix: Adjust BibTeX formatting
- Test again: Success
- Exit: Document test case

##### Scenario 2: Systematic Review Workflow
```bash
agent-browser open http://localhost:3000/literature/new-review
agent-browser find label "Research Question" fill "What is the impact of AI on drug discovery?"
agent-browser find label "Inclusion Criteria" fill "Must use AI, published 2020-2025"
agent-browser find label "Exclusion Criteria" fill "Review papers only"
agent-browser find role button click --name "Create Review"
agent-browser wait --text "Screening Phase"
agent-browser find role button click --name "Start Screening"
# Screen 20 papers
for i in {1..20}; do
  agent-browser find text "Include" click
done
agent-browser find role button click --name "Generate PRISMA"
agent-browser screenshot prisma-diagram.png
```

**Ralph Loop**:
- Test systematic review creation
- Find problem: Screening count mismatch
- Fix: Add real-time counter
- Test again: Success
- Exit: Document test case

##### Scenario 3: AI Writer Workflow
```bash
agent-browser open http://localhost:3000/writing/new
agent-browser find label "Project Title" fill "AI-Powered Drug Discovery"
agent-browser find label "Type" select "Review Article"
agent-browser find role button click --name "Create Project"
agent-browser find role button click --name "Generate Abstract"
agent-browser wait --text "Abstract generated"
agent-browser get text "#abstract-content"
# Verify academic tone
agent-browser find role button click --name "Check Academic Tone"
agent-browser screenshot abstract-check.png
agent-browser find label "Tone Score" get text
# Add citations
agent-browser find role button click --name "Insert Citation"
agent-browser find label "Search" fill "drug discovery AI"
agent-browser find text "First paper" click
agent-browser screenshot citation-inserted.png
# Export to LaTeX
agent-browser find role button click --name "Export"
agent-browser find text "LaTeX" click
```

**Ralph Loop**:
- Test AI writing workflow
- Find problem: Export missing bibliography
- Fix: Add bibliography generation
- Test again: Success
- Exit: Document test case

##### Scenario 4: Full Nature Review Workflow (Dr. Chen's Goal)
```bash
# Dr. Chen needs to submit a review to Nature
# Step 1: Literature search (500+ papers)
agent-browser open http://localhost:3000/literature
agent-browser find label "Search" fill "AI drug discovery deep learning"
agent-browser find label "Date Range" fill "2020-2025"
agent-browser find checkbox "PubMed" check
agent-browser find checkbox "arXiv" check
agent-browser find checkbox "Google Scholar" check
agent-browser find role button click --name "Search"
agent-browser wait --text "Results: 527"
# Step 2: Systematic screening
agent-browser find role button click --name "Start PRISMA"
# Screen 100 papers (automated bulk screening)
agent-browser click "#bulk-screen"
agent-browser find checkbox "Screen all" check
agent-browser find role button click --name "Screen"
# Step 3: Data extraction (200 papers)
agent-browser click "#data-extraction"
agent-browser upload "#papers-list" ["selected_papers.json"]
agent-browser find role button click --name "Extract Data"
# Step 4: AI Writer
agent-browser open http://localhost:3000/writing/project-001
agent-browser find role button click --name "Generate Introduction"
agent-browser find role button click --name "Generate Methods"
agent-browser find role button click --name "Generate Results"
agent-browser find role button click --name "Generate Discussion"
agent-browser find role button click --name "Generate Conclusion"
# Step 5: Citation management
agent-browser find role button click --name "Generate Bibliography"
agent-browser find label "Style" select "Nature"
agent-browser find role button click --name "Generate"
# Step 6: Export for Nature
agent-browser find role button click --name "Export"
agent-browser find text "Nature Format" click
agent-browser screenshot nature-export.png
```

**Ralph Loop**:
- Test full Nature submission workflow
- Find problem: Format doesn't match Nature requirements
- Fix: Add Nature-specific template
- Test again: Format matches
- Exit: Document test case

## QUALITY GATES

### Per-Feature Requirements
Before moving to next feature, must pass:

1. **Functionality**: All user stories work as specified
2. **Agent-Browser Tests**: All test scenarios pass
3. **Error Handling**: Graceful error messages
4. **Performance**: <2s page load, <500ms API
5. **Accessibility**: WCAG 2.1 AA compliant
6. **Mobile**: Responsive on mobile devices
7. **Code Quality**: Type hints, no console errors
8. **Documentation**: API docs updated
9. **Dr. Chen Approval**: Test with real researcher feedback

### Project-Wide Requirements
Before launch, must pass:

1. **All 11 Features**: Implemented and tested
2. **Integration Tests**: All features work together
3. **Security Audit**: No secrets, input validation, rate limiting
4. **Performance**: <2s p95 response time
5. **Uptime**: 99.9% availability
6. **Backup**: Database backups every hour
7. **Monitoring**: APM tools configured
8. **Documentation**: User docs, API docs, dev docs
9. **Beta Test**: 20+ researchers test all features
10. **Dr. Chen Sign-Off**: Dr. Chen successfully submits Nature review

## IMPLEMENTATION ORDER

### Parallel Tracks
Can implement in parallel where possible:

#### Track A: Core Infrastructure (Week 1-3)
- Spec-Kit setup
- Constitution
- Auth
- Database
- Basic UI

#### Track B: AI/ML Features (Week 4-11)
- Chat with PDF
- Literature search
- AI Writer
- Systematic review

#### Track C: Supporting Tools (Week 12-17)
- Citation generator
- Data extraction
- AI detector
- Paraphraser
- Deep review
- Citation booster

#### Track D: Testing & Polish (Week 18-20)
- Agent-browser E2E tests
- Ralph loop iterations
- Performance optimization
- Security hardening
- Documentation
- Launch prep

## SUCCESS METRICS

### Feature Completion
- [ ] 11/11 features implemented
- [ ] 50+ user stories completed
- [ ] 200+ test scenarios passing
- [ ] Dr. Chen's Nature review submitted

### Quality Metrics
- [ ] 95%+ test coverage
- [ ] <500ms API response (p95)
- [ ] <2s page load (p95)
- [ ] 0 critical bugs
- [ ] <5 minor bugs

### User Success (Beta)
- [ ] 20+ beta testers
- [ ] 80%+ feature usage
- [ ] 4.5+ average rating
- [ ] 0 feature abandonment

### Business Metrics (Launch)
- [ ] 100+ paying users (Month 1)
- [ ] 500+ total users (Month 1)
- [ ] <5% churn (Month 1)
- [ ] $1,000+ MRR (Month 1)

## NEXT ACTIONS

### Immediate (Today)
1. Install spec-kit
2. Initialize SDD project
3. Create constitution
4. Create specification
5. Update SESSION_MEMORY.md with this plan

### This Week
1. Complete Phase 0 (Spec-Driven Setup)
2. Validate spec-kit setup
3. Review constitution with user
4. Get approval on specification
5. Generate detailed tasks

### Next Week
1. Begin Phase 1 (Foundation)
2. Implement authentication
3. Set up database
4. Build dashboard
5. Start Ralph loop testing

## RISKS & MITIGATION

### Risk 1: MCP Integration Complexity
**Risk**: Integrating 3 MCP servers may be complex
**Mitigation**:
- Start with paper-search-mcp first
- Test integration thoroughly
- Use Claude Scientific Skills as fallback
- Document integration patterns

### Risk 2: AI Model Costs
**Risk**: OpenAI costs for 100+ beta testers
**Mitigation**:
- Use GPT-4o-mini for simple tasks
- Cache common queries
- Implement rate limiting per user tier
- Monitor costs daily

### Risk 3: Performance with Large PDFs
**Risk**: 50+ page PDFs timeout
**Mitigation**:
- Implement streaming processing
- Use async workers
- Add progress indicators
- Set reasonable timeouts (5 min per PDF)

### Risk 4: API Rate Limits
**Risk**: PubMed/Scholar rate limits block users
**Mitigation**:
- Implement caching layer
- Use multiple API keys if needed
- Add queue system
- Show rate limit status to users

### Risk 5: Dr. Chen's Review Rejected
**Risk**: Nature rejects Dr. Chen's review
**Mitigation**:
- Use Claude Scientific Skills for Nature-specific guidance
- Get peer review from another academic
- Validate format against Nature template
- Test multiple AI-generated drafts

## CONTINGENCY PLANS

### Plan A: Original Plan
Proceed with all 11 features and SDD methodology.

### Plan B: Reduced Scope
If timeline runs over:
- Phase 11 (Citation Booster) → Optional
- Phase 8 (AI Detector) → Optional
- Focus on core features (Chat with PDF, Literature Search, AI Writer)

### Plan C: Staggered Launch
If development takes longer:
- Launch MVP: Chat with PDF + Literature Search + AI Writer
- Launch V1: Add remaining features

## DOCUMENTATION REQUIREMENTS

### Developer Docs
- Architecture overview
- API documentation (OpenAPI/Swagger)
- Database schema
- MCP integration guide
- Environment setup
- Troubleshooting guide

### User Docs
- Getting started guide
- Feature tutorials (per feature)
- Dr. Chen's Nature review case study
- FAQ
- Video walkthroughs

### Test Docs
- Test scenarios (per feature)
- Ralph loop examples
- Agent-browser scripts
- Expected results
- Known issues

---

**Remember**: All context saved in markdown files. If session crashes, read SESSION_MEMORY.md to regain full context.
