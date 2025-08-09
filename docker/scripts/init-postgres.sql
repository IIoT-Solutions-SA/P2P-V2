-- PostgreSQL initialization script for P2P Sandbox
-- This script is executed when the PostgreSQL container starts for the first time

-- Create the main application database (if not exists)
CREATE DATABASE p2p_sandbox;

-- Create the SuperTokens database (if not exists)  
CREATE DATABASE supertokens;

-- Set default permissions (optional)
-- Additional setup can be added here as needed
EOF < /dev/null
