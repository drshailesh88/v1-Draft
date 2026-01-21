-- Core Database Schema for V1 Draft
-- PostgreSQL + pgvector (Supabase)

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    subscription_tier VARCHAR(50) DEFAULT 'free',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Documents table (for Chat with PDF)
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500),
    filename VARCHAR(255) NOT NULL,
    storage_key VARCHAR(500),
    total_pages INT,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) DEFAULT 'uploading'
);

-- Document chunks (for vector search)
CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INT NOT NULL,
    content TEXT NOT NULL,
    page_number INT,
    embedding vector(1536)
);

-- Chats table
CREATE TABLE IF NOT EXISTS chats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    document_id UUID REFERENCES documents(id) ON DELETE SET NULL,
    title VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Messages table
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_id UUID REFERENCES chats(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Literature searches table
CREATE TABLE IF NOT EXISTS literature_searches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    query TEXT NOT NULL,
    sources JSONB,
    results JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Saved papers table
CREATE TABLE IF NOT EXISTS saved_papers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500),
    authors JSONB,
    year VARCHAR(10),
    journal VARCHAR(255),
    doi VARCHAR(255),
    abstract TEXT,
    source VARCHAR(50),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Citations table
CREATE TABLE IF NOT EXISTS citations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    metadata JSONB NOT NULL,
    style VARCHAR(50),
    formatted TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Data extractions table
CREATE TABLE IF NOT EXISTS data_extractions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    extraction_type VARCHAR(50),
    data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- AI detections table
CREATE TABLE IF NOT EXISTS ai_detections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    text TEXT,
    ai_probability FLOAT,
    human_probability FLOAT,
    verdict VARCHAR(50),
    confidence FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Research topics table
CREATE TABLE IF NOT EXISTS research_topics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    research_field VARCHAR(255) NOT NULL,
    topic_name VARCHAR(500) NOT NULL,
    description TEXT,
    relevance_score FLOAT,
    gap_analysis TEXT,
    trending_score FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Paraphrases table
CREATE TABLE IF NOT EXISTS paraphrases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    original_text TEXT NOT NULL,
    paraphrased_text TEXT NOT NULL,
    intensity VARCHAR(20) NOT NULL,
    vocabulary_enhancements JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- AI writer projects table
CREATE TABLE IF NOT EXISTS ai_writer_projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    topic TEXT NOT NULL,
    research_questions TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- AI writer sections table
CREATE TABLE IF NOT EXISTS ai_writer_sections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES ai_writer_projects(id) ON DELETE CASCADE,
    section_type VARCHAR(50) NOT NULL CHECK (section_type IN ('abstract', 'introduction', 'methods', 'results', 'discussion', 'conclusion')),
    content TEXT,
    word_count INT,
    citations_used JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Systematic reviews table
CREATE TABLE IF NOT EXISTS systematic_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    research_question TEXT NOT NULL,
    databases JSONB NOT NULL,
    search_terms TEXT NOT NULL,
    inclusion_criteria TEXT NOT NULL,
    exclusion_criteria TEXT NOT NULL,
    screening_counts JSONB DEFAULT '{"identification": 0, "screening": 0, "eligibility": 0, "included": 0, "excluded": 0}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Screening records table
