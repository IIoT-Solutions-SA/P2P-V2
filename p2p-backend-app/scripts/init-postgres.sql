-- Create SuperTokens database
CREATE DATABASE supertokens;

-- Create extensions in main database
\c p2p_sandbox;

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Add any other PostgreSQL extensions we might need
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For text search
CREATE EXTENSION IF NOT EXISTS "btree_gin"; -- For better indexing

-- Create a simple version tracking table
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

-- Insert initial version
INSERT INTO schema_version (version, description) 
VALUES (1, 'Initial database setup') 
ON CONFLICT (version) DO NOTHING;