-- Initial database setup script
-- This runs automatically when PostgreSQL container starts

-- Create database if it doesn't exist (already done by POSTGRES_DB env var)
-- Just ensure we're using the correct database
\c vietcms_moderation;

-- Create extension for UUID support (if needed in future)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Set timezone
SET timezone = 'UTC';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE vietcms_moderation TO vietcms;

