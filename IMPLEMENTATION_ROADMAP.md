# IMPLEMENTATION ROADMAP

## STEP 1: PROJECT INITIALIZATION (Day 1)

### Frontend Setup
```bash
cd /Users/shaileshsingh/V1\ draft
npx create-next-app@latest client --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"
cd client
npm install @clerk/nextjs @tanstack/react-table lucide-react class-variance-authority clsx tailwind-merge
npx shadcn-ui@latest init
npx shadcn-ui@latest add button card input textarea table badge dialog dropdown-menu
```

### Backend Setup
```bash
cd /Users/shaileshsingh/V1\ draft
python -m venv venv
source venv/bin/activate
pip install fastapi uvicorn[standard] langchain langchain-openai llama-index psycopg2-binary pgvector python-multipart python-jose[cryptography] passlib[bcrypt] python-dotenv stripe openai tiktoken pypdf pdfplumber unstructured
mkdir -p server/app/{api,core,models,services}
mkdir -p server/{pdf_processor,vector_store,langchain_chains}
```

### Database Schema Design
```sql
-- users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clerk_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    subscription_tier VARCHAR(50) DEFAULT 'free',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- documents table
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500),
    filename VARCHAR(255) NOT NULL,
    s3_key VARCHAR(500),
    total_pages INT,
    uploaded_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'uploading'
);

-- document_chunks table (for vector search)
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INT NOT NULL,
    content TEXT NOT NULL,
    page_number INT,
    embedding vector(1536)
);

-- chats table
CREATE TABLE chats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    document_id UUID REFERENCES documents(id) ON DELETE SET NULL,
    title VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW()
);

-- messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_id UUID REFERENCES chats(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL, -- 'user' or 'assistant'
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- literature_searches table
CREATE TABLE literature_searches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    query TEXT NOT NULL,
    sources JSONB, -- ['pubmed', 'scholar', 'arxiv']
    results JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- citations table
CREATE TABLE citations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    bibtex TEXT,
    style VARCHAR(50), -- 'apa', 'mla', 'chicago'
    formatted TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- writing_projects table
CREATE TABLE writing_projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500),
    abstract TEXT,
    content JSONB, -- structured by sections
    status VARCHAR(50) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for vector search
CREATE INDEX ON document_chunks USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX ON document_chunks (document_id);
CREATE INDEX ON chats (user_id);
CREATE INDEX ON messages (chat_id);
```

## STEP 2: AUTHENTICATION & SUBSCRIPTIONS (Day 2-3)

### Clerk Integration
1. Create Clerk account at dashboard.clerk.com
2. Get API keys (publishable and secret)
3. Add to `.env`:
```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_...
CLERK_SECRET_KEY=sk_...
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
```

### Stripe Integration
1. Create Stripe account at dashboard.stripe.com
2. Create products:
   - Free: $0/month
   - Pro: $19/month
   - Team: $49/month/user
3. Add to `.env`:
```env
STRIPE_SECRET_KEY=sk_...
STRIPE_WEBHOOK_SECRET=whsec_...
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_...
```

### Implement Auth Middleware
```typescript
// middleware.ts
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'

const isProtectedRoute = createRouteMatcher([
  '/dashboard(.*)',
  '/chat(.*)',
  '/library(.*)',
  '/writing(.*)',
  '/literature(.*)',
])

export default clerkMiddleware((auth, req) => {
  if (isProtectedRoute(req)) auth().protect()
})

export const config = {
  matcher: ['/((?!.*\\..*|_next).*)', '/', '/(api|trpc)(.*)'],
}
```

## STEP 3: PDF PROCESSING & VECTOR SEARCH (Day 4-6)

