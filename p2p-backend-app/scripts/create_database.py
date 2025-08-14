import asyncio
import asyncpg
import os
import time

# A simple retry loop to handle database startup timing
max_retries = 10
retry_delay = 3 # seconds

for attempt in range(max_retries):
    try:
        print(f"Attempt {attempt + 1}/{max_retries}: Connecting to PostgreSQL...")
        
        # Use environment variables for connection details
        conn = asyncio.run(asyncpg.connect(
            user=os.environ.get('POSTGRES_USER'),
            password=os.environ.get('POSTGRES_PASSWORD'),
            database='postgres',
            host='postgres' # <-- This is the critical fix: use the service name
        ))

        print("✅ Successfully connected to PostgreSQL.")
        
        exists = asyncio.run(conn.fetchval("SELECT 1 FROM pg_database WHERE datname = 'supertokens'"))

        if not exists:
            print("Database 'supertokens' does not exist. Creating it now...")
            asyncio.run(conn.execute('CREATE DATABASE supertokens'))
            print("✅ Database 'supertokens' created successfully.")
        else:
            print("✅ Database 'supertokens' already exists.")
            
        asyncio.run(conn.close())
        break # Exit the loop on success

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        if attempt < max_retries - 1:
            print(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
        else:
            print("❌ Max retries reached. Could not connect to the database.")
            exit(1) # Exit with an error code