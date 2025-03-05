
import time
import os
import numpy as np
import psutil
import matplotlib.pyplot as plt
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pgvector.sqlalchemy import Vector
import pinecone
import logging
import argparse
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("VectorDBBenchmark")

# Constants
VECTOR_DIMENSIONS = 128
DEFAULT_TEST_SIZES = [1000, 10000, 100000]  # Number of vectors to test with
NUM_QUERIES = 100  # Number of queries to run for each test size
TOP_K = 10  # Number of results to return for each query

# PostgreSQL model setup
Base = declarative_base()

class VectorEntry(Base):
    __tablename__ = 'vector_entries'
    
    id = Column(Integer, primary_key=True)
    text = Column(Text)
    embedding = Column(Vector(VECTOR_DIMENSIONS))

class Benchmark:
    def __init__(self, pg_connection_string, pinecone_api_key, pinecone_env):
        self.pg_connection_string = pg_connection_string
        self.pinecone_api_key = pinecone_api_key
        self.pinecone_env = pinecone_env
        self.pg_engine = None
        self.pg_session = None
        self.pinecone_index = None
        self.results = []
        
    def setup_postgresql(self):
        """Setup PostgreSQL with pgvector extension"""
        logger.info("Setting up PostgreSQL...")
        self.pg_engine = create_engine(self.pg_connection_string)
        
        # Create session
        Session = sessionmaker(bind=self.pg_engine)
        self.pg_session = Session()
        
        # Ensure pgvector extension is installed
        with self.pg_engine.connect() as conn:
            conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            conn.commit()
        
        # Create tables
        Base.metadata.create_all(self.pg_engine)
        
        logger.info("PostgreSQL setup complete.")
        
    def setup_pinecone(self):
        """Setup Pinecone index"""
        logger.info("Setting up Pinecone...")
        pinecone.init(api_key=self.pinecone_api_key, environment=self.pinecone_env)
        
        index_name = "benchmark-test"
        
        # Check if index exists, if not create it
        if index_name not in pinecone.list_indexes():
            pinecone.create_index(
                name=index_name,
                dimension=VECTOR_DIMENSIONS,
                metric="cosine"
            )
        
        self.pinecone_index = pinecone.Index(index_name)
        logger.info("Pinecone setup complete.")
        
    def generate_data(self, size):
        """Generate random vectors and text data"""
        logger.info(f"Generating {size} random vectors...")
        
        vectors = np.random.rand(size, VECTOR_DIMENSIONS).astype(np.float32)
        # Normalize vectors for cosine similarity
        vectors = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
        
        # Generate some dummy text data
        texts = [f"Document {i}" for i in range(size)]
        
        return vectors, texts
    
    def insert_to_postgresql(self, vectors, texts):
        """Insert vectors to PostgreSQL"""
        logger.info(f"Inserting {len(vectors)} vectors to PostgreSQL...")
        
        start_time = time.time()
        start_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024  # MB
        
        # Clear existing data
        self.pg_session.query(VectorEntry).delete()
        self.pg_session.commit()
        
        # Insert data in batches
        batch_size = 1000
        for i in range(0, len(vectors), batch_size):
            batch_vectors = vectors[i:i+batch_size]
            batch_texts = texts[i:i+batch_size]
            
            entries = []
            for j, (vector, text) in enumerate(zip(batch_vectors, batch_texts)):
                entries.append(VectorEntry(
                    text=text,
                    embedding=vector.tolist()
                ))
            
            self.pg_session.bulk_save_objects(entries)
            self.pg_session.commit()
            
        end_time = time.time()
        end_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024  # MB
        
        duration = end_time - start_time
        memory_used = end_memory - start_memory
        
        logger.info(f"PostgreSQL insertion completed in {duration:.2f} seconds, using {memory_used:.2f} MB")
        return {"duration": duration, "memory_used": memory_used}
    
    def insert_to_pinecone(self, vectors, texts):
        """Insert vectors to Pinecone"""
        logger.info(f"Inserting {len(vectors)} vectors to Pinecone...")
        
        start_time = time.time()
        start_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024  # MB
        
        # Delete existing vectors
        self.pinecone_index.delete(deleteAll=True)
        
        # Insert data in batches
        batch_size = 100  # Pinecone recommends smaller batch sizes
        for i in range(0, len(vectors), batch_size):
            batch_vectors = vectors[i:i+batch_size]
            batch_texts = texts[i:i+batch_size]
            
            items = []
            for j, (vector, text) in enumerate(zip(batch_vectors, batch_texts)):
                item_id = str(i + j)
                items.append((item_id, vector.tolist(), {"text": text}))
            
            self.pinecone_index.upsert(items)
            
        end_time = time.time()
        end_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024  # MB
        
        duration = end_time - start_time
        memory_used = end_memory - start_memory
        
        logger.info(f"Pinecone insertion completed in {duration:.2f} seconds, using {memory_used:.2f} MB")
        return {"duration": duration, "memory_used": memory_used}
    
    def query_postgresql(self, query_vectors):
        """Query vectors in PostgreSQL"""
        logger.info(f"Querying {len(query_vectors)} vectors in PostgreSQL...")
        
        start_time = time.time()
        start_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024  # MB
        
        query_times = []
        
        for query_vector in query_vectors:
            query_start = time.time()
            
            # Using cosine similarity
            results = self.pg_session.execute(
                f"""
                SELECT id, text, 1 - (embedding <=> :query_embedding) as similarity
                FROM vector_entries
                ORDER BY embedding <=> :query_embedding
                LIMIT {TOP_K}
                """,
                {"query_embedding": query_vector.tolist()}
            ).fetchall()
            
            query_times.append(time.time() - query_start)
        
        end_time = time.time()
        end_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024  # MB
        
        duration = end_time - start_time
        avg_query_time = sum(query_times) / len(query_times)
        memory_used = end_memory - start_memory
        
        logger.info(f"PostgreSQL queries completed in {duration:.2f} seconds (avg: {avg_query_time:.4f}s), using {memory_used:.2f} MB")
        return {"duration": duration, "avg_query_time": avg_query_time, "memory_used": memory_used}
    
    def query_pinecone(self, query_vectors):
        """Query vectors in Pinecone"""
        logger.info(f"Querying {len(query_vectors)} vectors in Pinecone...")
        
        start_time = time.time()
        start_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024  # MB
        
        query_times = []
        
        for query_vector in query_vectors:
            query_start = time.time()
            
            results = self.pinecone_index.query(
                vector=query_vector.tolist(),
                top_k=TOP_K,
                include_metadata=True
            )
            
            query_times.append(time.time() - query_start)
        
        end_time = time.time()
        end_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024  # MB
        
        duration = end_time - start_time
        avg_query_time = sum(query_times) / len(query_times)
        memory_used = end_memory - start_memory
        
        logger.info(f"Pinecone queries completed in {duration:.2f} seconds (avg: {avg_query_time:.4f}s), using {memory_used:.2f} MB")
        return {"duration": duration, "avg_query_time": avg_query_time, "memory_used": memory_used}
    
    def run_benchmark(self, test_sizes=None):
        """Run benchmark tests for different data sizes"""
        if test_sizes is None:
            test_sizes = DEFAULT_TEST_SIZES
            
        # Create output directory for results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = f"benchmark_results_{timestamp}"
        os.makedirs(results_dir, exist_ok=True)
        
        for size in test_sizes:
            logger.info(f"Running benchmark with {size} vectors")
            
            # Generate data
            vectors, texts = self.generate_data(size)
            
            # Insert to databases
            pg_insert_metrics = self.insert_to_postgresql(vectors, texts)
            pinecone_insert_metrics = self.insert_to_pinecone(vectors, texts)
            
            # Generate query vectors
            query_vectors = np.random.rand(NUM_QUERIES, VECTOR_DIMENSIONS).astype(np.float32)
            query_vectors = query_vectors / np.linalg.norm(query_vectors, axis=1, keepdims=True)
            
            # Query databases
            pg_query_metrics = self.query_postgresql(query_vectors)
            pinecone_query_metrics = self.query_pinecone(query_vectors)
            
            # Save results
            self.results.append({
                "size": size,
                "postgresql_insert_time": pg_insert_metrics["duration"],
                "postgresql_insert_memory": pg_insert_metrics["memory_used"],
                "postgresql_query_time": pg_query_metrics["duration"],