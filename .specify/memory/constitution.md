# V1 Draft Constitution

## Core Principles

### I. Library-First Development
Use proven, MIT/Apache licensed GitHub repositories for every feature. No reinventing the wheel. Every feature should leverage existing libraries:
- `arxiv`, `biopython`, `semanticscholar` for paper search
- `pdfplumber` for PDF processing
- `langchain`, `openai` for AI features
- `pandas`, `openpyxl` for data export

### II. API-First Architecture
Every feature is an API endpoint first:
- FastAPI backend with automatic OpenAPI docs
- REST endpoints with JSON responses
- Health checks at `/health`
- Frontend consumes backend API

### III. Test Before Deploy
Before deploying any feature:
1. Test endpoint locally with curl
2. Verify response format
3. Check error handling
4. Then deploy to Railway

### IV. Don't Break Working Features
8 features are PRODUCTION READY. Do not modify:
- ai_writer.py, deep_review.py, paraphraser.py
- systematic_review.py, ai_detector.py, topics.py
- payments.py, citations.py

### V. Spec-Driven Development
Follow the Speckit workflow:
1. `/speckit.specify` - Define what to build
2. `/speckit.plan` - Create technical plan
3. `/speckit.tasks` - Generate task list
4. `/speckit.implement` - Execute implementation
5. `/speckit.analyze` - Verify consistency

## Technology Constraints

### Backend
- Python 3.11+ with FastAPI
- Supabase for database (PostgreSQL + pgvector)
- OpenAI GPT-4 for AI features
- No Flask, no Django

### Frontend
- Next.js 16 with App Router
- React 19, TypeScript
- Tailwind CSS for styling
- No other UI frameworks

### Deployment
- Railway for hosting
- Docker for containerization
- GitHub for version control

## Development Workflow

1. **Read** CLAUDE.md and STATUS.md first
2. **Check** MASTER_BUILD_PLAN.md for implementation details
3. **Follow** task order: Literature Search → Chat PDF → Citation Booster → Data Extraction
4. **Test** each feature before moving to next
5. **Commit** after each completed task
6. **Deploy** with `railway up`

## Governance

- This constitution guides all development decisions
- CLAUDE.md is the primary directive file
- MASTER_BUILD_PLAN.md contains implementation code
- STATUS.md shows current progress
- Speckit specs in `.specify/specs/` define features

**Version**: 1.0.0 | **Ratified**: 2026-01-22 | **Last Amended**: 2026-01-22
