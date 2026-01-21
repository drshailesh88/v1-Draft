# Database Migration Instructions

## Migrations

### Migration 002: Vector Search Function

**File**: `migrations/002_add_vector_search_function.sql`

**Description**: Adds the `match_document_chunks` function to Supabase for vector similarity search in Chat with PDF feature.

**How to Apply**:

1. Go to your Supabase project: https://supabase.com/dashboard/project/qmtilfljwlixgcucwprs
2. Navigate to SQL Editor
3. Copy the contents of `server/migrations/002_add_vector_search_function.sql`
4. Paste and run the SQL

**What this does**:
- Creates a PostgreSQL function `match_document_chunks()` that performs vector similarity search
- Uses cosine similarity to find relevant document chunks for RAG chat
- Parameters:
  - `query_embedding`: The vector to search for (1536 dimensions)
  - `match_document_id`: Only search within a specific document
  - `match_threshold`: Minimum similarity score (default: 0.7)
  - `match_count`: Number of results to return (default: 5)

**Returns**:
- Table of matching chunks with id, document_id, chunk_index, content, page_number, and similarity score

**After applying this migration**:
The Chat with PDF feature will be able to retrieve relevant document chunks based on user queries.