### PDF Upload Endpoint
```python
# server/app/api/documents.py
from fastapi import UploadFile, File, HTTPException
from pdf_processor import extract_text, extract_tables

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    # Check subscription limits
    if current_user.subscription_tier == 'free':
        doc_count = await count_user_docs(current_user.id)
        if doc_count >= 5:
            raise HTTPException(400, "Free tier limited to 5 documents")
    
    # Save to S3 or local storage
    # Extract text
    text = await extract_text(file)
    
    # Extract tables
    tables = await extract_tables(file)
    
    # Split into chunks
    chunks = split_text(text)
    
    # Generate embeddings and store in pgvector
    for i, chunk in enumerate(chunks):
        embedding = await generate_embedding(chunk)
        await store_chunk(document_id, i, chunk, embedding)
    
    return {"status": "processed", "document_id": doc_id}
```

### Chat with PDF Implementation
```python
# server/app/api/chat.py
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from vector_store import search_similar_chunks

@router.post("/chat")
async def chat_with_document(
    query: str,
    document_id: str,
    current_user: User = Depends(get_current_user)
):
    # Search for relevant chunks
    relevant_chunks = await search_similar_chunks(query, document_id, k=5)
    
    # Build context
    context = "\n\n".join([chunk.content for chunk in relevant_chunks])
    
    # Create prompt
    prompt = ChatPromptTemplate.from_template("""
    Use the following context from the document to answer the user's question.
    If the answer is not in the context, say "I don't have enough information from this document to answer that."
    
    Context:
    {context}
    
    Question: {question}
    
    Answer:
    """)
    
    # Generate response
    llm = ChatOpenAI(model="gpt-4")
    chain = prompt | llm
    response = await chain.ainvoke({
        "context": context,
        "question": query
    })
    
    return {"answer": response.content, "sources": [c.page_number for c in relevant_chunks]}
```

## STEP 4: LITERATURE SEARCH (Day 7-9)

### PubMed Integration
```python
# server/app/api/literature.py
from Bio import Entrez
import arxiv
import scholarly

@router.post("/search")
async def search_literature(
    query: str,
    sources: List[str] = ["pubmed", "scholar", "arxiv"],
    current_user: User = Depends(get_current_user)
):
    results = {"pubmed": [], "scholar": [], "arxiv": []}
    
    if "pubmed" in sources:
        results["pubmed"] = await search_pubmed(query)
    
    if "scholar" in sources:
        results["scholar"] = await search_scholar(query)
    
    if "arxiv" in sources:
        results["arxiv"] = await search_arxiv(query)
    
    # Save search history
    await save_search(current_user.id, query, sources, results)
    
    return results

async def search_pubmed(query: str, limit: int = 20):
    Entrez.email = "your@email.com"
    handle = Entrez.esearch(db="pubmed", term=query, retmax=limit)
    record = Entrez.read(handle)
    ids = record["IdList"]
    
    if not ids:
        return []
    
    handle = Entrez.efetch(db="pubmed", id=",".join(ids), rettype="medline", retmode="text")
    records = Medline.parse(handle)
    
    results = []
    for record in records:
        results.append({
            "title": record.get("TI", ""),
            "authors": record.get("AU", []),
            "journal": record.get("JT", ""),
            "year": record.get("DP", "")[:4] if record.get("DP") else "",
            "pmid": record.get("PMID", ""),
            "abstract": record.get("AB", ""),
            "doi": record.get("AID", [""])[0].split(" ")[0] if record.get("AID") else ""
        })
    
    return results

async def search_arxiv(query: str, limit: int = 20):
    search = arxiv.Search(
        query=query,
        max_results=limit
    )
    
    results = []
    for result in search.results():
        results.append({
            "title": result.title,
            "authors": [author.name for author in result.authors],
            "year": result.published.year,
            "arxiv_id": result.entry_id.split("/")[-1],
            "abstract": result.summary,
            "pdf_url": result.pdf_url,
            "categories": result.categories
        })
    
    return results

async def search_scholar(query: str, limit: int = 20):
    search_query = scholarly.search_pubs(query)
    
    results = []
    for i, publication in enumerate(search_query):
        if i >= limit:
            break
        results.append({
            "title": publication.get('bib', {}).get('title', ''),
            "authors": publication.get('bib', {}).get('author', []),
            "year": publication.get('bib', {}).get('pub_year', ''),
            "venue": publication.get('bib', {}).get('venue', ''),
            "url": publication.get('pub_url', ''),
            "citations": publication.get('num_citations', 0)
        })
    
    return results
```

