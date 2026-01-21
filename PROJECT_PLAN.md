# V1 Draft Project Plan

## Project Overview
Building a subscription-based academic research platform with custom UI.

## Core Features to Build

### 1. Chat with PDF
- Upload and chat with PDF documents
- Extract and query content from research papers
- RAG (Retrieval-Augmented Generation) capabilities

### 2. Literature Review
- Systematic literature search (PRISMA methodology)
- Multi-source search (PubMed, Google Scholar, ArXiv)
- Smart paper organization and filtering

### 3. AI Writer / Manuscript Drafting
- Draft academic papers for journal submission
- Section-by-section writing assistance
- Academic tone and style enforcement

### 4. Find Topics / Concepts
- Topic discovery and exploration
- Research gap identification
- Trending topics in academic fields

### 5. Paraphraser
- Academic paraphrasing tool
- Plagiarism reduction
- Style adaptation

### 6. Citation Generator
- Multiple citation styles (APA, MLA, Chicago, IEEE, etc.)
- Automatic citation formatting
- Bibliography management

### 7. Extract Data
- Table and figure extraction from papers
- Data digitization
- CSV/Excel export

### 8. AI Detector
- AI-generated content detection
- Originality scoring
- Text analysis

### 9. Citation Booster
- Suggest relevant citations
- Citation completeness checks
- Reference improvement

### 10. Systematic Literature Review
- PRISMA framework implementation
- Study selection and screening
- Bias assessment tools

### 11. Deep Review
- Comprehensive paper analysis
- Cross-paper insights
- Quality assessment

## Tech Stack
- Frontend: Next.js 14 (App Router)
- Backend: Node.js with FastAPI/Express
- Database: PostgreSQL + pgvector
- Vector Search: Pinecone or Weaviate
- PDF Processing: PDF.js, PyMuPDF
- AI Models: OpenAI GPT-4, Claude 3.5
- Payment: Stripe
- Auth: Clerk/Auth0

## Proven GitHub Repositories to Use

### PDF Processing & Chat
1. **langchain-ai/langchain** - PDF loading and RAG
2. **llamaindex/LlamaIndex** - Document indexing and retrieval
3. **pdfplumber/pdfplumber** - PDF text and table extraction
4. **mstamy2/PyPDF2** - PDF manipulation

### Literature Search
5. **ncbi/Entrez-Direct** - PubMed API integration
6. **scholarly/python-scholarly** - Google Scholar scraping
7. **Cornell-ARX/arxiv.py** - ArXiv API wrapper
8. **Semantic Scholar/semanticscholar-python** - Semantic Scholar API

### Citation Management
9. **citation-style-language/locales** - Citation style definitions
10. **citation-file-format/citation-file-format** - Citation format
11. **bibtex-utils/bibtexparser** - BibTeX parsing

### AI Writing Tools
12. **langchain-ai/langchain** - Chain for academic writing
13. **microsoft/autogen** - Multi-agent writing assistance
14. **PennBioTk/PyOCLC** - Citation and reference management

### Data Extraction
15. **pdfplumber/pdfplumber** - Table extraction
16. **mhahsler/PyMuPDF** - Advanced PDF parsing
17. **camel-dev/camel** - Structured data extraction

### Content Analysis
18. **OpenAI/openai-cookbook** - Content analysis examples
19. **langchain-ai/langchain** - Text analysis chains

## Project Phases

### Phase 1: Foundation (Week 1-2)
- Project setup (Next.js + Backend)
- Database schema design
- Authentication system
- Subscription setup with Stripe

### Phase 2: Core PDF & Search (Week 3-4)
- PDF upload and processing
- Vector database setup
- Chat with PDF implementation
- Literature search integration

### Phase 3: Writing & Citation Tools (Week 5-6)
- AI Writer implementation
- Citation generator
- Paraphrasing tool
- Citation booster

### Phase 4: Data & Analysis (Week 7-8)
- Data extraction from PDFs
- AI detector
- Systematic review tools
- Deep review feature

### Phase 5: Testing & Launch (Week 9-10)
- E2E testing
- Performance optimization
- Deployment
- Launch preparation

## Excluded Features
- Chart/Data visualizations
- Poster generation
- Patent search
- Website/research site builder

## Subscription Tiers
- **Free**: Limited PDF uploads, basic chat
- **Pro ($19/mo)**: Unlimited PDFs, advanced search, AI writer
- **Team ($49/mo/user)**: Team collaboration, priority support, API access
