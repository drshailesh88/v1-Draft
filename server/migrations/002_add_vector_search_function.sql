-- Vector Search Function for Chat with PDF Feature
-- This function performs similarity search on document chunks using pgvector

CREATE OR REPLACE FUNCTION match_document_chunks(
    query_embedding vector(1536),
    match_document_id UUID,
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 5
)
RETURNS TABLE (
    id UUID,
    document_id UUID,
    chunk_index INT,
    content TEXT,
    page_number INT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        dc.id,
        dc.document_id,
        dc.chunk_index,
        dc.content,
        dc.page_number,
        1 - (dc.embedding <=> query_embedding) as similarity
    FROM document_chunks dc
    WHERE dc.document_id = match_document_id
      AND (dc.embedding <=> query_embedding) < (1 - match_threshold)
    ORDER BY dc.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Add comment for documentation
COMMENT ON FUNCTION match_document_chunks IS 'Performs vector similarity search on document chunks for RAG chat functionality';