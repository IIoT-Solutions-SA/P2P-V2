// MongoDB initialization script for P2P Sandbox
// This script is executed when the MongoDB container starts for the first time

// Switch to the application database
db = db.getSiblingDB('p2p_sandbox');

// Create a simple collection to ensure database exists
db.init.insertOne({initialized: true, created_at: new Date()});

// Create indexes that will be needed
db.use_cases.createIndex({ "title": "text", "description": "text" });
db.use_cases.createIndex({ "created_at": -1 });
db.use_cases.createIndex({ "organization_id": 1 });

print('MongoDB initialization completed for p2p_sandbox database');
EOF < /dev/null
