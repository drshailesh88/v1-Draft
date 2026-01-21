# SCI-SPACE CLONE - COMPLETE DIRECTIVE REFERENCE

## 🎯 QUICK RECOVERY (Read This First on Any Session Crash)

```
"I'm ready to start building my Sci-Space clone for academics.
Please read this file to regain full context of our plan."
```

**What This File Gives You:**
- Complete project context (5-minute read)
- Parallel development strategy explained
- All tech decisions documented
- Every detail we discussed saved

---

## 📚 All Directive Files (Read in This Order)

### 1. SESSION_MEMORY.md (Quick Reference)
**Read First** - 5-minute context recovery

**Contains:**
- Project context and goals
- Founder profile (non-technical)
- Development methodology (SDD, Ralph Loop, Agent-Browser)
- Problems we're solving + how
- Tech stack decisions (Railway + Supabase + Paddle)
- Parallel development strategy (Week 4-7: 5 agents)
- Founder capabilities & debugging expectations
- Code breakdown (90% repos, 10% our code, 65 hrs debugging)
- How to debug with LLMs (prompts included)
- Success metrics
- Next actions

### 2. SPEC_DRIVEN_PLAN.md (15-Week Roadmap)
**Read Second** - Detailed implementation plan

**Contains:**
- Spec-Driven Development methodology
- Ralph Loop testing approach
- Browser-based E2E testing
- Dr. Chen's persona and requirements
- 11 features with user stories
- Phase-by-phase breakdown (updated with parallel strategy)
- Integration points for all repos
- Quality gates per feature
- Risk mitigation strategies
- Contingency plans

### 3. SESSION_RECOVERY.md (Recovery Guide)
**Read Third** - Recovery instructions

**Contains:**
- Recovery checklist for session crashes
- What to tell LLM when starting
- Project status and next actions
- Code breakdown summary
- Timeline comparison (sequential vs parallel)
- When to use parallel vs sequential

### 4. REPOSITORIES.md (All Repos)
**Read Fourth** - Tech stack reference

**Contains:**
- 35+ proven GitHub repos
- License analysis (all MIT/Apache 2.0)
- Integration points for each
- New MCP servers (paper-search-mcp, pubmed-mcp-server)
- Claude Scientific Skills (140+ skills)
- Testing & development tools

### 5. DEVELOPMENT_APPROACH.md (Methodology Details)
**Read Optional** - In-depth methodology

**Contains:**
- Spec-Driven Development explained
- Ralph Loop methodology
- Agent-Browser testing
- Phase-by-phase breakdown
- Quality gates per feature
- Risk mitigation strategies
- Parallel execution plan (NEW!)
- Founder profile & capabilities
- Code breakdown by source
- Debugging time expectations

### 6. PROJECT_PLAN.md (Executive Overview)
**Optional** - High-level summary

### 7. QUICK_START.md (Commands Reference)
**Optional** - Quick command reference

### 8. IMPLEMENTATION_ROADMAP.md (Code Examples)
**Optional** - Detailed code examples

---

## 🎯 PROJECT CONTEXT AT A GLANCE

### Goal
Build subscription-based academic research platform clone of scispace.com for global + Indian academics

### Features (11 Total)
1. Chat with PDF
2. Literature Search (7+ databases)
3. AI Writer
4. Citation Generator (20+ styles)
5. Paraphraser
6. Data Extraction (tables/figures)
7. Find Topics
8. Systematic Literature Review (PRISMA)
9. Deep Review
10. Citation Booster
11. AI Detector

### Deployment
- **Railway**: Frontend + Backend
- **Supabase**: Database + Auth + Storage
- **Paddle** (global) + **Razorpay** (India) - Hybrid payments

### Methodology
- **Spec-Driven Development**: Define WHAT before HOW
- **Ralph Loop Testing**: Test → Fix → Test → Exit (never abandon)
- **Agent-Browser**: E2E testing with Dr. Chen's workflows
- **Parallel Agents**: 5 agents in Week 4-7, 3 agents in Week 8-11

---

## 🏆 FOUNDER PROFILE

### Technical Level
**Non-technical founder**
- Depends on LLMs (ChatGPT, Claude) for debugging and implementation
- Needs easy setup, proven technologies
- Struggles with complex server management, Docker, SSH