### Systematic Literature Review (PRISMA)
```python
# server/app/api/prisma.py
@router.post("/systematic-review")
async def systematic_review(
    research_question: str,
    inclusion_criteria: List[str],
    exclusion_criteria: List[str],
    sources: List[str],
    current_user: User = Depends(get_current_user)
):
    # Phase 1: Identification
    initial_results = await search_literature(research_question, sources, current_user)
    
    # Phase 2: Screening (title/abstract)
    screened_results = []
    for source in initial_results:
        for paper in initial_results[source]:
            if meets_criteria(paper, inclusion_criteria, exclusion_criteria):
                screened_results.append(paper)
    
    # Phase 3: Eligibility (full text)
    eligible_results = []
    for paper in screened_results:
        full_text = await get_full_text(paper)
        if meets_criteria(full_text, inclusion_criteria, exclusion_criteria):
            eligible_results.append(paper)
    
    # Phase 4: Included studies
    return {
        "initial_results": sum(len(r) for r in initial_results.values()),
        "screened_results": len(screened_results),
        "eligible_results": len(eligible_results),
        "studies": eligible_results,
        "prisma_flow_diagram": generate_prisma_diagram(
            len(initial_results),
            len(screened_results),
            len(eligible_results)
        )
    }
```

## STEP 5: AI WRITER (Day 10-12)

### Academic Paper Writing Chain
```python
# server/langchain_chains/writing.py
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

async def write_section(section_type: str, context: dict):
    llm = ChatOpenAI(model="gpt-4", temperature=0.7)
    
    prompts = {
        "abstract": """
        Write an abstract for an academic paper with the following details:
        - Topic: {topic}
        - Key findings: {findings}
        - Methods: {methods}
        - Implications: {implications}
        
        The abstract should be concise (150-250 words) and follow standard academic structure.
        """,
        
        "introduction": """
        Write an introduction for an academic paper on {topic}.
        Include:
        - Background and context
        - Research gap
        - Objectives
        - Structure of the paper
        Length: 500-800 words
        """,
        
        "methods": """
        Write a methods section for a study on {topic}.
        Methodology: {methodology}
        Participants: {participants}
        Data collection: {data_collection}
        Analysis: {analysis}
        Length: 400-600 words
        """,
        
        "results": """
        Write a results section for a study on {topic}.
        Findings: {findings}
        Include appropriate academic language and statistical reporting where applicable.
        Length: 500-700 words
        """,
        
        "discussion": """
        Write a discussion section for a study on {topic}.
        Results: {results}
        Include:
        - Interpretation of findings
        - Comparison with existing literature
        - Limitations
        - Future research directions
        Length: 600-900 words
        """,
        
        "conclusion": """
        Write a conclusion for a paper on {topic}.
        Summarize key points and provide final thoughts.
        Length: 150-300 words
        """
    }
    
    prompt = ChatPromptTemplate.from_template(prompts[section_type])
    chain = prompt | llm | StrOutputParser()
    
    return await chain.ainvoke(context)

@router.post("/write-paper")
async def generate_paper(
    project_id: str,
    section: str,
    context: dict,
    current_user: User = Depends(get_current_user)
):
    content = await write_section(section, context)
    
    # Save to database
    await update_writing_project(project_id, section, content)
    
    return {"section": section, "content": content}
```

## STEP 6: CITATION GENERATOR (Day 13-14)

