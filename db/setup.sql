-- Create the database with UTF8 encoding
CREATE DATABASE cherry_db WITH ENCODING 'UTF8';

-- Connect to the database
\c cherry_db

-- Enable the pgvector extension
CREATE EXTENSION IF NOT EXISTS pgvector;
