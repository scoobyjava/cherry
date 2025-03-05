
-- Enable the pgvector extension
CREATE EXTENSION IF NOT EXISTS pgvector;

-- Create the memories table
CREATE TABLE IF NOT EXISTS memories (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536) NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create an index on the embedding column for faster similarity searches
CREATE INDEX IF NOT EXISTS memories_embedding_idx ON memories USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Create an index on agent_id for faster lookups
CREATE INDEX IF NOT EXISTS memories_agent_id_idx ON memories(agent_id);

-- Comment: You may need to adjust the number of lists in the vector index based on your data size
-- Typically, sqrt(number_of_rows) is a good starting point for lists
