# SCI-SPACE CLONE - QUICK START

## 🎯 PROJECT SUMMARY
Building a subscription-based academic research platform with:
- Chat with PDF
- Literature search (PubMed, Google Scholar, ArXiv)
- AI Writer for academic papers
- Citation generator (APA, MLA, Chicago, IEEE)
- Data extraction from PDFs
- AI content detection
- Systematic literature review (PRISMA)

## 📚 DOCUMENTATION STRUCTURE

1. **PROJECT_PLAN.md** - Overall project plan, phases, and tech stack
2. **REPOSITORIES.md** - 35+ proven GitHub repos with license analysis
3. **SESSION_MEMORY.md** - Context persistence between sessions
4. **IMPLEMENTATION_ROADMAP.md** - Detailed step-by-step implementation guide
5. **QUICK_START.md** - This file - quick reference guide

## 🚀 QUICK START COMMANDS

### Day 1: Project Setup
```bash
cd /Users/shaileshsingh/V1\ draft

# Frontend
npx create-next-app@latest client --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"
cd client
npm install @clerk/nextjs @tanstack/react-table lucide-react class-variance-authority clsx tailwind-merge
npx shadcn-ui@latest init
npx shadcn-ui@latest add button card input textarea table badge dialog dropdown-menu

# Backend
cd ..
python -m venv venv
source venv/bin/activate
pip install fastapi uvicorn[standard] langchain langchain-openai llama-index psycopg2-binary pgvector python-multipart python-jose[cryptography] passlib[bcrypt] python-dotenv stripe openai tiktoken pypdf pdfplumber unstructured biopython scholarly arxiv

# Directory structure
mkdir -p server/app/{api,core,models,services}
mkdir -p server/{pdf_processor,vector_store,langchain_chains}
```

### Database Setup
```bash
# Start PostgreSQL with pgvector
docker run --name sci-space-db \
  -e POSTGRES_DB=scispace \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  pgvector/pgvector:pg16

# Run migrations
psql -h localhost -U postgres -d scispace < schema.sql
```

### Environment Variables
```env
# .env file
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/scispace

# Clerk Auth
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_...
CLERK_SECRET_KEY=sk_...
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up

# Stripe
STRIPE_SECRET_KEY=sk_...
STRIPE_WEBHOOK_SECRET=whsec_...
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_...

# OpenAI
OPENAI_API_KEY=sk-...

# Anthropic (optional)
ANTHROPIC_API_KEY=sk-ant-...

# S3 (for file storage)
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
AWS_S3_BUCKET=scispace-docs
```

## 📋 FEATURE IMPLEMENTATION ORDER

### Priority 1 (Core MVP - Week 1-3)
1. ✅ Authentication (Clerk)
2. ✅ PDF Upload & Processing
3. ✅ Chat with PDF (RAG)
4. ✅ Basic Dashboard

### Priority 2 (Essential - Week 4-6)
5. ✅ Literature Search (PubMed, ArXiv)
6. ✅ Citation Generator
7. ✅ AI Writer (basic)
8. ✅ Data Extraction (tables)

### Priority 3 (Advanced - Week 7-10)
9. ✅ Systematic Literature Review (PRISMA)
10. ✅ Deep Review
11. ✅ Citation Booster
12. ✅ AI Detector
13. ✅ Paraphraser

## 🛠️ KEY REPOS TO USE

### Must-Have (All MIT/Apache 2.0)
- **LangChain** - AI orchestration
- **LlamaIndex** - Document indexing
- **Next.js 14** - Frontend framework
- **FastAPI** - Backend framework
- **shadcn/ui** - UI components
- **pgvector** - Vector search in Postgres
- **PDFPlumber** - Table extraction
- **Unstructured** - Document parsing
- **Clerk** - Authentication
- **Stripe SDK** - Payments

### API Integrations
- **PubMed** - via BioPython
- **ArXiv** - via arxiv.py
- **Google Scholar** - via Scholarly
- **Semantic Scholar** - official API

## 💰 SUBSCRIPTION TIERS

### Free Tier
- 5 PDF uploads
- Basic chat with PDF
- 50 literature searches/month
- Basic citation generation

### Pro ($19/month)
- Unlimited PDFs
- Unlimited literature searches
- AI Writer
- Advanced data extraction
- Priority processing

### Team ($49/month/user)
- Everything in Pro
- Team collaboration
- Shared libraries
- Admin dashboard
- Priority support

## 📊 DATABASE SCHEMA

### Core Tables
- `users` - User accounts
- `documents` - Uploaded PDFs
- `document_chunks` - Text chunks with embeddings (vector search)
- `chats` - Chat sessions
- `messages` - Chat messages
- `literature_searches` - Search history
- `citations` - Generated citations
- `writing_projects` - AI-written papers

### Key Feature
- `document_chunks` table uses `vector(1536)` column for embeddings
- Indexed with ivfflat for fast similarity search
- Enables RAG (Retrieval-Augmented Generation)

