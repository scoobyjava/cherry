import time
import psycopg2
import numpy as np
from typing import List, Dict, Any
from utils.metrics import BenchmarkResult


class PostgresRunner:
    """Runs benchmarks for PostgreSQL with vector extensions"""
    
    def __init__(self, config):
        self.config = config
        self.table_name = "benchmark_vectors"
        
        # Connect to PostgreSQL
        self.connection = psycopg2.connect(
            host=config["host"],
            port=config["port"],
            dbname=config["database"],
            user=config["user"],
            password=config["password"]
        )
        self.cursor = self.connection.cursor()
        
        # Setup tables and extensions
        self._setup_database()
        
    def _setup_database(self):
        """Set up PostgreSQL database with vector extension"""
        commands = [
            # Create vector extension if it doesn't exist
            "CREATE EXTENSION IF NOT EXISTS vector;",
            
            # Drop table if exists
            f"DROP TABLE IF EXISTS {self.table_name};",
            
            # Create table with vector column
            f"""
            CREATE TABLE {self.table_name} (
                id TEXT PRIMARY KEY,
                embedding vector(384),
                source_type TEXT,
                timestamp BIGINT,
                relevance_score FLOAT,
                category TEXT,
                document_id TEXT,
                section_id TEXT,
                confidence FLOAT
            );
            """,
            
            # Create index on vector column
            f"CREATE INDEX ON {self.table_name} USING ivfflat (embedding vector_cosine_ops);",
            
            # Create indexes on metadata fields
            f"CREATE INDEX ON {self.table_name} (category);",
            f"CREATE INDEX ON {self.table_name} (source_type);",
            f"CREATE INDEX ON {self.table_name} (relevance_score);"
        ]
        
        for command in commands:
            self.cursor.execute(command)
        
        self.connection.commit()
        
    def insert_vectors(self, dataset: List[Dict[str, Any]]) -> float:
        """Insert vectors into PostgreSQL and return time taken"""
        start_time = time.time()
        
        for item in dataset:
            vector_str = str(item["vector"]).replace('[', '{').replace(']', '}')
            metadata = item["metadata"]
            
            self.cursor.execute(
                f"""
                INSERT INTO {self.table_name} 
                (id, embedding, source_type, timestamp, relevance_score, category, 
                document_id, section_id, confidence)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    item["id"],
                    vector_str,
                    metadata["source_type"],
                    metadata["timestamp"],
                    metadata["relevance_score"],
                    metadata["category"],
                    metadata["document_id"],
                    metadata["section_id"],
                    metadata["confidence"]
                )
            )
        
        self.connection.commit()
        return time.time() - start_time
        
    def benchmark_search(self, query_vectors: List[np.ndarray], top_k=5) -> Dict:
        """Benchmark simple vector search"""
        result = BenchmarkResult(
            test_name="simple_search",
            system_name="postgres",
            dataset_size=self._get_vector_count()
        )
        
        for vector in query_vectors:
            vector_str = str(vector.tolist()).replace('[', '{').replace(']', '}')
            
            start_time = time.time()
            self.cursor.execute(
                f"""
                SELECT id, 1 - (embedding <=> %s) AS similarity
                FROM {self.table_name}
                ORDER BY embedding <=> %s
                LIMIT %s
                """,
                (vector_str, vector_str, top_k)
            )
            self.cursor.fetchall()  # Fetch results to complete the operation
            latency = time.time() - start_time
            result.latencies.append(latency)
            
        return result.to_dict()
        
    def benchmark_filtered_search(self, query_vectors: List[np.ndarray], top_k=5) -> Dict:
        """Benchmark filtered vector search"""
        result = BenchmarkResult(
            test_name="filtered_search",
            system_name="postgres",
            dataset_size=self._get_vector_count()
        )
        
        # Cycle through different filter types
        filter_types = [
            ("category = %s", "technology"),
            ("source_type = %s", "web"),
            ("relevance_score >= %s", 0.5)
        ]
        
        for i, vector in enumerate(query_vectors):
            filter_clause, filter_value = filter_types[i % len(filter_types)]
            vector_str = str(vector.tolist()).replace('[', '{').replace(']', '}')
            
            start_time = time.time()
            self.cursor.execute(
                f"""
                SELECT id, 1 - (embedding <=> %s) AS similarity
                FROM {self.table_name}
                WHERE {filter_clause}
                ORDER BY embedding <=> %s
                LIMIT %s
                """,
                (vector_str, filter_value, vector_str, top_k)
            )
            self.cursor.fetchall()  # Fetch results to complete the operation
            latency = time.time() - start_time
            result.latencies.append(latency)
            
        return result.to_dict()
        
    def _get_vector_count(self) -> int:
        """Get the count of vectors in the table"""
        self.cursor.execute(f"SELECT COUNT(*) FROM {self.table_name}")
        return self.cursor.fetchone()[0]
        
    def cleanup(self):
        """Clean up resources after benchmarking"""
        try:
            # Drop the table
            self.cursor.execute(f"DROP TABLE IF EXISTS {self.table_name}")
            self.connection.commit()
            print(f"Cleaned up PostgreSQL table '{self.table_name}'")
        except Exception as e:
            print(f"Error cleaning up PostgreSQL: {str(e)}")
        finally:
            # Close connections
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