CREATE TABLE IF NOT EXISTS screening_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    review_id UUID REFERENCES systematic_reviews(id) ON DELETE CASCADE,
    paper_id VARCHAR(255) NOT NULL,
    title TEXT NOT NULL,
    authors JSONB,
    year VARCHAR(10),
    doi VARCHAR(255),
    status VARCHAR(20) NOT NULL CHECK (status IN ('included', 'excluded', 'pending')),
    reason TEXT,
    stage VARCHAR(50) NOT NULL CHECK (stage IN ('identification', 'screening', 'eligibility')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Citation boosts table
CREATE TABLE IF NOT EXISTS citation_boosts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    original_text TEXT NOT NULL,
    gap_analysis TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Boosted citations table
CREATE TABLE IF NOT EXISTS boosted_citations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    boost_id UUID REFERENCES citation_boosts(id) ON DELETE CASCADE,
    paper_id VARCHAR(500) NOT NULL,
    position_in_text INT,
    relevance_score FLOAT,
    paper_metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Deep reviews table
CREATE TABLE IF NOT EXISTS deep_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    paper_title VARCHAR(500) NOT NULL,
    paper_content TEXT,
    comparison_papers JSONB,
    overall_rating JSONB,
    methods_critique TEXT,
    results_critique TEXT,
    discussion_critique TEXT,
    suggestions TEXT,
    similarity_analysis JSONB,
    agent_tasks JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Subscriptions table
CREATE TABLE IF NOT EXISTS subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tier VARCHAR(50) NOT NULL CHECK (tier IN ('free', 'pro', 'team')),
    payment_method VARCHAR(50) NOT NULL CHECK (payment_method IN ('none', 'paddle', 'razorpay')),
    currency VARCHAR(10) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) NOT NULL CHECK (status IN ('active', 'cancelled', 'past_due')),
    paddle_customer_id VARCHAR(255),
    paddle_subscription_id VARCHAR(255),
    razorpay_subscription_id VARCHAR(255),
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    ends_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Transactions table
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subscription_id UUID REFERENCES subscriptions(id) ON DELETE CASCADE,
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(10) NOT NULL,
    status VARCHAR(50) NOT NULL CHECK (status IN ('pending', 'completed', 'failed', 'refunded')),
    payment_method VARCHAR(50) NOT NULL CHECK (payment_method IN ('paddle', 'razorpay')),
    paddle_transaction_id VARCHAR(255),
    razorpay_order_id VARCHAR(255),
    razorpay_payment_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB
);

-- Create indexes for vector search
CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding ON document_chunks
USING ivfflat (embedding vector_cosine_ops);

-- Create other indexes
CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id ON document_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_chats_user_id ON chats(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_chat_id ON messages(chat_id);
CREATE INDEX IF NOT EXISTS idx_literature_searches_user_id ON literature_searches(user_id);
CREATE INDEX IF NOT EXISTS idx_saved_papers_user_id ON saved_papers(user_id);
CREATE INDEX IF NOT EXISTS idx_citations_user_id ON citations(user_id);
CREATE INDEX IF NOT EXISTS idx_data_extractions_user_id ON data_extractions(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_detections_user_id ON ai_detections(user_id);
CREATE INDEX IF NOT EXISTS idx_research_topics_user_id ON research_topics(user_id);
CREATE INDEX IF NOT EXISTS idx_paraphrases_user_id ON paraphrases(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_writer_projects_user_id ON ai_writer_projects(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_writer_sections_project_id ON ai_writer_sections(project_id);
CREATE INDEX IF NOT EXISTS idx_systematic_reviews_user_id ON systematic_reviews(user_id);
CREATE INDEX IF NOT EXISTS idx_screening_records_review_id ON screening_records(review_id);
CREATE INDEX IF NOT EXISTS idx_citation_boosts_user_id ON citation_boosts(user_id);
CREATE INDEX IF NOT EXISTS idx_boosted_citations_boost_id ON boosted_citations(boost_id);
CREATE INDEX IF NOT EXISTS idx_deep_reviews_user_id ON deep_reviews(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_subscriptions_paddle_subscription_id ON subscriptions(paddle_subscription_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_razorpay_subscription_id ON subscriptions(razorpay_subscription_id);
CREATE INDEX IF NOT EXISTS idx_transactions_subscription_id ON transactions(subscription_id);
CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);
CREATE INDEX IF NOT EXISTS idx_transactions_paddle_transaction_id ON transactions(paddle_transaction_id);
CREATE INDEX IF NOT EXISTS idx_transactions_razorpay_order_id ON transactions(razorpay_order_id);