### Citation Formatting
```python
# server/app/api/citations.py
from citation_style_python import CitationStyle

@router.post("/generate")
async def generate_citation(
    metadata: dict,
    style: str = "apa",
    current_user: User = Depends(get_current_user)
):
    # Map style names
    style_mapping = {
        "apa": "apa",
        "mla": "modern-language-association",
        "chicago": "chicago-author-date",
        "ieee": "ieee",
        "harvard": "harvard"
    }
    
    style_name = style_mapping.get(style.lower(), "apa")
    
    # Generate citation
    citation = CitationStyle(style_name)
    formatted = citation.format(**metadata)
    
    # Generate BibTeX
    bibtex = generate_bibtex(metadata)
    
    # Save to database
    await save_citation(current_user.id, bibtex, style, formatted)
    
    return {
        "formatted": formatted,
        "bibtex": bibtex,
        "style": style
    }

def generate_bibtex(metadata):
    entry_type = determine_entry_type(metadata)
    bib_id = f"{metadata.get('first_author', '').split()[1]}{metadata.get('year', '2024')}"
    
    bibtex = f"@{entry_type}{{{bib_id},\n"
    bibtex += f"  author = {{{', '.join(metadata.get('authors', []))}}},\n"
    bibtex += f"  title = {{{metadata.get('title', '')}}},\n"
    if metadata.get('journal'):
        bibtex += f"  journal = {{{metadata.get('journal', '')}}},\n"
    if metadata.get('year'):
        bibtex += f"  year = {{{metadata.get('year', '')}}},\n"
    if metadata.get('volume'):
        bibtex += f"  volume = {{{metadata.get('volume', '')}}},\n"
    if metadata.get('pages'):
        bibtex += f"  pages = {{{metadata.get('pages', '')}}},\n"
    if metadata.get('doi'):
        bibtex += f"  doi = {{{metadata.get('doi', '')}}},\n"
    bibtex += "}"
    
    return bibtex
```

## STEP 7: DATA EXTRACTION (Day 15-16)

### Table Extraction
```python
# server/pdf_processor/tables.py
import pdfplumber
import camelot

async def extract_tables_from_pdf(file_path: str):
    # Method 1: pdfplumber
    pdf = pdfplumber.open(file_path)
    tables = []
    
    for page_num, page in enumerate(pdf.pages):
        page_tables = page.extract_tables()
        for table in page_tables:
            tables.append({
                "page": page_num + 1,
                "data": table,
                "method": "pdfplumber"
            })
    
    # Method 2: camelot for complex tables
    camelot_tables = camelot.read_pdf(file_path, flavor='lattice')
    for i, table in enumerate(camelot_tables):
        tables.append({
            "page": camelot_tables[i].page,
            "data": table.df.values.tolist(),
            "method": "camelot"
        })
    
    return tables

@router.post("/extract-tables")
async def extract_tables(
    document_id: str,
    current_user: User = Depends(get_current_user)
):
    doc = await get_document(document_id)
    file_path = await get_file_path(doc.s3_key)
    
    tables = await extract_tables_from_pdf(file_path)
    
    # Convert to CSV for download
    csv_data = []
    for i, table in enumerate(tables):
        csv = table_to_csv(table["data"])
        csv_data.append({
            "table_id": i + 1,
            "page": table["page"],
            "csv": csv
        })
    
    return {"tables": csv_data}
```

## STEP 8: AI DETECTOR (Day 17)

### AI Content Detection
```python
# server/app/api/ai-detector.py
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

@router.post("/detect")
async def detect_ai_content(
    text: str,
    current_user: User = Depends(get_current_user)
):
    # Load pre-trained model
    model_name = "roberta-base-openai-detector"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    
    # Tokenize
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    
    # Predict
    with torch.no_grad():
        outputs = model(**inputs)
        predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
    
    # Get probabilities
    ai_prob = predictions[0][1].item()
    human_prob = predictions[0][0].item()
    
    return {
        "ai_probability": round(ai_prob * 100, 2),
        "human_probability": round(human_prob * 100, 2),
        "verdict": "AI-generated" if ai_prob > 0.5 else "Likely human-written",
        "confidence": round(max(ai_prob, human_prob) * 100, 2)
    }
```

## STEP 9: FRONTEND COMPONENTS (Day 18-21)

