# Sci-Space Clone - Academic Research Platform

🚀 **5 Parallel Features Built**
- Agent A: Chat with PDF ✅
- Agent B: Literature Search ✅
- Agent C: Citation Generator ✅
- Agent D: Data Extraction ✅
- Agent E: AI Detector ✅

## 📋 Project Status

### ✅ Phase 1: Foundation (Week 2-3)
- [x] Frontend scaffold (Next.js)
- [x] Backend scaffold (FastAPI)
- [x] Project structure
- [x] Database schema (PostgreSQL + pgvector)
- [x] Core utilities (Supabase, OpenAI)
- [ ] Supabase setup (manual - see below)
- [ ] Railway deployment (manual - see below)
- [ ] Payment integration (Paddle + Razorpay)
- [ ] Auth setup (Supabase Auth)

### ✅ Phase 2-6: Parallel Sprint (Week 4-7) - 5 INDEPENDENT FEATURES
All 5 features have API endpoints created!

## 🏗️ Project Structure

\`\`\`
/Users/shaileshsingh/V1 draft/
├── client/                          # Next.js frontend
│   ├── app/
│   ├── components/
│   └── lib/
├── server/                         # FastAPI backend
│   ├── app/
│   │   └── api/                 # 5 parallel feature APIs
│   │       ├── chat.py           # Agent A
│   │       ├── literature.py      # Agent B
│   │       ├── citations.py      # Agent C
│   │       ├── data_extraction.py # Agent D
│   │       └── ai_detector.py   # Agent E
│   ├── core/                     # Core utilities
│   ├── pdf_processor/             # PDF processing
│   ├── langchain_chains/         # RAG chains
│   └── main.py                   # FastAPI app
├── database_schema.sql            # Supabase schema
├── server/.env.example           # Environment template
└── ULTIMATE_BUILD_DIRECTIVE.md  # Master directive
\`\`\`

## 🚀 Quick Start

### 1. Set Up Supabase (Manual)

1. Create account: https://supabase.com
2. Create project
3. Run database schema:
   \`\`\`sql
   -- Copy content from database_schema.sql
   -- Run in Supabase SQL Editor
   \`\`\`
4. Enable pgvector extension:
   \`\`\`sql
   create extension if not exists vector;
   \`\`\`
5. Get credentials:
   - Project URL
   - Anon Key
   - Service Role Key

### 2. Set Up Environment

\`\`\`bash
cd server
cp .env.example .env
# Edit .env with your credentials
\`\`\`

Add to \`.env\`:
\`\`\`bash
# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# OpenAI
OPENAI_API_KEY=your_openai_api_key
\`\`\`

### 3. Install Dependencies

**Backend**:
\`\`\`bash
cd server
source ../venv/bin/activate
pip install -r requirements.txt
\`\`\`

**Frontend**:
\`\`\`bash
cd client
npm install
\`\`\`

### 4. Run Locally

**Backend**:
\`\`\`bash
cd server
python main.py
# API runs on http://localhost:8000
\`\`\`

**Frontend**:
\`\`\`bash
cd client
npm run dev
# Frontend runs on http://localhost:3000
\`\`\`

## 🌐 Deployment

### Railway (Frontend + Backend)

1. Create account: https://railway.app
2. Connect GitHub repository
3. Create new service:
   - Select "Deploy from GitHub repo"
   - Select Railway service type
   - Configure build command: \`cd server && python main.py\`
   - Configure port: 8000
4. Add environment variables in Railway dashboard
5. Deploy!

### Supabase (Already Set Up)
Database, auth, and storage are all in Supabase. No additional deployment needed!

## 📊 API Endpoints

### Agent A: Chat with PDF
- \`POST /api/chat/upload\` - Upload PDF
- \`POST /api/chat/chat\` - Chat with document

### Agent B: Literature Search
- \`POST /api/literature/search\` - Search academic databases
- \`POST /api/literature/save-paper\` - Save paper to library
- \`GET /api/literature/saved-papers\` - Get saved papers
- \`GET /api/literature/export/{format}\` - Export citations

### Agent C: Citation Generator
- \`POST /api/citations/generate\` - Generate single citation
- \`POST /api/citations/batch-generate\` - Generate multiple citations

### Agent D: Data Extraction
- \`POST /api/data-extraction/extract-tables\` - Extract tables
- \`POST /api/data-extraction/extract-figures\` - Extract figures
- \`POST /api/data-extraction/export-csv\` - Export to CSV
- \`POST /api/data-extraction/export-excel\` - Export to Excel

### Agent E: AI Detector
- \`POST /api/ai-detector/detect-text\` - Detect AI in text
- \`POST /api/ai-detector/detect-file\` - Detect AI in file

## 🎯 Next Steps

### Immediate (This Week)
1. Complete Supabase setup
2. Complete Railway deployment
3. Implement Supabase Auth
4. Implement Paddle + Razorpay payments
5. Build frontend UI for all 5 features

### Next Week (Week 8-11: Sequential)
These features depend on Literature Search (Agent B):
- Agent F: AI Writer
- Agent G: Systematic Review
- Agent H: Citation Booster

## 📚 Reference Documents

- **ULTIMATE_BUILD_DIRECTIVE.md** - Master directive
- **SESSION_MEMORY.md** - Context recovery
- **SPEC_DRIVEN_PLAN.md** - 15-week roadmap
- **SESSION_RECOVERY.md** - Recovery guide
- **PARALLEL_BUILDER.md** - Parallel dev guide

## 💰 Cost Estimation

### Infrastructure (Monthly)
- Railway (Frontend + Backend): \$20/month
- Supabase (DB + Auth + Storage): \$0 → \$25/month
- **Total: \$20-45/month**

### AI APIs (for 100 users)
- OpenAI GPT-4: \$30-80
- Embeddings: \$10-20
- **Total: \$40-100/month**

### Total: \$60-145/month (startup phase)
### Revenue (100 users @ \$19/mo): \$1,900/month

## ✅ Testing (Ralph Loop)

For each feature:
1. Implement feature
2. Test feature
3. Find problem
4. Fix problem
5. Test again
6. Exit when all tests pass

## 🎯 Success Criteria

By feature completion:
- [ ] All user stories pass Ralph Loop testing
- [ ] Agent-browser scenarios pass
- [ ] Dr. Chen approves functionality
- [ ] Documentation complete

By project launch:
- [ ] 11/11 features implemented
- [ ] 200+ test scenarios passing
- [ ] Dr. Chen successfully submits Nature review
- [ ] 100+ paying users (Month 1)

---

**Remember**: Use ULTIMATE_BUILD_DIRECTIVE.md as compass. All plans, strategies, and decisions are documented there.
