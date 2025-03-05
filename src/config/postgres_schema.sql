-- Enable pgvector extension if not already enabled
CREATE EXTENSION IF NOT EXISTS vector;

-- Search vectors table
CREATE TABLE IF NOT EXISTS search_vectors (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536) NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Recommendation vectors table
CREATE TABLE IF NOT EXISTS recommendation_vectors (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536) NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- QA vectors table
CREATE TABLE IF NOT EXISTS qa_vectors (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536) NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indices for vector similarity search
CREATE INDEX IF NOT EXISTS search_vectors_embedding_idx ON search_vectors USING ivfflat (embedding vector_l2_ops);
CREATE INDEX IF NOT EXISTS recommendation_vectors_embedding_idx ON recommendation_vectors USING ivfflat (embedding vector_l2_ops);
CREATE INDEX IF NOT EXISTS qa_vectors_embedding_idx ON qa_vectors USING ivfflat (embedding vector_l2_ops);

-- Create indices for common metadata fields
CREATE INDEX IF NOT EXISTS search_vectors_source_idx ON search_vectors USING GIN ((metadata -> 'source_type'));
CREATE INDEX IF NOT EXISTS search_vectors_category_idx ON search_vectors USING GIN ((metadata -> 'category'));
CREATE INDEX IF NOT EXISTS recommendation_vectors_user_idx ON recommendation_vectors USING GIN ((metadata -> 'user_id'));
CREATE INDEX IF NOT EXISTS recommendation_vectors_item_idx ON recommendation_vectors USING GIN ((metadata -> 'item_id'));
CREATE INDEX IF NOT EXISTS qa_vectors_document_idx ON qa_vectors USING GIN ((metadata -> 'document_id'));