### Main Dashboard
```typescript
// client/app/dashboard/page.tsx
export default function Dashboard() {
  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold mb-8">Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard title="Documents" value="12" icon="FileText" />
        <StatCard title="Chats" value="24" icon="MessageSquare" />
        <StatCard title="Literature Searches" value="8" icon="Search" />
      </div>
      
      <div className="mt-8">
        <h2 className="text-2xl font-semibold mb-4">Quick Actions</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <QuickAction 
            title="Upload PDF" 
            description="Chat with your documents"
            icon="Upload"
            href="/chat/new"
          />
          <QuickAction 
            title="Literature Search" 
            description="Search academic databases"
            icon="Search"
            href="/literature"
          />
          <QuickAction 
            title="Write Paper" 
            description="AI-assisted writing"
            icon="PenTool"
            href="/writing"
          />
          <QuickAction 
            title="Citations" 
            description="Generate citations"
            icon="Quote"
            href="/citations"
          />
        </div>
      </div>
    </div>
  )
}
```

### Chat with PDF Component
```typescript
// client/app/chat/[id]/page.tsx
'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export default function ChatWithDocument({ params }: { params: { id: string } }) {
  const [messages, setMessages] = useState<Array<{role: string, content: string}>>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  
  const sendMessage = async () => {
    if (!input.trim()) return
    
    setIsLoading(true)
    setMessages(prev => [...prev, { role: 'user', content: input }])
    setInput('')
    
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          document_id: params.id,
          query: input
        })
      })
      
      const data = await response.json()
      setMessages(prev => [...prev, { role: 'assistant', content: data.answer }])
    } catch (error) {
      console.error('Error:', error)
    } finally {
      setIsLoading(false)
    }
  }
  
  return (
    <div className="container mx-auto py-8">
      <Card className="h-[600px] flex flex-col">
        <CardHeader>
          <CardTitle>Chat with Document</CardTitle>
        </CardHeader>
        <CardContent className="flex-1 overflow-y-auto mb-4">
          {messages.map((msg, i) => (
            <div key={i} className={`mb-4 ${msg.role === 'user' ? 'text-right' : ''}`}>
              <div className={`inline-block p-3 rounded-lg ${
                msg.role === 'user' 
                  ? 'bg-blue-500 text-white' 
                  : 'bg-gray-100 text-gray-900'
              }`}>
                {msg.content}
              </div>
            </div>
          ))}
        </CardContent>
        <div className="border-t pt-4">
          <div className="flex gap-2">
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question about the document..."
              onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
              className="flex-1"
            />
            <Button onClick={sendMessage} disabled={isLoading}>
              {isLoading ? 'Sending...' : 'Send'}
            </Button>
          </div>
        </div>
      </Card>
    </div>
  )
}
```

## DEPLOYMENT CHECKLIST

### Pre-Launch
- [ ] All features tested
- [ ] Performance optimized
- [ ] Error handling in place
- [ ] Rate limiting implemented
- [ ] Monitoring configured
- [ ] Backup strategy in place
- [ ] Documentation complete

### Launch
- [ ] DNS configured
- [ ] SSL certificates installed
- [ ] Stripe webhooks active
- [ ] Clerk auth working
- [ ] Database migrations run
- [ ] Environment variables set
- [ ] Monitoring dashboards ready

### Post-Launch
- [ ] Analytics tracking
- [ ] User feedback collection
- [ ] Performance monitoring
- [ ] Error tracking (Sentry)
- [ ] Regular backups
- [ ] Security updates

## COST ESTIMATION (Monthly)

### Infrastructure
- Railway/Render: $5-20 (depending on scale)
- PostgreSQL: $5-20
- Storage (S3): $5-10
- Total: $15-50

### AI APIs (for 100 active users)
- OpenAI GPT-4: $30-80
- Embeddings: $10-20
- Total: $40-100

### Third-party Services
- Clerk: Free tier covers 5,000 MAUs
- Stripe: 2.9% + $0.30 per transaction

### Total: $55-150/month (infrastructure + AI)
### Revenue (100 users @ $19/mo): $1,900/month
### Net: ~$1,750-1,850/month (at 100 users)
