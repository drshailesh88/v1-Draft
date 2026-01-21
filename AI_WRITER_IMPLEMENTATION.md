# AI Writer Feature - Phase 7 Implementation

## Overview
AI Writer allows researchers to draft academic papers section-by-section with AI assistance. It integrates with the Literature Search feature for citation management and uses OpenAI GPT-4 for content generation.

## Files Created

### Backend
- **server/app/api/ai_writer.py** (286 lines)
  - FastAPI router with 6 endpoints
  - GPT-4 integration for content generation
  - Academic writing prompts for each section type
  - Citation extraction and integration

### Frontend
- **client/src/app/ai-writer/page.tsx** (477 lines)
  - Project management UI
  - Section generation interface
  - Paper search and selection
  - Rich text editor with word count
  - Save/load functionality

- **client/src/components/ui/tabs.tsx** (52 lines)
  - Tabs, TabsList, TabsTrigger, TabsContent components
  - Based on @radix-ui/react-tabs

## Files Modified

### Database
- **server/database_schema.sql**
  - Added `ai_writer_projects` table
  - Added `ai_writer_sections` table
  - Added performance indexes

### Backend
- **server/main.py**
  - Added `literature` router (AI Writer dependency)
  - Added `ai_writer` router with prefix `/api/ai-writer`
  - Updated API features list

### Frontend
- **client/package.json**
  - Added `@radix-ui/react-tabs` dependency

- **client/src/app/page.tsx**
  - Added AI Writer to feature cards
  - Added navigation link to `/ai-writer`

### Dependencies
- **requirements.txt**
  - Added `arxiv>=2.1.0`
  - Added `biopython>=1.83`
  - Added `requests>=2.31.0`

## API Endpoints

### POST /api/ai-writer/create-project
Create a new writing project
- Request: `{title, topic, research_questions}`
- Response: `{project_id}`

### POST /api/ai-writer/generate-section
Generate a paper section using GPT-4
- Request: `{project_id, section_type, paper_topic, key_points, selected_papers[]}`
- Response: `{generated_text, word_count, citations_used}`

### POST /api/ai-writer/save-section
Save a generated section
- Request: `{project_id, section_type, content, word_count, citations_used}`
- Response: `{status}`

### GET /api/ai-writer/project/{id}
Get full project with all sections
- Response: Project object with sections array

### GET /api/ai-writer/projects
List user's projects
- Response: `{projects: [...]}`

### DELETE /api/ai-writer/project/{id}
Delete a project and all its sections
- Response: `{status}`

## Database Schema

### ai_writer_projects
- `id` (UUID, primary key)
- `user_id` (UUID, foreign key → users)
- `title` (VARCHAR 500)
- `topic` (TEXT)
- `research_questions` (TEXT)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

### ai_writer_sections
- `id` (UUID, primary key)
- `project_id` (UUID, foreign key → ai_writer_projects)
- `section_type` (VARCHAR 50, CHECK: abstract, introduction, methods, results, discussion, conclusion)
- `content` (TEXT)
- `word_count` (INT)
- `citations_used` (JSONB)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

## Section Types
1. **Abstract** (200-250 words)
   - Background, objective, methods, results, conclusion

2. **Introduction**
   - Background, problem statement, research gap, objectives, structure

3. **Methods**
   - Research design, data collection, analysis methods, tools/technologies

4. **Results**
   - Objective findings presentation, no interpretation

5. **Discussion**
   - Findings interpretation, comparison with literature, limitations, implications

6. **Conclusion**
   - Summary, significance, future directions

## Features

### Project Management
- Create new writing projects
- List all projects
- View project details
- Delete projects

### Section Generation
- Select section type from 6 options
- Enter key points for the section
- Select relevant papers for citations
- Generate content with AI
- Edit generated content
- Save sections

### Literature Integration
- Search papers from multiple sources
- Select papers to cite
- Auto-insert citations in generated content
- Track citations used

### Word Count Tracking
- Real-time word count per section
- Display on save
- Track overall project progress

## Installation Steps

1. Install dependencies:
   ```bash
   cd client
   npm install @radix-ui/react-tabs

   cd server
   pip install arxiv biopython requests
   ```

2. Update database:
   ```sql
   -- Run in Supabase SQL editor
   -- Tables are in server/database_schema.sql
   ```

3. Start servers:
   ```bash
   # Backend
   cd server
   uvicorn main:app --reload

   # Frontend
   cd client
   npm run dev
   ```

4. Access the feature:
   - Navigate to `/ai-writer` or
   - Click "AI Writer" on home page

## Academic Writing Prompts

Each section type has a specialized prompt:
- Enforces academic tone
- Specifies content requirements
- Provides context about citations
- Guides GPT-4 structure

## Citation Integration

- Papers are fetched from Literature Search API
- Users can select relevant papers
- GPT-4 is instructed to use selected papers
- Citations are extracted and tracked
- Format: `[Author, Year]` style

## Future Enhancements

- Export to LaTeX/Word
- Version history
- Collaborative editing
- Custom citation styles
- Plagiarism checker integration
- AI-powered suggestions
- Document templates