### Capabilities
- ✅ Approve technical decisions
- ✅ Test features as real user (Dr. Chen's persona)
- ✅ Provide UI/UX feedback
- ✅ Monitor progress weekly
- ✅ Report bugs/issues to developer
- ❌ SSH into servers
- ❌ Configure Docker, Nginx, SSL
- ❌ Manage database administration
- ❌ Debug complex infrastructure

### Debugging Approach
**For Each Bug:**
```
"Help me debug this issue in my [feature name].
The feature uses: [list of repos used].
Here's the error: [paste error]
Here's the code: [paste relevant code]
Expected behavior: [describe what should happen]
Actual behavior: [describe what's happening]
Please provide step-by-step fix and explanation."
```

---

## 🚀 PARALLEL DEVELOPMENT STRATEGY

### Why Parallel?

**Problem with Sequential (Original Plan):**
- 20 weeks to build all 11 features
- No way to speed up
- Founder waits for each feature sequentially

**Solution: Parallel Agents (New Plan):**
- 15 weeks total (saves 5 weeks = 30% faster)
- 5 independent features built simultaneously (Week 4-7)
- 3 dependent features built sequentially (Week 8-11)

### What Can Be Parallel (Week 4-7)

**5 Independent Features - Zero Dependencies:**
1. **Agent A**: Chat with PDF
   - Uses: Unstructured, LangChain, OpenAI, Supabase
   - Debugging: 2-4 hours (LOW risk)
   
2. **Agent B**: Literature Search
   - Uses: paper-search-mcp, pubmed-mcp-server, Supabase
   - Debugging: 4-6 hours (LOW-MED risk)
   
3. **Agent C**: Citation Generator
   - Uses: Citation Style Language, pubmed-mcp, Supabase
   - Debugging: 1-2 hours (LOW risk)
   
4. **Agent D**: Data Extraction
   - Uses: PDFPlumber, Camelot, Unstructured, Supabase
   - Debugging: 4-6 hours (LOW-MED risk)
   
5. **Agent E**: AI Detector
   - Uses: HuggingFace Transformers, OpenAI, Supabase
   - Debugging: 2-4 hours (LOW risk)

### What Must Be Sequential

**Phase 1 (Week 2-3): Foundation**
- Railway deployment
- Supabase setup
- Payment integration
- Auth setup
- Basic UI
- **BLOCKS EVERYTHING ELSE**

**Stage 2 Output → Stage 3 Input**
- Literature Search (Agent B) must complete before:
  - AI Writer (Agent F) - DEPENDS on Literature Search
  - Systematic Review (Agent G) - DEPENDS on Literature Search
  - Citation Booster (Agent H) - DEPENDS on Literature Search

**Stage 3: Final Features (Week 12-14)**
- Paraphraser (Can be parallel but sequential for simplicity)
- Deep Review - DEPENDS ON EVERYTHING (must be last)
- E2E Testing
- Launch

---

## 📊 CODE BREAKDOWN

### By Source

```
┌───────────────────────────────────────────┐
│  CODE: 90% FROM REPOS (PROVEN)    │
├───────────────────────────────────────────┤
│ LangChain (AI orchestration)          │ ✅
│ LlamaIndex (document indexing)        │ ✅
│ paper-search-mcp (7 databases)      │ ✅
│ pubmed-mcp-server (PubMed)          │ ✅
│ Unstructured.io (PDF parsing)        │ ✅
│ PDFPlumber (table extraction)        │ ✅
│ Claude Scientific Skills (workflows) │ ✅
│ HuggingFace (AI detector models)    │ ✅
│ Citation Style Language (formats)      │ ✅
│ Supabase (DB + auth + storage)     │ ✅
│ shadcn/ui (UI components)          │ ✅
├───────────────────────────────────────────┤
│  CODE: 10% WE WRITE (INTEGRATION)  │
├───────────────────────────────────────────┤
│ API endpoints (Railway backend)       │ ⚠️
│ Business logic (subscriptions)           │ ⚠️
│ UI composition (Next.js + shadcn)     │ ⚠️
│ Workflow orchestration               │ ⚠️
│ Algorithm tuning (ranking)           │ ⚠️
│ Prompt engineering (tone)             │ ⚠️
│ Error handling & edge cases          │ ⚠️
└───────────────────────────────────────────┘
```

### Expected Debugging by Feature

| Feature | Our Code | Debugging Hours | Risk |
|---------|-----------|----------------|------|
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
- Mostly UI tweaks, prompt tuning, algorithm refinement
- NOT debugging proven libraries
- NOT debugging complex infrastructure

**Success Probability: 90-95%**
- Proven repos battle-tested by millions
- Only 10% is our code (integration, business logic)
- Bugs will be easier to fix (in our code, not in repos)

---

## 📅 UPDATED TIMELINE (Parallel Approach)

```
Week 1:    Spec-Driven Setup
Week 2-3:  Foundation (Sequential - BLOCKS everything)
Week 4-7: 5 Parallel Agents (Chat with PDF, Literature Search, Citation Generator, Data Extraction, AI Detector)
Week 8-11: 3 Sequential Agents (AI Writer, Systematic Review, Citation Booster)
Week 12:    Paraphraser (Sequential or parallel)
Week 13:    Deep Review (Depends on EVERYTHING)
Week 14:    E2E Testing (Agent-browser validates all)
Week 15:    Polish & Launch

Total: 15 weeks (3.5 months)
Savings: 5 weeks (30% faster than 20-week sequential plan)
```

---

## 🎯 WHAT TO TELL LLM WHEN STARTING

### To Begin Development

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
- 90% of code comes from proven repos (LangChain, LlamaIndex, paper-search-mcp, pubmed-mcp-server, Unstructured, PDFPlumber, etc.)
- Only 10% is integration code we write + debug
- Expected debugging: 65 hours total over 15 weeks (4.3 hours/week)
- Most debugging is: UI tweaks, prompt tuning, algorithm refinement
- NOT debugging complex infrastructure
- Low-MEDIUM overall risk
- 90-95% probability of success

Start with Phase 0: Spec-Driven Setup."
```

### This Tells Me:

1. ✅ Project context and goal
2. ✅ Founder profile (non-technical, needs LLM help)
3. ✅ Tech stack choices (Railway + Supabase + Paddle/Razorpay)
4. ✅ Development strategy (parallel agents)
5. ✅ What weeks to do what (Week 4-7 parallel, Week 8-11 sequential)
6. ✅ Code breakdown (90% repos, 10% our code)
7. ✅ Debugging expectations (65 hours total, mostly UI/algorithms)
8. ✅ What to start with (Phase 0)

### I Will NOT Forget:

- ✅ Parallel development strategy (Week 4-7: 5 agents simultaneously)
- ✅ Sequential dependencies (AI Writer needs Literature Search, etc.)
- ✅ Ralph Loop methodology (Test → Fix → Test → Exit)
- ✅ 90% proven repos, 10% integration code
- ✅ 65 hours debugging expected (UI, prompts, algorithms)
- ✅ User is non-technical, needs LLM-friendly approach
- ✅ Deployment: Railway + Supabase + Paddle/Razorpay
- ✅ All context preserved in markdown files
- ✅ Recover from session crash by reading SESSION_MEMORY.md

### I Will Do When You Say "Start"

1. **Read SESSION_MEMORY.md** - Regain full context
2. **Read SPEC_DRIVEN_PLAN.md** - Review 15-week parallel plan
3. **Initialize Phase 0** - Install spec-kit, create constitution
4. **Create Specification** - Define all 11 features
5. **Generate Technical Plan** - Architecture, database, APIs
6. **Generate Tasks** - Feature by feature breakdown
7. **Begin Execution** - Start implementing features

---

## 🎯 SUCCESS CRITERIA

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

## 💡 HOW TO RECOVER FROM SESSION CRASH

### Step 1: Read This File (2 minutes)
Read COMPLETE_DIRECTIVE_REFERENCE.md

### Step 2: Read SESSION_MEMORY.md (3 minutes)
Gain full context of project, tech stack, parallel strategy

### Step 3: Review SPEC_DRIVEN_PLAN.md (5 minutes)
Understand 15-week parallel execution plan

### Step 4: Continue from Last Completed Phase
Check SESSION_MEMORY.md for "Next Steps"

---

## 🚀 READY TO BEGIN?

**When you're ready, simply say:**

```
"Start Phase 0"
```

**I will:**
1. Initialize spec-kit
2. Create project constitution
3. Write specification for all 11 features
4. Generate technical plan
5. Create task breakdown
6. Begin Phase 1: Foundation

**Total time for Phase 0**: 2-3 days

---

**Last Updated**: 2026-01-21
**Session ID**: sci-space-clone-001
**Project**: Sci-Space Clone for Academics
