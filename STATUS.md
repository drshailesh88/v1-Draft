# V1 DRAFT - PROJECT STATUS

## AT A GLANCE

```
PROJECT:     V1 Draft (Academic Research Platform)
COMPLETION:  80% (8/12 features working)
LIVE URL:    https://v1-draft-production.up.railway.app
GITHUB:      https://github.com/drshailesh88/v1-Draft
```

---

## FEATURE STATUS

| # | Feature | Backend | Frontend | Router | Status |
|---|---------|---------|----------|--------|--------|
| 1 | AI Writer | ai_writer.py | /ai-writer | ENABLED | WORKING |
| 2 | Deep Review | deep_review.py | /deep-review | ENABLED | WORKING |
| 3 | Paraphraser | paraphraser.py | /paraphraser | ENABLED | WORKING |
| 4 | Systematic Review | systematic_review.py | /systematic-review | ENABLED | WORKING |
| 5 | AI Detector | ai_detector.py | /ai-detector | DISABLED | WORKING (enable router) |
| 6 | Topic Discovery | topics.py | /topics | ENABLED | WORKING |
| 7 | Payments | payments.py | /subscription | ENABLED | WORKING |
| 8 | Citations | citations.py | /citations | DISABLED | WORKING (enable router) |
| 9 | Literature Search | literature.py | /literature | ENABLED | BROKEN (MCP) |
| 10 | Chat with PDF | chat.py | /chat | DISABLED | BROKEN (missing modules) |
| 11 | Citation Booster | citation_booster.py | /citation-booster | ENABLED | PARTIAL (needs #9) |
| 12 | Data Extraction | data_extraction.py | /data-extraction | DISABLED | STUB |

---

## WHAT'S BROKEN & HOW TO FIX

### 1. Literature Search (CRITICAL)
```
PROBLEM:  MCP server integration doesn't work
FILE:     server/app/api/literature.py
FIX:      Replace MCP with direct library calls (arxiv, biopython, semanticscholar)
CREATE:   server/core/literature_clients.py
```

### 2. Chat with PDF (CRITICAL)
```
PROBLEM:  Missing pdf_processor and langchain_chains modules
FILE:     server/app/api/chat.py
FIX:      Create the missing modules
CREATE:   server/pdf_processor/processor.py
CREATE:   server/langchain_chains/rag_chain.py
ENABLE:   Uncomment router in main.py line 65
```

### 3. Citation Booster (MEDIUM)
```
PROBLEM:  Depends on Literature Search
FILE:     server/app/api/citation_booster.py
FIX:      Fix Literature Search first, then this works
```

### 4. Data Extraction (LOW)
```
PROBLEM:  Only placeholder code
FILE:     server/app/api/data_extraction.py
FIX:      Implement with pdfplumber
ENABLE:   Uncomment router in main.py line 79
```

---

## TASK ORDER

```
[1] Literature Search  →  Unblocks Citation Booster
[2] Chat with PDF      →  Independent
[3] Citation Booster   →  Just test (no code)
[4] Data Extraction    →  Independent
[5] Enable routers     →  Final step
[6] Deploy             →  railway up
```

---

## FILES TO CREATE

```
server/core/literature_clients.py     ← NEW (Task 1)
server/pdf_processor/processor.py     ← NEW (Task 2)
server/langchain_chains/rag_chain.py  ← NEW (Task 2)
```

---

## FILES TO MODIFY

```
server/app/api/literature.py          ← Remove MCP code (Task 1)
server/app/api/chat.py                ← Update imports (Task 2)
server/app/api/data_extraction.py     ← Implement logic (Task 4)
server/main.py                        ← Enable routers (Task 5)
```

---

## DO NOT TOUCH

These files are WORKING. Only modify if explicitly broken:
- ai_writer.py
- deep_review.py
- paraphraser.py
- systematic_review.py
- ai_detector.py
- topics.py
- payments.py
- citations.py
- database.py
- openai_client.py

---

## DETAILED GUIDE

For step-by-step implementation with code examples, see:
- `MASTER_BUILD_PLAN.md` - Full implementation guide
- `CLAUDE.md` - Project directives
- `.specify/specs/implementation-plan.md` - Speckit format

---

## COMMANDS

```bash
# Local dev
cd server && python main.py

# Deploy
git add -A && git commit -m "message" && railway up

# Test endpoint
curl https://v1-draft-production.up.railway.app/health
```

---

**Last Updated**: 2026-01-22
