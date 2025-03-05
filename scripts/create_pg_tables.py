#!/usr/bin/env python3

import os
import sys
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config_loader import load_config
from services.pg_service import PostgresService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_tables(config_path: str):
    """Create necessary tables in PostgreSQL if they don't exist"""
    try:
        # Load config
        config = load_config(config_path)
        pg_service = PostgresService(config["postgres"])
        
        # Create tables
        logger.info("Creating necessary tables in PostgreSQL...")
        
        # Create memory_entries table
        pg_service.execute_query("""
            CREATE TABLE IF NOT EXISTS memory_entries (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                namespace VARCHAR(50) NOT NULL,
                metadata JSONB DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_memory_namespace ON memory_entries(namespace);
            CREATE INDEX IF NOT EXISTS idx_memory_updated ON memory_entries(updated_at);
        """)
        
        # Create embedded_entries tracking table
        pg_service.execute_query("""
            CREATE TABLE IF NOT EXISTS embedded_entries (
                entry_id INTEGER REFERENCES memory_entries(id) ON DELETE CASCADE,
                namespace VARCHAR(50) NOT NULL,
                embedded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (entry_id, namespace)
            );
            
            CREATE INDEX IF NOT EXISTS idx_embedded_namespace ON embedded_entries(namespace);
        """)
        
        # Create sync_log table to track sync jobs
        pg_service.execute_query("""
            CREATE TABLE IF NOT EXISTS sync_log (
                id SERIAL PRIMARY KEY,
                namespace VARCHAR(50) NOT NULL,
                entries_checked INTEGER DEFAULT 0,
                entries_embedded INTEGER DEFAULT 0,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                status VARCHAR(20) DEFAULT 'running'
            );
        """)
        
        logger.info("Tables created successfully")
        
    except Exception as e:
        logger.error(f"Error creating tables: {str(e)}")
        raise

if __name__ == "__main__":
    create_tables("/workspaces/cherry/benchmarks/benchmark_config.json")
