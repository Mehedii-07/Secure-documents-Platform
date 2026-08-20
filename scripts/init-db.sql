-- ============================================================
-- init-db.sql — Postgres initialization
-- Runs ONCE when the container is first created.
-- Creates the pgvector extension required for embeddings.
-- ============================================================

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pg_trgm for full-text search (used alongside vector search)
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Enable btree_gin for composite indexes
CREATE EXTENSION IF NOT EXISTS btree_gin;
