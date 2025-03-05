CREATE TABLE IF NOT EXISTS ui_ux_memories (
    id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(50),
    tags JSONB,
    recommendations JSONB,
    wireframes JSONB,
    design_principles TEXT[],
    accessibility_score FLOAT,
    user_feedback JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    embedding_id VARCHAR(36),
    metadata JSONB
);

-- Index for faster searches
CREATE INDEX IF NOT EXISTS idx_ui_ux_memories_category ON ui_ux_memories(category);
CREATE INDEX IF NOT EXISTS idx_ui_ux_memories_embedding_id ON ui_ux_memories(embedding_id);
CREATE INDEX IF NOT EXISTS idx_ui_ux_memories_tags ON ui_ux_memories USING GIN (tags);