## 🎨 UI COMPONENTS TO BUILD

### Pages
- `/sign-in` - Sign in page
- `/sign-up` - Sign up page
- `/dashboard` - Main dashboard
- `/chat/new` - Upload & chat with PDF
- `/chat/[id]` - Chat with specific document
- `/literature` - Literature search
- `/writing` - AI writer
- `/citations` - Citation generator
- `/library` - Document library
- `/pricing` - Pricing page
- `/settings` - User settings

### Components
- `StatCard` - Dashboard stats
- `QuickAction` - Quick action buttons
- `ChatInterface` - Chat with PDF UI
- `LiteratureSearch` - Search interface
- `WritingEditor` - AI writing editor
- `CitationForm` - Citation generator form
- `DocumentList` - List of uploaded documents

## 🔍 CORE ALGORITHMS

### RAG Pipeline
1. Upload PDF → Extract text
2. Split text into chunks (500-1000 tokens)
3. Generate embeddings (OpenAI text-embedding-3-small)
4. Store in pgvector with metadata
5. Query → Search similar chunks → Augment prompt → Generate response

### Literature Search
1. Query entered → Search multiple APIs
2. Deduplicate results
3. Rank by relevance
4. Display with preview
5. Save to user's library

### AI Writer
1. User selects section (abstract, intro, methods, etc.)
2. Provide context (topic, findings, methods)
3. LangChain chain with GPT-4 generates content
4. User can edit and refine
5. Save to database

### Systematic Review (PRISMA)
1. Define research question
2. Set inclusion/exclusion criteria
3. Search multiple databases
4. Screen titles/abstracts
5. Review full texts
6. Extract data
7. Generate PRISMA flow diagram

## 🚨 COMMON ISSUES & SOLUTIONS

### PDF Processing Issues
- **Problem**: PDFs with complex layouts
- **Solution**: Use both PDFPlumber and Camelot, compare results

### Vector Search Performance
- **Problem**: Slow search on large datasets
- **Solution**: Use ivfflat index, limit k (top-k results)

### API Rate Limits
- **Problem**: PubMed/Google Scholar rate limits
- **Solution**: Implement caching, use multiple IP addresses if needed

### AI Costs
- **Problem**: High OpenAI costs
- **Solution**: Use smaller models for simple tasks, cache results, use streaming

## 📈 MONITORING & ANALYTICS

### Key Metrics to Track
- DAU/MAU (Daily/Monthly Active Users)
- Documents uploaded per user
- Chats per session
- Literature searches per user
- AI Writer usage
- Conversion rates (free → pro)
- Churn rate
- API usage (tokens, requests)

### Tools
- **Vercel Analytics** - Web analytics
- **LangSmith** - LLM app monitoring (free tier)
- **Sentry** - Error tracking
- **PostgreSQL queries** - Database performance

## 🔄 SESSION RECOVERY

If session crashes, restore context by reading:
```bash
# Read session memory
cat /Users/shaileshsingh/V1\ draft/SESSION_MEMORY.md

# Read project plan
cat /Users/shaileshsingh/V1\ draft/PROJECT_PLAN.md

# Read repositories
cat /Users/shaileshsingh/V1\ draft/REPOSITORIES.md

# Read implementation roadmap
cat /Users/shaileshsingh/V1\ draft/IMPLEMENTATION_ROADMAP.md
```

## 📞 NEXT STEPS

1. **Initialize project structure** (Day 1)
2. **Set up authentication** (Clerk) (Day 2)
3. **Create database schema** (Day 3)
4. **Implement PDF upload** (Day 4-5)
5. **Build Chat with PDF** (Day 6-7)
6. **Add literature search** (Day 8-9)
7. **Create AI Writer** (Day 10-11)
8. **Add citation generator** (Day 12)
9. **Implement subscription** (Stripe) (Day 13)
10. **Deploy MVP** (Day 14)

## 🎯 SUCCESS METRICS

### MVP Launch (Day 14)
- Working Chat with PDF
- Literature search from 3+ sources
- Basic AI Writer
- Citation generator (5+ styles)
- Authentication working
- Subscription payments working

### V1.0 Launch (Day 30)
- All 11 features working
- 100+ beta testers
- Payment processing live
- Documentation complete
- Analytics set up

## 💡 TIPS FOR SUCCESS

1. **Start simple**: Implement basic version of each feature first
2. **Test early**: Test each feature before moving to next
3. **Monitor costs**: Track OpenAI API usage from day 1
4. **Document everything**: Keep SESSION_MEMORY.md updated
5. **Use proven repos**: Don't reinvent the wheel
6. **Focus on UX**: Make it easy for academics to use
7. **Get feedback early**: Beta test with actual researchers
8. **Plan for scale**: Design for growth from day 1

---

**Remember**: All context is saved in the markdown files. If session crashes, just read SESSION_MEMORY.md to regain context!
